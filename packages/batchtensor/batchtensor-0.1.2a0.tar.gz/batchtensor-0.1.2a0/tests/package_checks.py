from __future__ import annotations

import logging

import torch
from coola import objects_are_equal

logger = logging.getLogger(__name__)


def check_nested() -> None:
    logger.info("Checking batchtensor.nested package...")

    from batchtensor.nested import index_select_along_batch

    assert objects_are_equal(
        index_select_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([[5], [4], [3], [2], [1]]),
            },
            torch.tensor([4, 3, 2, 1, 0]),
        ),
        {
            "a": torch.tensor([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
            "b": torch.tensor([[1], [2], [3], [4], [5]]),
        },
    )


def check_recursive() -> None:
    logger.info("Checking batchtensor.recursive package...")

    from batchtensor.recursive import recursive_apply

    assert objects_are_equal(recursive_apply([1, "abc"], str), ["1", "abc"])


def check_tensor() -> None:
    logger.info("Checking batchtensor.tensor package...")

    from batchtensor.tensor import index_select_along_batch

    assert objects_are_equal(
        index_select_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]), torch.tensor([4, 3, 2, 1, 0])
        ),
        torch.tensor([[8, 9], [6, 7], [4, 5], [2, 3], [0, 1]]),
    )


def main() -> None:
    check_nested()
    check_recursive()
    check_tensor()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
