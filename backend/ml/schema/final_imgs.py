from PIL import Image
from dataclasses import dataclass

# dataclass FinalImages luokkaan laitetaan finaalit boundingbox ja segmentaatio maskit,
# sekä yhdistety bbox ja seg kuva. Index on onnx modelista NMS ja confidence numeron jälkeen kuinka mones prediction bbox ja segmentaatio maski on
# final images luodaan append() kutsulla onnx_to_img / color_and_draw_segmentation_bbox() jonka jälkeen passataan predic.py pää looppiin

@dataclass
class FinalImagesObject:
    index: int
    overlay_seg: Image.Image | None
    overlay_bbox: Image.Image | None
    blended_together: Image.Image | None
    original_rgba: Image.Image | None
