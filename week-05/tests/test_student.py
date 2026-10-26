"""可修改的小测试示例：另选输入，保留自己的预期与解释。

测试通过参数接收课程 fixture，--impl 才能切换候选实现。
不要直接 from operations import pop_last 绕过这个开关。
"""

import numpy as np


def test_my_pop_example(pop_last):
    items = [7, 4]

    result = pop_last(items)

    assert result == 4
    assert items == [7]


def test_my_pop_last_repeated_on_three_items(pop_last):
    # 预测：依次取出 9、3、5，最后空列表返回 None。
    items = [5, 3, 9]

    assert pop_last(items) == 9
    assert items == [5, 3]
    assert pop_last(items) == 3
    assert items == [5]
    assert pop_last(items) == 5
    assert items == []
    assert pop_last(items) is None
    assert items == []


def test_my_positive_squares_mixed_list(positive_squares):
    # 预测：[5, 0, -1, 2, 2] -> [25, 4, 4]，0 与负数被跳过，重复的 2 保留。
    values = [5, 0, -1, 2, 2]
    before = list(values)

    result = positive_squares(values)

    assert result == [25, 4, 4]
    assert isinstance(result, list)
    assert values == before


def test_my_positive_squares_numpy_array(positive_squares):
    # 预测：array([4, -2, 0, 3]) -> [16, 9]，原数组内容不变。
    values = np.array([4, -2, 0, 3], dtype=int)
    before = values.copy()

    result = positive_squares(values)

    assert result == [16, 9]
    assert isinstance(result, list)
    np.testing.assert_array_equal(values, before)


def test_my_positive_square_map_order_and_negatives(positive_square_map):
    # 预测：{"x": 3, "y": 0, "z": 3, "w": -4} -> {"x": 9, "z": 9}，
    # 键顺序为 ["x", "z"]，原字典完全不变。
    record = {"x": 3, "y": 0, "z": 3, "w": -4}
    before = record.copy()

    result = positive_square_map(record)

    assert result == {"x": 9, "z": 9}
    assert list(result) == ["x", "z"]
    assert isinstance(result, dict)
    assert record == before
    assert list(record) == list(before)
