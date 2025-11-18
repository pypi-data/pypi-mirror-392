from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import numpy.typing as npt


@dataclass()
class RoiRectangle:
    """
    A class representing a rectangle.

    Args:
        y1 (int): The y-coordinate of the top-left corner of the rectangle.
        y2 (int | None): The y-coordinate of the bottom-right corner of the rectangle.
            If it is None it mean infinit range.
        x1 (int): The x-coordinate of the top-left corner of the rectangle.
        x2 (int | None): The x-coordinate of the bottom-right corner of the rectangle.
            If it is None it mean infinit range.
        The cropping operation uses half-open intervals [x1, x2) and [y1, y2).
        This means the coordinates (x2, y2) are not included in the cropped region.
    """

    y1: int = field(init=True, repr=True)
    y2: Optional[int] = field(init=True, repr=True)
    x1: int = field(init=True, repr=True)
    x2: Optional[int] = field(init=True, repr=True)

    def __post_init__(self):
        if self.x2 is not None and self.x2 < self.x1:
            raise ValueError("x2 must be >= x1")
        if self.y2 is not None and self.y2 < self.y1:
            raise ValueError("y2 must be >= y1")

    @property
    def width(self) -> Optional[int]:
        return None if self.x2 is None else self.x2 - self.x1

    @property
    def height(self) -> Optional[int]:
        return None if self.y2 is None else self.y2 - self.y1

    @property
    def center(self) -> Optional[tuple[int, int]]:
        if self.x2 is None or self.y2 is None:
            return None
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def move(self, dx: int, dy: int) -> RoiRectangle:
        """Move the ROI relative to its current position.
        """
        return RoiRectangle(
            self.y1 + dy,
            self.y2 + dy if self.y2 is not None else None,
            self.x1 + dx,
            self.x2 + dx if self.x2 is not None else None,
        )

    def recenter(self, new_center: tuple[int, int]) -> RoiRectangle:
        x_i, y_i = self.center if self.center else (
            self.x1 + (self.width or 0) // 2,
            self.y1 + (self.height or 0) // 2,
        )
        x_f, y_f = new_center
        dx, dy = x_f - x_i, y_f - y_i

        return RoiRectangle(
            y1=self.y1 + dy,
            y2=self.y2 + dy if self.y2 is not None else None,
            x1=self.x1 + dx,
            x2=self.x2 + dx if self.x2 is not None else None,
        )

    def resize(self, new_width: int, new_height: int) -> RoiRectangle:
        if self.center is None:
            if self.x2 is None and self.y2 is None:
                return self
            cx = self.x1 + (self.width or 0) // 2
            cy = self.y1 + (self.height or 0) // 2
        else:
            cx, cy = self.center

        half_w, half_h = new_width // 2, new_height // 2
        new_x1, new_y1 = cx - half_w, cy - half_h
        new_x2, new_y2 = cx + (new_width - half_w), cy + (new_height - half_h)

        return RoiRectangle(
            y1=new_y1,
            y2=new_y2 if self.y2 is not None else None,
            x1=new_x1,
            x2=new_x2 if self.x2 is not None else None,
        )


    def to_tuple(self) -> tuple[int, Optional[int], int, Optional[int]]:
        """
        Get the coordinates of the ROI.
        """
        return self.y1, self.y2, self.x1, self.x2

    @property
    def area(self) -> Optional[int]:
        """
        Get the area of the ROI.
        """
        if self.width is None or self.height is None:
            return None
        return self.width * self.height

    @property
    def shape(self) -> tuple[Optional[int], Optional[int]]:
        """
        get the shape of the ROI.
        """
        return (self.height, self.width)

    def get_slices(self) -> tuple[slice, slice]:
        """
        Get the slices for the ROI.

        Returns:
            tuple: Slices for the x and y axes.
        """
        return slice(self.y1, self.y2), slice(self.x1,  self.x2)

    def slice(self, image: np.ndarray) -> npt.NDArray:
        """
        Slice the specified region from the image.

        Args:
            image (np.ndarray): Input image.

        Returns:
            np.ndarray: Sliced region of the image.
        """
        return image[..., self.y1 : self.y2, self.x1 : self.x2]

    @classmethod
    def from_tuple(cls, coords: tuple[int, Optional[int], int, Optional[int]]) -> 'RoiRectangle':
        """
        Create a RoiRectangle instance from a tuple of coordinates.
        The tuple should contain four integers: (y1, y2, x1, x2).   
        """
        y1, y2, x1, x2 = coords
        return cls(y1=y1, y2=y2, x1=x1, x2=x2)


RoiRectangle.__module__ = "roi_rectangle"


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib import patches

    # 테스트용 이미지 생성
    test_image = np.random.random((100, 100))

    # RoiRectangle 인스턴스 생성
    roi = RoiRectangle(x1=20, y1=30, x2=70, y2=80)

    # ROI 정보 출력
    print("Initial ROI:")
    print(roi)

    # ROI 중심 좌표 출력
    print("Center Coordinate:", roi.center)

    # ROI 크기 출력
    print("Width:", roi.width)
    print("Height:", roi.height)

    # ROI 이동 테스트
    new_center = (50, 50)
    
    print("\nAfter Moving to Center:")
    print(roi.recenter(new_center))

    # ROI 크기 조절 테스트
    new_width, new_height = 30, 40
    
    print("\nAfter Resizing:")
    print(roi.resize(new_width, new_height))

    # ROI 영역 슬라이싱 테스트
    roi_slice = roi.slice(test_image)
    print("\nROI Slice:")
    print(roi_slice)

    # 원본 이미지 시각화
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.imshow(test_image, cmap='gray')

    # ROI 슬라이싱
    roi_slice = roi.slice(test_image)

    # 슬라이싱한 이미지 시각화
    plt.subplot(1, 2, 2)
    plt.title('ROI Slice')
    plt.imshow(roi_slice, cmap='gray')

    # ROI 영역 표시
    plt.gca().add_patch(patches.Rectangle(
        (roi.x1, roi.y1),
        roi.width,
        roi.height,
        linewidth=2,
        edgecolor='r',
        facecolor='none'
    ))
    plt.show()
