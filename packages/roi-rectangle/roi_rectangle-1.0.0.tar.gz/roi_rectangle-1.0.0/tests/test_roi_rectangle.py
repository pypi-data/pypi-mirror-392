import pytest
import numpy as np

from roi_rectangle import RoiRectangle


def test_roi_rectangle_init():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    assert roi.x1 == 10
    assert roi.y1 == 20
    assert roi.x2 == 30
    assert roi.y2 == 40
    assert roi.width == 20
    assert roi.height == 20


def test_roi_rectangle_center():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    assert roi.center == (20, 30)


def test_roi_rectangle_move_to_center():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    roi = roi.recenter((50, 60))
    assert roi.x1 == 40
    assert roi.y1 == 50
    assert roi.x2 == 60
    assert roi.y2 == 70


def test_roi_rectangle_resize():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    roi = roi.resize(40, 60)
    assert roi.x1 == 0
    assert roi.y1 == 0
    assert roi.x2 == 40
    assert roi.y2 == 60
    assert roi.width == 40
    assert roi.height == 60


def test_roi_rectangle_to_tuple():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    assert roi.to_tuple() == (10, 20, 30, 40)


def test_roi_rectangle_area():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    assert roi.area == 400


def test_roi_rectangle_shape():
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    assert roi.shape == (20, 20)


def test_roi_rectangle_slice():
    image = np.random.randint(0, 255, (100, 100))
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    sliced_image = roi.slice(image)
    assert sliced_image.shape == (20, 20)


def test_roi_rectangle_get_slices():
    image = np.random.randint(0, 255, (100, 100))
    roi = RoiRectangle(x1=10, y1=20, x2=30, y2=40)
    slices = roi.get_slices()
    sliced_image = image[slices]
    assert sliced_image.shape == (20, 20)


def test_roi_rectangle_from_tuple():
    roi = RoiRectangle.from_tuple((10, 20, 30, 40))
    assert roi.x1 == 10
    assert roi.y1 == 20
    assert roi.x2 == 30
    assert roi.y2 == 40
    assert roi.width == 20
    assert roi.height == 20


def test_roi_rectangle_none_values():
    roi = RoiRectangle(x1=10, y1=20, x2=None, y2=None)
    assert roi.x1 == 10
    assert roi.y1 == 20
    assert roi.x2 is None
    assert roi.y2 is None
    assert roi.width is None
    assert roi.height is None
    assert roi.center is None
    assert roi.area is None


if __name__ == "__main__":
    pytest.main()
