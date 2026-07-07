from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class ImgSize:
    height: int
    width: int
    channel: int = 3

    def get_tuple(self) -> tuple:
        return (self.height, self.width, self.channel)


def letterbox(img: np.ndarray, new_size: ImgSize, fill_value: int = 114) -> np.ndarray:
    aspect_ratio = min(new_size.height / img.shape[1], new_size.width / img.shape[0])

    new_size_with_ar = int(img.shape[1] * aspect_ratio), int(img.shape[0] * aspect_ratio)
    resized_img = np.asarray(cv2.resize(img, new_size_with_ar), dtype=np.uint8)
    resized_h, resized_w, _ = resized_img.shape

    padded_img = np.full(new_size.get_tuple(), fill_value, dtype=np.uint8)
    center_x = new_size.width / 2
    center_y = new_size.height / 2

    x_range_start = int(center_x - (resized_w / 2))
    x_range_end = int(center_x + (resized_w / 2))

    y_range_start = int(center_y - (resized_h / 2))
    y_range_end = int(center_y + (resized_h / 2))
    pad = (y_range_start,x_range_start) # notice pad has changed, Pad value for de-letterboxing is now just (y,x)

    padded_img[y_range_start: y_range_end, x_range_start: x_range_end, :] = resized_img
    return padded_img, aspect_ratio, pad