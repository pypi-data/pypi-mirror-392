"""
bbox.py

Provides the `Bbox` class and utility functions for manipulating bounding boxes
in various coordinate formats (Pascal VOC, COCO, YOLO, etc.). Supports
transformations, geometric operations, and conversions.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple
from typing_extensions import Self

from pydantic import BaseModel, model_validator, __version__ as pydantic_version


class Bbox(BaseModel):
    """
    A class to represent a Bbox (inherits from Pydantic BaseModel).

    The bbox is stored in Pascal_VOC format:
    top-left, bottom-right with a top-left origin (PIL coord system).
    (meaning that top < bottom)

    The bottom and right edges are considered excluded from the Bbox for compatibility with array
    slicing and PIL image cropping features (in case of Int Bboxes).

    Attributes:
        left (float): The left coordinate of the bounding box.
        top (float): The top coordinate of the bounding box.
        right (float): The right coordinate of the bounding box.
        bottom (float): The bottom coordinate of the bounding box.
    """

    left: float
    top: float
    right: float
    bottom: float

    if pydantic_version >= "2.12.0":

        @model_validator(mode="after")
        def check_passwords_match(self) -> Self:
            if self.left > self.right or self.top > self.bottom:
                raise ValueError("The Bbox is not valid (negative width or height).")
            return self
    else:
        # Ensure compatibility with previous pydantic versions

        @model_validator(mode="after")  # type: ignore[arg-type]
        @classmethod
        def check_passwords_match(cls, model: "Bbox") -> "Bbox":
            if model.left > model.right or model.top > model.bottom:
                raise ValueError("The Bbox is not valid (negative width or height).")
            return model

    # region From methods
    @classmethod
    def from_tlbr(cls, tlbr: Sequence[float]) -> Bbox:
        """
        Initializes the bounding box from top-left and bottom-right coordinates.

        Args:
            tlbr (Sequence[float]): A sequence containing the top-left and bottom-right coordinates
                of the bounding box in the format (left, top, right, bottom).

        Returns:
            Bbox: The Bbox instance.

        Raises:
            ValueError: If the length of the sequence is not 4, or if the Bbox is not valid
                (ie `left > right` or `top > bottom`).

        Example:
            >>> bbox = Bbox.from_tlbr((10, 20, 30, 40))
            >>> print(bbox.left, bbox.top, bbox.right, bbox.bottom)
            10 20 30 40
        """
        _assert_sequence_len(seq=tlbr)
        return cls(left=tlbr[0], top=tlbr[1], right=tlbr[2], bottom=tlbr[3])

    @classmethod
    def from_tlwh(cls, tlwh: Sequence[float]) -> Bbox:
        """
        Initializes the bounding box from top-left and width-height coordinates.

        Args:
            tlwh (Sequence[float]): A sequence containing the top-left and width-height coordinates
                of the bounding box in the format (left, top, width, height).

        Returns:
            Bbox: The Bbox instance.

        Raises:
            ValueError: If the length of the sequence is not 4, or if the Bbox is not valid
                (ie `width < 0` or `height < 0`).

        Example:
            >>> bbox = Bbox.from_tlwh((10, 20, 20, 30))
            >>> print(bbox.left, bbox.top, bbox.right, bbox.bottom)
            10 20 30 50
        """
        _assert_sequence_len(seq=tlwh)
        return cls(
            left=tlwh[0],
            top=tlwh[1],
            right=tlwh[0] + tlwh[2],
            bottom=tlwh[1] + tlwh[3],
        )

    @classmethod
    def from_cwh(cls, cwh: Sequence[float]) -> Bbox:
        """
        Initializes the bounding box from center and width-height coordinates.

        Args:
            cwh (Sequence[float]): A sequence containing the center and width-height coordinates
                of the bounding box in the format (center_x, center_y, width, height).

        Returns:
            Bbox: The Bbox instance.

        Raises:
            ValueError: If the length of the sequence is not 4, or if the Bbox is not valid
                (ie `width < 0` or `height < 0`).

        Example:
            >>> bbox = Bbox.from_cwh((20, 35, 20, 30))
            >>> print(bbox.left, bbox.top, bbox.right, bbox.bottom)
            10 20 30 50
        """
        _assert_sequence_len(seq=cwh)
        half_width = cwh[2] / 2
        half_height = cwh[3] / 2
        return cls(
            left=cwh[0] - half_width,
            top=cwh[1] - half_height,
            right=cwh[0] + half_width,
            bottom=cwh[1] + half_height,
        )

    from_xyxy = from_tlbr
    from_pascal_voc = from_tlbr
    from_list = from_tlbr
    from_coco = from_tlwh

    # endregion

    # region To methods
    def to_tlbr(self) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Top-Left, Bottom-Right format.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates (x_min, y_min,
            x_max, y_max).

            x_min and y_min are the coordinates of the top-left corner of the bounding box.
            x_max and y_max are the coordinates of the bottom-right corner of the bounding box.
        """
        return (self.left, self.top, self.right, self.bottom)

    def to_list(self) -> List[float]:
        """
        Returns the bounding box coordinates in Top-Left, Bottom-Right format.

        Returns:
            List[float]: The bounding box coordinates [x_min, y_min,
            x_max, y_max].

            x_min and y_min are the coordinates of the top-left corner of the bounding box.
            x_max and y_max are the coordinates of the bottom-right corner of the bounding box.
        """
        return [self.left, self.top, self.right, self.bottom]

    def to_norm_tlbr(self, img_w: int, img_h: int) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Top-Left, Bottom-Right format, normalized
        based on the image dimensions.

        Args:
            img_w (int): The image width in pixels.
            img_h (int): The image height in pixels.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates (x_min, y_min,
            x_max, y_max).

            x_min and y_min are the coordinates of the top-left corner of the bounding box.
            x_max and y_max are the coordinates of the bottom-right corner of the bounding box.

            All the returned values are **NORMALIZED** based on the image dimensions.
        """
        return (
            self.left / img_w,
            self.top / img_h,
            self.right / img_w,
            self.bottom / img_h,
        )

    def to_tlwh(self) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Top-Left, Width-Height format.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates (x_min, y_min,
            width, height).

            x_min and y_min are coordinates of the top-left corner of the bounding box.
        """
        return (self.left, self.top, self.width, self.height)

    def to_norm_tlwh(self, img_w: int, img_h: int) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Top-Left, Width-Height format, normalized
        based on the image dimensions.

        Args:
            img_w (int): The image width in pixels.
            img_h (int): The image height in pixels.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates [x_min, y_min,
            width, height].

            x_min and y_min are the coordinates of the top-left corner of the bounding box.

            All the returned values are **NORMALIZED** based on the image dimensions.
        """
        return (
            self.left / img_w,
            self.top / img_h,
            self.right / img_w,
            self.bottom / img_h,
        )

    def to_cwh(self) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Center, Width-Height format.

        Returns:
            Tuple[float, float, float, float]: The bounding box coordinates (x_center, y_center,
            width, height).
        """
        return (*self.center, self.width, self.height)

    def to_norm_cwh(self, img_w: int, img_h: int) -> Tuple[float, float, float, float]:
        """
        Returns the bounding box coordinates in Center, Width-Height format, normalized
        based on the image dimensions.

        Args:
            img_w (int): The image width in pixels.
            img_h (int): The image height in pixels.

        Returns:
            Tuple[float, float, float, float]: The NORMALIZED bounding box
            coordinates (x_center, y_center, width, height).
        """
        cx, cy = self.center
        return (cx / img_w, cy / img_h, self.width / img_w, self.height / img_h)

    def to_polygon(
        self,
    ) -> Tuple[
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
        Tuple[float, float],
    ]:
        """
        Returns the bounding box corners as points.

        Returns:
            The corners coordinates in (x, y) format.
            The order is `top_left > top_right > bottom_right > bottom_left`
        """
        return (
            (self.left, self.top),
            (self.right, self.top),
            (self.right, self.bottom),
            (self.left, self.bottom),
        )

    to_pascal_voc = to_tlbr
    to_xyxy = to_tlbr
    to_albu = to_norm_tlbr
    to_coco = to_tlwh
    to_yolo = to_norm_cwh

    # endregion

    # region Transformations
    def shift(self, horizontal_shift: float = 0, vertical_shift: float = 0) -> Bbox:
        """
        Return a shifted Bbox by the specified horizontal and vertical amounts.

        Args:
            horizontal_shift (float, optional): The amount to shift the bounding box horizontally.
                Defaults to 0.
            vertical_shift (float, optional): The amount to shift the bounding box vertically.
                Defaults to 0.

        Returns:
            Bbox: The shifted Bbox instance.
        """
        return Bbox(
            left=self.left + horizontal_shift,
            top=self.top + vertical_shift,
            right=self.right + horizontal_shift,
            bottom=self.bottom + vertical_shift,
        )

    def scale(self, scale_factor: float) -> Bbox:
        """
        Return a scaled Bbox by the specified scale factor. The scaling will be from the center.

        Args:
            scale_factor (float): The factor to scale the bounding box by. Width and height will
                be scaled by this factor.

        Returns:
            Bbox: The scaled Bbox instance.

        Raises:
            ValueError: If the scale is strictly negative.
        """
        if scale_factor < 0:
            raise ValueError(
                "Scaling with a negative value would result in an invalid Bbox."
            )

        cx, cy = self.center
        new_width = self.width * scale_factor
        new_height = self.height * scale_factor

        return Bbox(
            left=cx - new_width / 2,
            right=cx + new_width / 2,
            top=cy - new_height / 2,
            bottom=cy + new_height / 2,
        )

    def scale_area(self, scale_factor: float) -> Bbox:
        """
        Return a scaled Bbox such that `new area`/`old area` == `scale_factor`.
        The scaling will be from the center.

        Args:
            scale_factor (float): The factor to scale the bounding box by. The area will be scaled by this factor.
                (and width and height will be scaled by the square root of this factor.)

        Returns:
            Bbox: The scaled Bbox instance.

        Raises:
            ValueError: If the scale is strictly negative.
        """
        if scale_factor < 0:
            raise ValueError(
                "Scaling with a negative value would result in an invalid Bbox."
            )

        return self.scale(scale_factor=scale_factor**0.5)

    def expand_uniform(self, padding: float) -> Bbox:
        """
        Return an expanded Bbox by the specified padding.

        Args:
            padding (float): The amount to expand the bounding box by.

        Returns:
            Bbox: The expanded Bbox instance.
        """
        return Bbox(
            left=self.left - padding,
            right=self.right + padding,
            top=self.top - padding,
            bottom=self.bottom + padding,
        )

    def expand(
        self, left: float = 0, top: float = 0, right: float = 0, bottom: float = 0
    ) -> Bbox:
        """
        Return an expanded Bbox by the specified padding for each side.

        Args:
            left (float, optional): The amount to expand the left side of the bounding box by.
                Defaults to 0.
            top (float, optional): The amount to expand the top side of the bounding box by.
                Defaults to 0.
            right (float, optional): The amount to expand the right side of the bounding box by.
                Defaults to 0.
            bottom (float, optional): The amount to expand the bottom side of the bounding box by.
                Defaults to 0.

        Returns:
            Bbox: The expanded Bbox instance.
        """
        return Bbox(
            left=self.left - left,
            right=self.right + right,
            top=self.top - top,
            bottom=self.bottom + bottom,
        )

    def pad_to_square(self) -> Bbox:
        """Returns a padded Bbox to make it a square."""
        width = self.width
        height = self.height

        if width > height:
            diff = (width - height) / 2
            return Bbox(
                left=self.left,
                right=self.right,
                top=self.top - diff,
                bottom=self.bottom + diff,
            )

        if height > width:
            diff = (height - width) / 2
            return Bbox(
                left=self.left - diff,
                right=self.right + diff,
                top=self.top,
                bottom=self.bottom,
            )

        return self.model_copy()

    def pad_to_aspect_ratio(self, target_ratio: float) -> Bbox:
        """
        Returns a padded Bbox to achieve the target aspect ratio.

        Args:
            target_ratio (float): The target aspect ratio.

        Returns:
            Bbox: A Bbox instance padded to the correct ratio.

        Raises:
            ValueError: If target_ratio is <= 0.
        """
        if target_ratio <= 0:
            raise ValueError(
                f"Target ratio cannot be negative or zero. Received {target_ratio}"
            )

        current_ratio = self.aspect_ratio
        if current_ratio > target_ratio:
            # Need to increase height
            new_height = self.width / target_ratio
            diff = (new_height - self.height) / 2
            return Bbox(
                left=self.left,
                right=self.right,
                top=self.top - diff,
                bottom=self.bottom + diff,
            )

        if current_ratio < target_ratio:
            # Need to increase width
            new_width = self.height * target_ratio
            diff = (new_width - self.width) / 2
            return Bbox(
                left=self.left - diff,
                right=self.right + diff,
                top=self.top,
                bottom=self.bottom,
            )

        return self.model_copy()

    def clip_to_img(self, img_w: int, img_h: int) -> Bbox:
        """
        Returns a clipped Bbox to the image dimensions.

        Remember that the bottom and right edges are considered excluded from the bbox, so
        `Bbox(left=-10, top=-20, right=100, bottom=120).clip_to_img(img_w=32, img_h=64)`
        returns `Bbox(left=0, top=0, right=32, bottom=64)`

        Args:
            img_w (int): The image width in pixels.
            img_h (int): The image height in pixels.

        Returns:
            Bbox: The clipped Bbox.
        """
        return Bbox(
            left=max(0, self.left),
            top=max(0, self.top),
            right=min(img_w, self.right),
            bottom=min(img_h, self.bottom),
        )

    # endregion

    def overlaps(self, other: Bbox) -> bool:
        """
        Checks if the current bounding box overlaps with another bounding box.

        Two bboxes are considered as overlapping if they intersect with a non-zero area.

        Args:
            other (Bbox): The other bounding box to check for overlap.

        Returns:
            bool: True if the bounding boxes overlap, False otherwise.
        """
        inter = self.intersection(other)

        return inter is not None and inter.area > 0

    def contains_point(self, x: float, y: float) -> bool:
        """
        Checks if a point is inside the bounding box.

        Args:
            x (float): The x-coordinate of the point.
            y (float): The y-coordinate of the point.

        Returns:
            bool: True if the point is inside the bounding box, False otherwise.
        """
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def union(self, other: Bbox) -> Bbox:
        """
        Calculates the minimal Bbox that englobes this one AND the other.

        Args:
            other (Bbox): The other bounding box to calculate the union with.

        Returns:
            Bbox: The minimal englobing Bbox.
        """
        return Bbox(
            left=min(self.left, other.left),
            top=min(self.top, other.top),
            right=max(self.right, other.right),
            bottom=max(self.bottom, other.bottom),
        )

    def intersection(self, other: Bbox) -> Optional[Bbox]:
        """
        Calculates the intersection with another Bbox. If the resulting Bbox is not valid (ie
        `left > right` or `top > bottom`, returns None.

        Args:
            other (Bbox): The other bounding box to calculate the intersection with.

        Returns:
            Optional[Bbox]: The intersection of the two bounding boxes if valid.
        """
        left = max(self.left, other.left)
        top = max(self.top, other.top)
        right = min(self.right, other.right)
        bottom = min(self.bottom, other.bottom)

        if left > right or top > bottom:
            return None

        return Bbox(left=left, top=top, right=right, bottom=bottom)

    def iou(self, other: Bbox) -> float:
        """Calculates the Intersection over Union (IoU) with another bounding box.

        Args:
            other (Bbox): The other Bbox.

        Returns:
            float: The IoU between the two bounding boxes.
        """
        # Calculate the intersection area
        inter = self.intersection(other)
        intersection_area = inter.area if inter is not None else 0

        # Calculate the union area
        union_area = self.area + other.area - intersection_area

        if union_area == 0:
            return 0

        # Calculate the IoU
        return intersection_area / union_area

    def distance_to_point(self, x: float, y: float) -> float:
        """
        Calculates the distance from the bounding box to a point.

        Args:
            x (float): The x-coordinate of the point.
            y (float): The y-coordinate of the point.

        Returns:
            float: The distance from the bounding box to the point.
        """
        dx = max(self.left - x, 0, x - self.right)
        dy = max(self.top - y, 0, y - self.bottom)
        return (dx**2 + dy**2) ** 0.5

    @property
    def width(self) -> float:
        """The width of the Bbox."""
        return self.right - self.left

    @property
    def height(self):
        """The height of the Bbox."""
        return self.bottom - self.top

    @property
    def area(self) -> float:
        """The area of the Bbox"""
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        """The center of the Bbox in (x, y) format."""
        return (self.left + self.right) / 2, (self.top + self.bottom) / 2

    @property
    def aspect_ratio(self) -> float:
        """The aspect ratio of the Bbox (width over height)."""
        return self.width / self.height

    __or__ = union
    __and__ = intersection


def _assert_sequence_len(seq: Sequence[float], target_len: int = 4) -> None:
    """
    Asserts that the length of the sequence is 4.

    Args:
        seq (Sequence[float]): The sequence to check the length of.
        target_len (int, optional): The target length of the sequence. Defaults to 4.

    Raises:
        ValueError: If the length of the sequence is not the target one.
    """
    if len(seq) != target_len:
        raise ValueError(
            f"A sequence of len {len(seq)} has been passed. Need a sequence of len {target_len}."
        )
