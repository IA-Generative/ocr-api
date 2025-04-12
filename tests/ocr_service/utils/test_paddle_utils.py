from ocr_service.utils.paddle import parse_box


def test_parse_box():
    box = [1, 2, 3, 4, 5, 6, 7, 8]
    actual = parse_box(box=box)
    expected = [[1, 2], [3, 4], [5, 6], [7, 8]]
    assert actual == expected
