from asfeslib.core import sort
import pytest
import asyncio

def test_all_sorts_agree():
    data = [5, 1, 9, 3, 2]
    expected = sorted(data)
    funcs = [
        sort.bubble_sort,
        sort.insertion_sort,
        sort.selection_sort,
        sort.merge_sort,
        sort.quick_sort,
        sort.heap_sort,
        sort.sort_builtin,
    ]
    for f in funcs:
        assert f(data) == expected

def test_reverse_sort():
    data = [1, 2, 3]
    for f in [sort.quick_sort, sort.merge_sort, sort.sort_builtin]:
        assert f(data, reverse=True) == [3, 2, 1]

def test_async_sort_event_loop():
    data = [4, 3, 2, 1]
    result = asyncio.run(sort.async_sort(data, delay=0))
    assert result == sorted(data)

def test_sorts_with_key():
    data = [{"v": 3}, {"v": 1}, {"v": 2}]
    expected = sorted(data, key=lambda x: x["v"])

    funcs = [
        sort.bubble_sort,
        sort.insertion_sort,
        sort.selection_sort,
        sort.merge_sort,
        sort.quick_sort,
        sort.heap_sort,
        sort.sort_builtin,
    ]

    for f in funcs:
        assert f(data, key=lambda x: x["v"]) == expected


def test_reverse_sort_all():
    data = [1, 2, 3, 4]
    expected = sorted(data, reverse=True)

    funcs = [
        sort.bubble_sort,
        sort.insertion_sort,
        sort.selection_sort,
        sort.merge_sort,
        sort.quick_sort,
        sort.heap_sort,
        sort.sort_builtin,
    ]

    for f in funcs:
        assert f(data, reverse=True) == expected


def test_async_sort_negative_delay_raises():
    with pytest.raises(ValueError):
        asyncio.run(sort.async_sort([3, 2, 1], delay=-0.1))