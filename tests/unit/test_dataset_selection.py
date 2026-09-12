from __future__ import annotations

import pytest

from utils.dataset_selection import select_dataset_slice


def test_select_dataset_slice_returns_the_requested_fixed_range() -> None:
    dataset = [{"id": index} for index in range(5)]

    selected = select_dataset_slice(dataset, start=2, count=1)

    assert selected == [{"id": 2}]
    assert dataset == [{"id": index} for index in range(5)]


@pytest.mark.parametrize(
    ("start", "count"),
    [(-1, 1), (0, 0), (4, 2)],
)
def test_select_dataset_slice_rejects_invalid_ranges(
    start: int,
    count: int,
) -> None:
    with pytest.raises(ValueError):
        select_dataset_slice([{"id": index} for index in range(5)], start, count)
