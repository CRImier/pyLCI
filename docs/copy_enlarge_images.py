#!/usr/bin/env python
import os
from PIL import Image

current_size_assertion = (128, 64)
desired_size = (256, 128)

output_folder = '_static'

images = [["../ui/tests/canvas_1.png", "canvas_test_1.png"],
          ["../ui/tests/canvas_2.png", "canvas_test_2.png"],
          ["../ui/tests/canvas_3.png", "canvas_test_3.png"],
          ["../ui/tests/canvas_4.png", "canvas_test_4.png"],
          ["../ui/tests/canvas_5.png", "canvas_test_5.png"],
          ["../ui/tests/canvas_6.png", "canvas_test_6.png"],
          ["../ui/tests/canvas_7.png", "canvas_test_7.png"],
          ["../ui/tests/canvas_8.png", "canvas_test_8.png"]]

for image_path, destination_filename in images:
    image = Image.open(image_path)
    assert(image.size == current_size_assertion)
    new_image = image.resize(desired_size)
    new_image.save(os.path.join(output_folder, destination_filename))
