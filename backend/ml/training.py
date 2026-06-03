import pathlib

import albumentations as A
from ultralytics import YOLO
#model = YOLO('yolo26n-seg.pt')
model = YOLO('yolo26n-seg.pt')

custom_transforms = []
#data="dataset.yaml"
results = model.train(data=str(pathlib.Path(__file__).parent / "dataset.yaml"), epochs= 100, imgsz=512, batch=16, device='cpu', cls=2.0,
                      degrees=15, perspective=0.0005, flipud=0.3, fliplr=0.5, hsv_v=0.4, hsv_s=0.3, hsv_h=0.01, mosaic=0.5,mixup=0.1, copy_paste=0.1, patience=20, name="baseline_v1")

valres = model.val(data=str(pathlib.Path(__file__).parent / "dataset.yaml"), imgsz = 512)

print("\n")
print("\n valres speed, ", valres.speed)
print("\n valres.seg.map50 ", valres.seg.map50)
print("\n valres.seg.map   ", valres.seg.map)
print("\n valres.seg.maps  ", valres.seg.maps)  # per-class mAP
#print("\n valres.box.prec_values, ", valres.box.prec_values)
#print("\n valres mean50, ", valres.box.map50)
#print("\n valres mean50-95, ", valres.box.map)
#print("valres mean50-95, ", valres.curves_results)