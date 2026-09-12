from __future__ import annotations

from typing import Sequence, TypeVar


DatasetItem = TypeVar("DatasetItem")


def select_dataset_slice(
    dataset: Sequence[DatasetItem],
    start: int,
    count: int,
) -> list[DatasetItem]:
    if start < 0:
        raise ValueError("dataset start must be non-negative")
    if count <= 0:
        raise ValueError("dataset count must be positive")

    end = start + count
    if end > len(dataset):
        raise ValueError(
            f"dataset slice [{start}:{end}] exceeds {len(dataset)} items"
        )

    return list(dataset[start:end])
