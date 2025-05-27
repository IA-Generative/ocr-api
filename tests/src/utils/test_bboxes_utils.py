from src.schemas.box import Bbox
from src.utils.bboxes import sort_bboxes_reading_order


def test_single_line_sorted_left_to_right():
    boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="1"),
        Bbox(x=0.3, y=0.1, width=1, height=1, confidence=1, text="1"),
        Bbox(x=0.2, y=0.1, width=1, height=1, confidence=1, text="1"),
    ]
    sorted_boxes = sort_bboxes_reading_order(boxes)
    assert len(sorted_boxes) == 1
    assert sorted_boxes == [[boxes[0], boxes[2], boxes[1]]]


def test_two_lines_sorted_top_to_bottom_and_left_to_right():
    boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="1"),  # line 1
        Bbox(x=0.3, y=0.1, width=1, height=1, confidence=1, text="1"),  # line 1
        Bbox(x=0.2, y=0.2, width=1, height=1, confidence=1, text="1"),  # line 2
        Bbox(x=0.05, y=0.2, width=1, height=1, confidence=1, text="1"),  # line 2
    ]
    sorted_boxes = sort_bboxes_reading_order(boxes)
    assert sorted_boxes == [[boxes[0], boxes[1]], [boxes[3], boxes[2]]]


def test_boxes_with_close_y_are_grouped_in_same_line():
    boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="1"),
        Bbox(
            x=0.2, y=0.1001, width=1, height=1, confidence=1, text="1"
        ),  # very close y
        Bbox(x=0.3, y=0.1002, width=1, height=1, confidence=1, text="1"),
    ]
    sorted_boxes = sort_bboxes_reading_order(boxes)
    assert len(sorted_boxes) == 1
    assert sorted_boxes == [boxes]


def test_boxes_far_enough_are_in_different_lines():
    boxes = [
        Bbox(x=0.1, y=0.1, width=1, height=1, confidence=1, text="1"),
        Bbox(
            x=0.2, y=0.2, width=1, height=1, confidence=1, text="1"
        ),  # delta_y = 0.1 > threshold
    ]
    sorted_boxes = sort_bboxes_reading_order(boxes, delta_y=0.05)
    # Check that the order is preserved: top to bottom
    assert len(sorted_boxes) == 2
    assert sorted_boxes == [[boxes[0]], [boxes[1]]]
