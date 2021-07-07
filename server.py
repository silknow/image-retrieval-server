from flask import Flask, request
from flask_cors import CORS
import os
import werkzeug
import ast
import csv
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_restx import Resource, Api
from werkzeug.middleware.proxy_fix import ProxyFix
import silknow_image_retrieval as sir

werkzeug.cached_property = werkzeug.utils.cached_property


VISUAL_MODEL_NAME = "visual_image_retrieval_v2"
SEMANTIC_MODEL_NAME = "visual_and_semantic_retrieval_v2"

model_visual = sir.preload_cnn_model(
    "./output_files/models/" + VISUAL_MODEL_NAME + "/"
)
model_semantic = sir.preload_cnn_model(
    "./output_files/models/" + SEMANTIC_MODEL_NAME + "/"
)
kd_tree_visual = sir.preload_kd_tree(
    "./output_files/trees/" + VISUAL_MODEL_NAME + "/"
)
kd_tree_semantic = sir.preload_kd_tree(
    "./output_files/trees/" + SEMANTIC_MODEL_NAME + "/"
)


def process(model_name, model, kd_tree):
    (
        tree,
        labels_tree,
        data_dict_train,
        relevant_variables,
        label2class_list,
    ) = kd_tree
    sir.get_kNN_from_preloaded_cnn_and_tree(
        tree,
        labels_tree,
        data_dict_train,
        relevant_variables,
        label2class_list,
        master_file_retrieval="master_file_retrieval.txt",
        master_dir_retrieval=r"./samples/",
        model=model,
        pred_gt_dir="./output_files/preds/" + model_name + "/",
        num_neighbors=20,
    )

    uris = list()
    with open("output_files/pred_gt_dir/kNN_LUT.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader, None)  # skip the headers
        for row in csv_reader:
            uris_fragments = ast.literal_eval(row[2])
            if uris_fragments:
                uris = list(
                    map(
                        lambda x: "http://data.silknow.org/object/" + x,
                        uris_fragments,
                    )
                )

    return uris


print("Starting web server...")
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
api = Api(app, doc="/doc")
cors = CORS(app)
ns = api.namespace("api", description="Image Retrieval API")


@ns.route("/status")
class status_route(Resource):
    def get(self):
        return "OK"


upload_parser = api.parser()
upload_parser.add_argument(
    "file", location="files", type=FileStorage, required=True
)


@ns.route("/retrieve", methods=["POST"])
@api.expect(upload_parser)
class retrieve_route(Resource):
    @ns.doc("retrieve_route")
    def post(self):
        # Save image
        f = request.files["file"]
        filepath = os.path.join("files", secure_filename(f.filename))
        Path(os.path.dirname(filepath)).mkdir(parents=True, exist_ok=True)
        f.save(filepath)

        # Add image to list of images to process
        with open(os.path.join("samples", "collection.txt"), "w") as f:
            f.write("#image\t#Label\n")
            f.write(os.path.join("..", filepath) + "\tImage\n")

        # Process image with Visual model
        visual_uris = process(
            model_name=VISUAL_MODEL_NAME,
            model=model_visual,
            kd_tree=kd_tree_visual,
        )
        semantic_uris = process(
            model_name=SEMANTIC_MODEL_NAME,
            model=model_semantic,
            kd_tree=kd_tree_semantic,
        )

        return {"visualUris": visual_uris, "semanticUris": semantic_uris}


@api.errorhandler
def default_error_handler(error):
    return {"error": str(error)}, getattr(error, "code", 500)


if __name__ == "__main__":
    app.run(debug=True)
