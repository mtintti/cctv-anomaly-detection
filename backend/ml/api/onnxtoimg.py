
import numpy as np
import torch
import ultralytics.utils.ops
from PIL import Image
from PIL.ImageDraw import ImageDraw

from backend.app.config import logger
from backend.ml.schema.final_imgs import FinalImagesObject
from backend.ml.schema.predict_obj import FoundOnnxObject

#objects_found = []
names = {
  0: "alligator crack",
  1: "longitudinal crack",
  2: "pothole",
  3: "transverse crack",
  4: "other corruption"
}

colors= { 0: [121, 212, 119, 255], 1:[234, 184, 133, 255], 2:[96, 112, 160, 255], 3: [75, 40, 163, 255], 4:[81,28,63, 255] }

def reshape_combine_coeffprototype(segmasks_prototypes, coeffs, tensor_width, tensor_height, original_img_w, original_img_h, scale, pad):

    # yhdistetään prototyyppi maskit 'oikeiden' mask löytöjen kanssa.segmask_prototypes shape on (32, 128, 128),
    # coeffs shape saadan kaikkien löytöjen numeron (N), 32 inviduaalisten bbox segmentaatio maskien shape  (N, 32).
    # Nämä yhdistetään toisiinsa masks= kohdassa jotta saadaan tulokseksi, (N, 128, 128)
    coeffs = torch.from_numpy(coeffs)
    segmasks_prototypes = torch.from_numpy(segmasks_prototypes)
    masks = torch.einsum("nc, chw->nhw", coeffs, segmasks_prototypes)
    #print("shape of masks ", masks.shape)
    masks_sigmoid = torch.sigmoid(masks)
    #print("shape of masks_sigmid ", masks_sigmoid.shape)
    #print("original_img_w and original_img_h in reshape_combine_coeffs")
    #print(original_img_w, original_img_h)

    rescaled_mask = ultralytics.utils.ops.scale_masks(masks_sigmoid[None].float(), (original_img_h, original_img_w))
    rescaled_mask = rescaled_mask.squeeze(0) #removing the batch as our shape would be ( 1,N,W, H) otherwise
    #print(" shape of rescaled_mask ", rescaled_mask.shape)

    return rescaled_mask


def scale_coordinates_tensor_to_img(x_cord, y_cord, bboxw, bboxh, scale, pad):
    # muutetaan scale ja pad valueilla, onnx mallin koordinaatit kuvan skaalaan
    # koska saadut koordinaatit ovat mallinnettu 512x512 kuvan mukaan, ollen liian pieniä
    pad_y = pad[0]  # leveys
    pad_x = pad[1]  # korkeus

    x = (x_cord - pad_x) / scale
    y = (y_cord - pad_y) / scale

    x2 = (bboxw - pad_x) / scale
    y2 = (bboxh - pad_y) / scale

    p1tuple = (x, y)
    p2tuple = (x2, y2)
    return p1tuple, p2tuple


def color_and_draw_segmentation_bbox(cropped, all_colors, coords, original_rgba, final_composed_images):
    # was here final_composed_images = []
    #print("cropped length ", len(cropped))
    for i in range(len(cropped)):
        cropped_invi = np.array(cropped[i])
        invidual_color = all_colors[i]
        cropped_invi_bw = (cropped_invi > 0.37).astype("uint8") * 255  # making it black and white

        # laitetaan segmentaatio maski overlayksi jotta se näkyy bounding boxin sisällä,
        # vaihdetaan valkoinen väri === 255, segmentaatio maskin omaksi väriksi (invidual_color).
        # alkuperäinen kuva ja overlay segmentaatio kuva yhdistetään yhdeksi kuvaksi
        overlay = np.zeros(
            (cropped_invi_bw.shape[0], cropped_invi_bw.shape[1], 4),
            dtype=np.uint8
        )

        overlay[cropped_invi_bw == 255] = invidual_color
        chosen_invidual_bbox_xy = coords[i]
        coordinate = (50, 100)
        overlay_bbox = np.zeros(
            (cropped_invi_bw.shape[0], cropped_invi_bw.shape[1], 4),
            dtype=np.uint8
        )
        overlay_bbox_image = Image.fromarray(overlay_bbox)
        rgba_check_original_pre = overlay_bbox_image.getpixel(coordinate)
        # alkuperäinen kuva, piirretään bbox coordinaatiin xy, väriksi laitetaan RGBA väri invidual_color:ista

        ImageDraw(overlay_bbox_image, 'RGBA').rectangle((chosen_invidual_bbox_xy[0], chosen_invidual_bbox_xy[1]), None,
                                                        outline=(
                                                        invidual_color[0], invidual_color[1], invidual_color[2],
                                                        invidual_color[3]), width=2)
        overlay_segmentmask_image = Image.fromarray(overlay)
        rgba_check_overlay = overlay_segmentmask_image.getpixel(coordinate)
        if len(rgba_check_overlay) == 4 and len(rgba_check_original_pre) == 4:
            blended = Image.alpha_composite(overlay_bbox_image, overlay_segmentmask_image)
            #print("moved past combining both overlays")
        else:
            logger.error("in onnx_to_img length of overlay_seg or overlay_bbox is rgb instead of rgba")
        addable = FinalImagesObject(index=i, overlay_seg=overlay_segmentmask_image, overlay_bbox=overlay_bbox_image, blended_together=blended, original_rgba=original_rgba)
        final_composed_images.append(addable)
        #return overlay_segmentmask_image, overlay_bbox_image, blended

    return final_composed_images


def arrange_full_segmentation_mask(objects_found, finalised_boxes, finalised_coeffs, segmasks_prototypes, original_image, final_composed_images):

    coords = []
    all_colors = []
    #muutetaan alkuperäinen kuva RGBA kuvaksi, koska tarvitsemme kaikkia chanelleitä myöhemmin segmentaatio overlay kuvaan


    for z in range(len(objects_found)):
        #print("in range objects_found ", objects_found[z])
        x_cord = objects_found[z].x
        y_cord = objects_found[z].y
        bboxw = objects_found[z].w
        bboxh = objects_found[z].h
        classname_id = objects_found[z].class_id
        original_img_w = objects_found[z].original_image_w
        original_img_h = objects_found[z].original_image_h
        scale = objects_found[z].scale
        pad = objects_found[z].pad
        p1tuple, p2tuple = scale_coordinates_tensor_to_img(x_cord, y_cord, bboxw, bboxh, scale, pad)
        coordinates = p1tuple,p2tuple
        coords.append(coordinates)
        rgb_color = colors[classname_id]
        all_colors.append(rgb_color)

    #print("coeffs ", finalised_coeffs.shape, " prototypes ", segmasks_prototypes.shape)

    #print("moving to reshape_combined ")
    #print(" ")
    final_mask_probs = reshape_combine_coeffprototype(segmasks_prototypes=segmasks_prototypes, coeffs=finalised_coeffs,
                                                      tensor_width=512, tensor_height=512,
                                                      original_img_w=original_img_w, original_img_h=original_img_h,
                                                      scale=scale, pad=pad)

    # bbox coordinaatit ovat yhdistetty yhteen tensoriin, tensorin shape on (N, 4)
    # yhdessä indexissä on yhden bounding box coordinaatit jota käytetään croppaamaan segmentaatio mask

    bbox_coords_as_tensor = torch.as_tensor(coords)
    bbox_coords_as_tensor= bbox_coords_as_tensor.reshape(len(coords), 4)
    #print("shape of bbox coords ", bbox_coords_as_tensor.shape)

    #print("finalmaskprops ", final_mask_probs.shape)
    cropped = ultralytics.utils.ops.crop_mask(final_mask_probs, bbox_coords_as_tensor)
    #print("cropped ", cropped.shape)
    #loopataan kaikki cropatut maskit, filteröidään mask 10% tarkkuudella musta valkoiseksi,
    # jotta vain segmentaatiot coordinaatissa on näkyvissä
    all_colors = np.array(all_colors)
    #print("colors of classess ", all_colors.shape)
    #seg_overlay, bbox_overlay, blended_together = color_and_draw_segmentation_bbox(cropped=cropped, all_colors=all_colors,coords=coords)
    final_composed_images = color_and_draw_segmentation_bbox(cropped=cropped, all_colors=all_colors, coords=coords, original_rgba=original_image, final_composed_images=final_composed_images)
    return final_composed_images


def onnx_to_img(boxes, coeff_masks,segmasks_prototypes, original_img_w, original_img_h, original_image, scale, pad, objects_found):

    indx = 0
    conf_to_pass = 0.10
    passedboxs = []
    passedcoeffs = []
    final_composed_images = []

    #koska kaikki boxes on prunattu mns kautta, poistaen löydöt jotka ovat 60% tai enemmän limittäin,
    # loopataan boxes löydöt tarkistaen että mallin luokan numeron ennustettun tulos on tarpeeksi isompi kuin 10% (conf_to_pass)
    for x in boxes:

        x_cord = x[0]
        y_cord = x[1]
        bboxw = x[2]
        bboxh = x[3]
        object_prop_score = x[4]
        classname_id = x[5]
        if object_prop_score >= conf_to_pass:
            if classname_id in names:
                name = names[classname_id]
                passedboxs.append(boxes[indx])
                passedcoeffs.append(coeff_masks[indx])
                #print("passedboxs  and passedcoeffs length ")
                #print(len(passedboxs), len(passedcoeffs))

                toadd = FoundOnnxObject(index=len(objects_found)+1, x=x_cord, y=y_cord, w=bboxw, h=bboxh, confidence_score=object_prop_score,
                                        class_id=classname_id, class_name=name, original_image_w=original_img_w, original_image_h=original_img_h, scale=scale, pad=pad)
                #print("next is to add for " )
                #print(" ")
                #print(toadd)
                objects_found.append(toadd)
                #print("info appended to objects found ", len(objects_found))
        indx += 1

    #print("past loop boxes in onnx_to_img ", len(objects_found))
    if len(passedboxs) > 0:
        finalised_boxes = np.array(passedboxs)
        finalised_coeffs = np.array(passedcoeffs)
        #print("finalised boxes and coeffs shape ", finalised_boxes.shape, " ", finalised_coeffs.shape)
        original_image_RGBA = original_image.convert('RGBA')
        #overlay_seg, overlay_bbox, blended_together = arrange_full_segmentation_mask(objects_found, finalised_boxes, finalised_coeffs, segmasks_prototypes, original_image_RGBA)
        final_composed_images = arrange_full_segmentation_mask(objects_found, finalised_boxes, finalised_coeffs, segmasks_prototypes, original_image_RGBA, final_composed_images)
        #print(" ")
        #print("original_image_rgba is present? ", original_image_RGBA, " original rgb ", original_image)

        #return overlay_seg, overlay_bbox, blended_together, original_image_RGBA
        return final_composed_images, original_image_RGBA
    else:
        print("--- !!")
        print("No predictions found!! ", len(passedboxs) , len(passedcoeffs))
        original_image_none = original_image.convert('RGBA')
        addable_nonFound = FinalImagesObject(index=len(objects_found)+1, overlay_seg=None, overlay_bbox=None,
                                    blended_together=None, original_rgba=original_image_none)
        final_composed_images.append(addable_nonFound)
        return final_composed_images, original_image_none
