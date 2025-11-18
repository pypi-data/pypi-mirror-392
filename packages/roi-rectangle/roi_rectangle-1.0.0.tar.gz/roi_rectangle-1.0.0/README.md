# roi_rectangle

A Python module for handling rectangular regions of interest (ROI) in images.

## Features

- Define a rectangular ROI with coordinates.
- Get the center of the ROI.
- Move the ROI to a new center.
- Resize the ROI.
- Get the coordinates and area of the ROI.
- Slice the ROI region from an image.

## Installation

To install the `roi_rectangle` module, use:

```sh
pip install roi_rectangle
```

## Usage

Here's an example of how to use the `RoiRectangle` module:

```python
from roi_rect import RoiRectangle
import numpy as np
import matplotlib.pyplot as plt

# Create a test image
test_image = np.random.random((100, 100))

# Create an instance of RoiRectangle
roi = RoiRectangle(y1=30, y2=80, x1=20, x2=70)

# Print ROI information
print("Initial ROI:")
print(roi)

# Get the center coordinate of the ROI
print("Center Coordinate:", roi.center)

# Get the width and height of the ROI
print("Width:", roi.width)
print("Height:", roi.height)

# Move the ROI to a new center
new_center = (50, 50)
roi.move_to_center(new_center)
print("\nAfter Moving to Center:")
print(roi)

# Resize the ROI
new_width, new_height = 30, 40
roi.resize(new_width, new_height)
print("\nAfter Resizing:")
print(roi)

# Slice the ROI region from the test image
roi_slice = roi.slice(test_image)
print("\nROI Slice:")
print(roi_slice)

# Visualize the original image and the sliced ROI
plt.figure(figsize=(8, 4))
plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(test_image, cmap='gray')

plt.subplot(1, 2, 2)
plt.title('ROI Slice')
plt.imshow(roi_slice, cmap='gray')

plt.gca().add_patch(plt.Rectangle((roi.x1, roi.y1), roi.width, roi.height, linewidth=2, edgecolor='r', facecolor='none'))
plt.show()
```

## License

This project is licensed under the MIT License.