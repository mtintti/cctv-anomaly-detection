
import pathlib

import albumentations as A
import cv2
from sympy.printing.pretty.pretty_symbology import line_width
from ultralytics import YOLO

#model = YOLO('yolo26n-seg.pt')
#model = YOLO('C:/ohjelmointi/HobbyProjects/cctv-anomaly-detection/runs/segment/model_v8/weights/best.pt')

custom_transforms = []
#data="dataset.yaml" // str(pathlib.Path(__file__).parent / "dataset.yaml")
#results = model.train(data=str(pathlib.Path(__file__).parent / "dataset.yaml"), epochs= 80, imgsz=512, batch=32, cls=1.5,
#                      degrees=15, perspective=0.0005, flipud=0.3, fliplr=0.5, hsv_v=0.4, hsv_s=0.3, hsv_h=0.01, mosaic=0.5,mixup=0.1, copy_paste=0.1, lr0=0.001, lrf=0.00001, cos_lr=True, conf=0.20, patience=40, name="model_v9") # old ones, lr0=0.01, lrf=0.01, batch=16

model = YOLO('C:/ohjelmointi/HobbyProjects/cctv-anomaly-detection/runs/segment/model_v9/weights/best.pt')
model.export(format="onnx", dynamic=True, batch=10)

pred = model.predict('https://weathercam.digitraffic.fi/C0165000.jpg', conf=0.10) #prev good example, C:\ohjelmointi\HobbyProjects\cctv-training\images\train/C0150409_tie-2-karkkila.jpg,  second
for i in pred:
    i.show()
    print(i.verbose())
    i.plot()
    print(i.to_json())
    i.save("prediction.jpg", line_width=1)
'''valres = model.val(data=str(pathlib.Path(__file__).parent / "dataset.yaml"), imgsz = 512) 

print("\n")
print("\n valres speed, ", valres.speed)
print("\n valres.seg.map50 ", valres.seg.map50)
print("\n valres.seg.map   ", valres.seg.map)
print("\n valres.seg.maps  ", valres.seg.maps)  # per-class mAP
#print("\n valres.box.prec_values, ", valres.box.prec_values)
#print("\n valres mean50, ", valres.box.map50)
#print("\n valres mean50-95, ", valres.box.map)
#print("valres mean50-95, ", valres.curves_results)
'''

