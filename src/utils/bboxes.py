from src.schemas.box import Bbox


def sort_bboxes_reading_order(
    bboxes: list[Bbox], delta_y: float = 0.005
) -> list[list[Bbox]]:
    """
    Sort bounding boxes in reading order (line by line, left to right).

    Args:
        bboxes (list[Bbox]): List of bounding boxes with attributes x and y (top-left corner).
        delta_y (float): Vertical tolerance to consider two boxes on the same line.

    Returns:
        list[Bbox]: Bounding boxes sorted in reading order.
    """
    # Step 1: Sort boxes top-to-bottom by y coordinate
    bboxes = sorted(bboxes, key=lambda box: box.y)
    lines: list[list[Bbox]] = []

    for box in bboxes:
        y_min = box.y
        added_to_line = False

        # Try to add the box to an existing line
        for line in lines:
            line_y = line[0].y
            if abs(y_min - line_y) < delta_y:
                line.append(box)
                added_to_line = True
                break

        # If no suitable line found, start a new line
        if not added_to_line:
            lines.append([box])

    # Step 2: Sort each line left-to-right by x coordinate
    for line in lines:
        line.sort(key=lambda box: box.x)

    return lines


def get_text_from_list_bboxes(boxes: list[Bbox]):
    return " ".join([b.text for b in boxes])
