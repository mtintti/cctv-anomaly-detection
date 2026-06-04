import pathlib
import cv2
import numpy as np
from ultralytics.data.augment import RandomPerspective

from backend.app import settings

imgdest_dir = settings.desktop


def image_specific_transforms(segann, names):
    id_to_name = {v: k for k, v in names.items()}
    annpath = pathlib.Path(segann)
    picpath = pathlib.Path(imgdest_dir)
    for txt_file in annpath.glob("*.txt"):
        with open(txt_file) as reader:
            for line in reader:
                line = line.strip()

                if not line:
                    continue

                class_id = int(line.split()[0])

                class_name = id_to_name[class_id]


               
                for pic_file in picpath.glob("*.jpg"):
                    #print("\n picfile, ",pic_file.name)
                    img_suffix = pic_file.suffix
                    txt_suffix = txt_file.suffix
                    if img_suffix in pic_file.name:
                        img_basename = pic_file.name.replace(img_suffix, '')
                        #print("imgbase ", img_basename)
                    if txt_suffix in txt_file.name:
                        txt_basename = txt_file.name.replace(txt_suffix, '')
                        #print("txtbase ", txt_basename)
                    if img_basename == txt_basename:
                        #print("imgbase ", img_basename, " txt_base ", txt_basename)
                        class_transforms(img_basename, txt_basename, class_id)
                        img = cv2.imread(str(pic_file))
                        polygons = load_yolo_segments(txt_file)
                        print("imgbase ", pic_file, " txt ", txt_file)

                        augmentations = [
                            ("rot10", lambda:
                            rotate_sample(
                                img,
                                polygons,
                                10
                            )),
                            ("rotm10", lambda:
                            rotate_sample(
                                img,
                                polygons,
                                -10
                            )),
                            ("persp08", lambda:
                            perspective_sample(
                                img,
                                polygons,
                                0.08
                            )),
                        ]

                        for suffix, aug_fn in augmentations:
                            img_aug, poly_aug = aug_fn()

                            new_base = (
                                f"{img_basename}_{suffix}"
                            )

                            cv2.imwrite(
                                str(picpath /
                                    f"{new_base}.jpg"),
                                img_aug
                            )

                            save_yolo_segments(
                                annpath /
                                f"{new_base}.txt",
                                poly_aug
                            )
                    #print("txt-file ", txt_file.name)

def class_transforms(img_basename,txt_basename,class_id):
    if class_id == 0 or class_id == 6:
        # degrees, translates, scales ja rotations more variance
        # print("\n image name in imgSpecif transforms ", )
        transform = RandomPerspective(degrees=10, translate=0.1, scale=0.1, shear=10)
    elif class_id == 2 or class_id == 4:
        # slight tilts, rotations on images,
        transform = RandomPerspective(degrees=5, translate=0.05, scale=0.05)
    elif class_id == 3:
        # asuming image is a pothole, varmaan shadow hommia?
        # degrees, translates, scales ja rotations more variance
        #print("imgbase ", img_basename, " txt_base ", txt_basename, " class_id ", class_id)
        transform = RandomPerspective(degrees=15, translate=0.15, scale=0.15)
        # transformed_mask = transform.apply_semantic()



def load_yolo_segments(txt_file):
    polygons = []

    with open(txt_file) as reader:
        for line in reader:

            line = line.strip()

            if not line:
                continue

            values = line.split()

            cls = int(values[0])

            coords = np.array(
                list(map(float, values[1:])),
                dtype=np.float32
            ).reshape(-1, 2)

            polygons.append((cls, coords))

    return polygons


def save_yolo_segments(outfile, polygons):

    with open(outfile, "w") as writer:

        for cls, pts in polygons:

            writer.write(str(cls))

            for x, y in pts:

                writer.write(
                    f" {x:.6f} {y:.6f}"
                )

            writer.write("\n")

import cv2
import numpy as np


def transform_polygons(polygons, M, width, height):

    transformed = []

    for cls, pts in polygons:

        pts_px = pts.copy()

        pts_px[:, 0] *= width
        pts_px[:, 1] *= height

        pts_h = np.hstack(
            [pts_px, np.ones((len(pts_px), 1))]
        )

        new_pts = (M @ pts_h.T).T

        new_pts[:, 0] /= width
        new_pts[:, 1] /= height

        new_pts = np.clip(
            new_pts,
            0,
            1
        )

        transformed.append(
            (cls, new_pts)
        )

    return transformed


def rotate_sample(
        image,
        polygons,
        angle):

    h, w = image.shape[:2]

    center = (
        w / 2,
        h / 2
    )

    M = cv2.getRotationMatrix2D(
        center,
        angle,
        1.0
    )

    img_aug = cv2.warpAffine(
        image,
        M,
        (w, h)
    )

    poly_aug = transform_polygons(
        polygons,
        M,
        w,
        h
    )

    return img_aug, poly_aug


def perspective_sample(
        image,
        polygons,
        strength=0.08):

    h, w = image.shape[:2]

    src = np.float32([
        [0, 0],
        [w, 0],
        [w, h],
        [0, h]
    ])

    dst = np.float32([
        [w*strength, h*strength],
        [w*(1-strength), 0],
        [w, h],
        [0, h*(1-strength)]
    ])

    H = cv2.getPerspectiveTransform(
        src,
        dst
    )

    img_aug = cv2.warpPerspective(
        image,
        H,
        (w, h)
    )

    transformed = []

    for cls, pts in polygons:

        pts_px = pts.copy()

        pts_px[:,0] *= w
        pts_px[:,1] *= h

        pts_px = pts_px.reshape(
            -1,
            1,
            2
        )

        warped = cv2.perspectiveTransform(
            pts_px,
            H
        )

        warped = warped.reshape(
            -1,
            2
        )

        warped[:,0] /= w
        warped[:,1] /= h

        warped = np.clip(
            warped,
            0,
            1
        )

        transformed.append(
            (cls, warped)
        )

    return img_aug, transformed