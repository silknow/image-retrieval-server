SILKNOW Image Retrieval API Server
===============================

Overview
--------

HTTP server used for the Image Retrieval on ADASilk.

Installation / Usage
--------------------

To install,  use:

    pip install -r requirements.txt

To run, use:

    python server.py

Deployment with Docker
--------------------

To build the image, use:

    docker build -t silknow/image-retrieval-server .

To run, use:

    docker run -d --name silknow_image_retrieval_server -p 4995:5000 -v $(pwd)/samples:/usr/src/app/samples -v $(pwd)/output_files:/usr/src/app/output_files silknow/image-retrieval-server
