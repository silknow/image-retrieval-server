SILKNOW Image Retrieval API Server
===============================

Overview
--------

HTTP server used for the Image Retrieval on ADASilk.

Installation / Usage
--------------------

To install use:

    docker build -t silknow/image-retrieval-server .

To run, use:

    docker run --rm -d --name silknow_image_retrieval_api -p 4995:5000 -v $(pwd)/samples:/usr/src/app/samples -v $(pwd)/output_files:/usr/src/app/output_files silknow/image-retrieval-server
