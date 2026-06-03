
import datetime
import json
import pathlib
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import cv2
from ultralytics.models.sam import Predictor as sam
from backend.app import settings
from backend.ml.segmentation.datasetPreparation.img_transforms import image_specific_transforms

names = { "alligator crack" : 0, "block crack" : 1, "longitudinal crack" : 2, "pothole" : 3, "transverse crack" : 4, "repair" : 5, "other corruption" : 6, }
colors= { 0: [121, 212, 119], 1:[61, 128, 123], 2:[234, 184, 133], 3:[96, 112, 160], 4: [75, 40, 163], 5:[81,28,63], 6:[203, 118, 28] }
imgname = ""


def ml_backend():
    overrides = dict(conf=0.25, task="segment", imgsz=512, mode="predict", model="sam_b.pt")
    predictor = sam(overrides=overrides)
    #fileLoc(predictor)
    #image_specific_transforms(settings.segann, names)

    #id_to_name = {v: k for k, v in names.items()}
    #counts = count_yolo_classes(settings.segann)
    #histogram_from_yolo(counts, id_to_name)


#desktop ja -ann on mistä training images ja .json tiedot saadaan SAM bbox:iä ja img classTitle:ä varten
#outerfile, on mihin visuaalisoidut ja eri luokkatietojen segmentaatio mask's tallennetaan
desktop = pathlib.Path(settings.desktop)
desktop_ann = pathlib.Path(settings.desktop_ann)
outerfile = pathlib.Path(settings.outerfile)
classCount = Counter()

def fileLoc(predictor):
    print("\n getting files..")
    indx = 0
    print("\n specific files: ")
    for item in desktop.iterdir():
        if item.is_file():
            imgname = item.name
            '''try:
                if "India" in imgname:'''
            imgdir = item.__str__()
            img_suffix = str(item.suffix)
            #print("\n item name found, ", imgname)
            img_basename = imgname.replace(img_suffix, '')
            for ann_item in desktop_ann.iterdir():
                if ann_item.is_file():
                    ann_name = str(ann_item.name)
                    ann_suffix = str(ann_item.suffix)
                    ann_dir = ann_item.__str__()
                    if ann_suffix in ann_name:
                        ann = ann_name.replace(ann_suffix, '')
                        if ann == imgname:
                            #print("ann, ", ann, " imgbase, ", img_basename)
                            indx+= 1
                            with open(ann_dir, "r") as jsonfile:
                                data = json.load((jsonfile))
                                #print("\n data found, ", data)
                                objectindx = len(data["objects"])
                                invi_indx = 0
                                while objectindx > 0:
                                    classtitle = data["objects"][invi_indx]["classTitle"]
                                    classCount[classtitle] += 1
                                    #print("\n classtitle: ", classtitle, " at ", img_basename)
                                    points = data["objects"][invi_indx]["points"]["exterior"]
                                    objectindx -= 1
                                    invi_indx += 1
                                    #print("\n object index, and invi ", objectindx, " ", invi_indx)
                                    #print("ann name to check if in same or diff??", ann)
                                    create_sam_mask(predictor, imgdir, img_basename, classtitle, points, invi_indx)

            '''finally:
                    if "India" not in img_basename:
                        print("\n was not found :< ", item.name)'''
        print("\n num of img and ann matches, ", indx)
    print("\n done segmenting.. showing histogram")


def create_file(full_path):
    full_path.mkdir(parents=True, exist_ok=True)


# SAM segmentaatio maski luodaan kuvan bounding box ndc koordinaatioista,
# yhdessä luodussa kuvassa on monta luokkatietoa.

def create_sam_mask(predictor, imgdir, img_basename, classtitle, points, invi_indx):
    indx = invi_indx
    outerpathdir = pathlib.Path(outerfile)
    image_rgb = cv2.imread(imgdir)
    predictor.set_image(image_rgb)
    parent_folder = pathlib.Path(__file__).parent
    save_directory = pathlib.Path(parent_folder / "past-runs")
    create_file(save_directory)
    create_file(outerpathdir)
    imgfilename = f"{img_basename}.jpg"
    # kuvan .json bboxin koordinaatit, jotka rajavat segmentaation
    minx = points[0][0]
    miny = points[0][1]
    maxx = points[1][0]
    maxy = points[1][1]
    res = [val for key, val in names.items() if classtitle in key]
    res_val = res[0]
    results = predictor(bboxes=[minx, miny,maxx, maxy], labels=res)
    for i, r in enumerate(results):
        # color_coded luokkatiedot on eritelty erillisillä väreillä, vain debuggaamiseen jotta kuvat on rajattu oikein
        # mutta itse luokkien värejä voi tulevaisuudessa käyttää front-end puolella + classtitle kategoriaa, jotenkin?
        masks_Data = r.masks
        color_codedtraining(outerpathdir, imgfilename, masks_Data, res_val, image_rgb, invi_indx)
        create_mask_yxz_labels(masks_Data, img_basename, res_val)


def label_per_enum(label_image,mask_Data):
    for enum, mask in enumerate(mask_Data):
        curr_label = mask.data.cpu().numpy()  # Converts from tensors to a numpy compatible array on the CPU
        mnarray = curr_label.squeeze()  # reduce each mask into 2D array
        label_image[mnarray] = enum + 1  # set each mask to a unique ID (enum)

    return (label_image)


#Segmantaatio mask's 0-1 koordinaatio systeemistä tarvitaan xyn koordinaatit, esim, 0.99609375 0.31640625
#numerot ovat SAM segmentaation inviduaaliset pisteet, ja yksi .txt tiedosto on per kuvan_basename, .txt tiedostossa erotaan koordinaatit luokkanumeroittain (names)
#koordinaatit tallennetaan .txt tiedostoon samalla nimella kuin vastaava kuva model.train() kutsua varten

def create_mask_yxz_labels(mask_Data, img_basename, res_val):
    diff_is_acceptable_to_change = False
    array_shape = [mask_Data.shape[1], mask_Data.shape[2]]
    label_img_zero = np.zeros(array_shape, dtype=np.int32)
    #label_image = label_per_enum(label_img_zero, mask_Data)
    normalized_coords = mask_Data.xyn
    textfile_name = f"{img_basename}.txt"
    segann_Path = pathlib.Path(settings.segann)
    create_file(segann_Path)
    fulltext_file = pathlib.Path(segann_Path/textfile_name)
    if fulltext_file.is_file():
        time_modified = fulltext_file.stat().st_mtime
        time_modified_readable = datetime.datetime.fromtimestamp((time_modified))
        time_now = datetime.datetime.now()
        diff = time_now - time_modified_readable
        if diff.total_seconds() > 120:
            #print("was recent, within to minutes. rewrite over", diff)
            diff_is_acceptable_to_change = True

    if diff_is_acceptable_to_change:
        reader = open(str(segann_Path / textfile_name), "w")
    else:
        reader = open(str(segann_Path / textfile_name), "a")
        #print("rewriting contents.. ")
        # before if rewrite change
    '''if fulltext_file.is_file():
        reader = open(str(segann_Path/textfile_name), "a")
    else:
        reader = open(str(segann_Path / textfile_name), "w")'''

    try:

        for y, mask in enumerate(normalized_coords):
            reader.write("\n")
            reader.write(str(res_val))
            reader.write(" ")

            for mask in np.nditer(normalized_coords):
                reader.write(str(mask))
                reader.write(" ")

    finally:
        reader.close()
        print("file done")


def color_codedtraining(outerpathdir, imgfilename, masks_Data, res_val, image_rgb, invi_indx):

        #the new image with more than one segmentation masks already in it
        if invi_indx > 1:
            img = cv2.imread(str(outerpathdir / imgfilename))
        else:
            img = image_rgb #original image, no masks. Set in fileLoc

        mask = masks_Data.data[0].cpu().numpy()
        mask = (mask > 0.5).astype("uint8")
        #colors based on the classname and rbg values
        rgb_color = colors[res_val]
        colored_mask = img.copy()
        colored_mask[mask == 1] = rgb_color
        alpha = 0.5
        #img is 'old' image, colored_mask is where the 'new' img gets data added
        # aka new image with old results in it
        blended = cv2.addWeighted(img, 1 - alpha, colored_mask, alpha, 0)
        cv2.imwrite(str(outerpathdir / imgfilename), blended)


def count_yolo_classes(segann_path):

    class_counts = Counter()

    segann_path = pathlib.Path(segann_path)

    for txt_file in segann_path.glob("*.txt"):

        with open(txt_file, "r") as reader:

            for line in reader:

                line = line.strip()

                if not line:
                    continue

                values = line.split()

                class_id = int(values[0])

                class_counts[class_id] += 1

    return class_counts


def print_distribution(id_to_name, class_counts):

    total = sum(class_counts.values())

    for class_id, count in sorted(class_counts.items()):

        class_name = id_to_name[class_id]

        pct = 100 * count / total

        print(
            f"{class_name}: {count} ({pct:.2f}%)"
        )

def histogram_from_yolo(class_counts, id_to_name):

    labels = [
        id_to_name[class_id]
        for class_id in sorted(class_counts.keys())
    ]

    counts = [
        class_counts[class_id]
        for class_id in sorted(class_counts.keys())
    ]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts)

    plt.xlabel("Class")
    plt.ylabel("Number of annotations")
    plt.title("YOLO Segmentation Dataset Distribution")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
    print_distribution(id_to_name, class_counts)


