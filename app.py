import os
from flask import Flask, send_from_directory, request, Response
from flask_cors import CORS, cross_origin
import jsonpickle
import numpy as np
import cv2
import torch
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()
import base64
import io

# import some common libraries
import sys
import numpy as np
import os, json, random
from PIL import Image

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import Boxes, BoxMode
from centernet.config import add_centernet_config
from detic.config import add_detic_config
from detic.modeling.utils import reset_cls_test

def load_predictor():
    cfg = get_cfg()
    add_centernet_config(cfg)
    add_detic_config(cfg)
    cfg.merge_from_file("configs/Detic_LCOCOI21k_CLIP_SwinB_896b32_4x_ft4x_max-size.yaml")
    cfg.MODEL.WEIGHTS = 'https://dl.fbaipublicfiles.com/detic/Detic_LCOCOI21k_CLIP_SwinB_896b32_4x_ft4x_max-size.pth'
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
    cfg.MODEL.ROI_BOX_HEAD.ZEROSHOT_WEIGHT_PATH = 'rand'
    cfg.MODEL.ROI_HEADS.ONE_CLASS_PER_PROPOSAL = True # For better visualization purpose. Set to False for all classes.
    cfg.MODEL.DEVICE='cpu' # uncomment this to use cpu-only mode.
    predictor = DefaultPredictor(cfg)

    BUILDIN_CLASSIFIER = {
        'lvis': 'datasets/metadata/lvis_v1_clip_a+cname.npy',
        'objects365': 'datasets/metadata/o365_clip_a+cnamefix.npy',
        'openimages': 'datasets/metadata/oid_clip_a+cname.npy',
        'coco': 'datasets/metadata/coco_clip_a+cname.npy',
    }

    BUILDIN_METADATA_PATH = {
        'lvis': 'lvis_v1_val',
        'objects365': 'objects365_v2_val',
        'openimages': 'oid_val_expanded',
        'coco': 'coco_2017_val',
    }

    vocabulary = 'lvis' # change to 'lvis', 'objects365', 'openimages', or 'coco'
    metadata = MetadataCatalog.get(BUILDIN_METADATA_PATH[vocabulary])
    classifier = BUILDIN_CLASSIFIER[vocabulary]
    num_classes = len(metadata.thing_classes)
    reset_cls_test(predictor.model, classifier, num_classes)
    return predictor, metadata

predictor,metadata = load_predictor()
app = Flask(__name__, static_folder='build')
cors = CORS(app)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cross_origin()
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


# route http posts to this method
@app.route('/api/upload', methods=['POST'])
def upload():
    r = request
    # convert string of image data to uint8
    rstr = r.data.decode("utf-8").replace('data:image/png;base64,', '')
    base64_decoded = base64.b64decode(rstr)
    byio = io.BytesIO(base64_decoded)
    byio.seek(0)
    img = Image.open(byio)
    img = np.array(img)[...,:3]
    # build a response dict to send back to client
    response = predictor(img)
    response_dict = response['instances'].to("cpu").get_fields()
    boxes = response_dict['pred_boxes'].to("cpu")
    scores = response_dict['scores'].to("cpu")
    pred_classes = response_dict['pred_classes'].to("cpu")
    class_names = metadata.thing_classes
    croplist = []
    count = 1
    for box,score,pclass in zip(boxes, scores,pred_classes):
        box = BoxMode.convert(box.tolist(),BoxMode(0),BoxMode(1))
        score = score.item() * 100 
        cropsize = {'x':box[0],'y':box[1],'width':box[2], 'height':box[3]}
        cropdict = {}
        cropdict['name'] = str(count) + " - " + class_names[pclass] + "(" + str(score) + ")"
        count += 1
        cropdict['cropsize'] = cropsize
        croplist.append(cropdict)
    response = json.dumps(croplist)
    return Response(response=response, status=200, mimetype="application/json")


if __name__ == '__main__':
    app.run(use_reloader=True, port=5000, threaded=True)

