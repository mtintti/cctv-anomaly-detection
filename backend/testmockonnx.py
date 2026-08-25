import numpy as np


#onnx stub
class FakeNodeArg:
    """
    Stand-in for onnxruntime's NodeArg. get_predictions() only ever touches
    `.name` (sess.get_inputs()[0].name, and [o.name for o in sess.get_outputs()]),
    so that's all this needs to expose.
    """

    def __init__(self, name, shape=None, type_="tensor(float)"):
        self.name = name
        self.shape = shape
        self.type = type_

    def __repr__(self):
        return f"FakeNodeArg(name={self.name!r}, shape={self.shape}, type={self.type!r})"


class MockupOnnxInferenceSession:
    """
    a mock-up of the real exported best.onnx model:

      output0 -> (1, 300, 38)   each row: [x, y, w, h, conf, cls, *32 mask coeffs]
      output1 -> (1, 32, 128, 128)   mask prototypes (32 channels to match
                                      the 32 mask coeffs sliced from output0)
    """

    def __init__(
        self,
        input_name="images",
        input_shape=(1, 3, 512, 512),
        num_detections=300,
        num_attrs=38,
        mask_dim=32,
        mask_h=128,
        mask_w=128,
        seed=42,
    ):
        self._input_name = input_name
        self._num_detections = num_detections
        self._num_attrs = num_attrs
        self._mask_dim = mask_dim
        self._mask_h = mask_h
        self._mask_w = mask_w
        self._rng = np.random.default_rng(seed)

        self._inputs = [FakeNodeArg(self._input_name, shape=list(input_shape))]
        self._outputs = [
            FakeNodeArg("output0", shape=[1, self._num_detections, self._num_attrs]),
            FakeNodeArg("output1", shape=[1, self._mask_dim, self._mask_h, self._mask_w]),
        ]

    def get_inputs(self):
        return self._inputs

    def get_outputs(self):
        return self._outputs

    def run(self, output_names, input_feed):
        if self._input_name not in input_feed:
            raise KeyError(
                f"FakeInferenceSession.run expected '{self._input_name}' in "
                f"input_feed, got keys={list(input_feed.keys())}"
            )

        # box coords in a plausible pixel range for a 512x512 letterboxed image
        boxes = self._rng.uniform(0, 512, size=(1, self._num_detections, 4)).astype(np.float32)
        # conf, class, and the 32 mask coeffs all live in roughly -1..1
        rest = self._rng.uniform(-1, 1, size=(1, self._num_detections, self._num_attrs - 4)).astype(np.float32)
        output0 = np.concatenate([boxes, rest], axis=2).astype(np.float32)

        output1 = self._rng.uniform(-1, 1, size=(1, self._mask_dim, self._mask_h, self._mask_w)).astype(np.float32)

        by_name = {"output0": output0, "output1": output1}

        if not output_names:
            return [by_name["output0"], by_name["output1"]]
        return [by_name[name] for name in output_names]

