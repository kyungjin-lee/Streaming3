
obj_model_def = "ObjectDetector/config/yolov3.cfg"
obj_weights_path = "ObjectDetector/weights/yolov3.weights"
obj_class_path = "ObjectDetector/data/coco.names"
obj_img_size = 416


class ObjDetectorInfo:
    def __init__(self):
       self.model_def = obj_model_def
       self.weights_path = obj_weights_path
       self.class_path = obj_class_path
       self.img_size = obj_img_size 

    def getInfo(self):
       return self

    def setInputSize(img_size):
        self.img_size = img_size



