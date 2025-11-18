"""Test file for bbox/utils.py"""

import unittest

from easy_bbox import Bbox, nms


class TestNMS(unittest.TestCase):
    """Unit tests for the nms function."""

    def test_nms_empty_input(self):
        """Test that the NMS function returns an empty list when the input is empty."""
        self.assertEqual(nms([], []), [])

    def test_nms_single_bbox(self):
        """Test that the NMS function returns the single bbox when there is only one bbox."""
        bboxes = [Bbox(left=0, top=0, right=10, bottom=10)]
        scores = [0.9]
        self.assertEqual(
            nms(bboxes, scores), [(Bbox(left=0, top=0, right=10, bottom=10), 0.9)]
        )

    def test_nms_no_suppression(self):
        """Test that the NMS function returns all bboxes when there is no suppression."""
        bboxes = [
            Bbox(left=0, top=0, right=10, bottom=10),
            Bbox(left=20, top=20, right=30, bottom=30),
        ]
        scores = [0.9, 0.8]
        self.assertEqual(
            nms(bboxes, scores),
            [
                (Bbox(left=0, top=0, right=10, bottom=10), 0.9),
                (Bbox(left=20, top=20, right=30, bottom=30), 0.8),
            ],
        )

    def test_nms_suppression(self):
        """Test that the NMS function suppresses bboxes with IoU above the threshold."""
        bboxes = [
            Bbox(left=0, top=0, right=10, bottom=10),
            Bbox(left=5, top=5, right=15, bottom=15),
        ]
        scores = [0.7, 0.8]
        self.assertListEqual(
            nms(bboxes, scores, iou_threshold=0.1),
            [(Bbox(left=5, top=5, right=15, bottom=15), 0.8)],
        )

        # Assert that results are ordered by decreasing score
        self.assertListEqual(
            nms(bboxes, scores, iou_threshold=1),
            sorted(zip(bboxes, scores), key=lambda x: x[1], reverse=True),
        )

    def test_nms_invalid_input(self):
        """Test that the NMS function raises a ValueError when the input is invalid."""
        bboxes = [Bbox(left=0, top=0, right=10, bottom=10)]
        scores = [0.9, 0.8]
        with self.assertRaises(ValueError):
            nms(bboxes, scores)


if __name__ == "__main__":
    unittest.main()
