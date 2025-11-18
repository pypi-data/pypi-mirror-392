from __future__ import annotations

import pytest
import torch
from coola import objects_are_equal

from batchtensor.nested import (
    amax_along_batch,
    amax_along_seq,
    amin_along_batch,
    amin_along_seq,
    argmax_along_batch,
    argmax_along_seq,
    argmin_along_batch,
    argmin_along_seq,
    max_along_batch,
    max_along_seq,
    mean_along_batch,
    mean_along_seq,
    median_along_batch,
    median_along_seq,
    min_along_batch,
    min_along_seq,
    prod_along_batch,
    prod_along_seq,
    sum_along_batch,
    sum_along_seq,
)
from tests.unit.tensor.test_reduction import DTYPES, FLOATING_DTYPES

######################################
#     Tests for amax_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[8, 9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {"a": torch.tensor([8, 9], dtype=dtype), "b": torch.tensor(4)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[8, 9]], dtype=dtype), "b": torch.tensor([4])},
    )


def test_amax_along_batch_nested() -> None:
    assert objects_are_equal(
        amax_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {"a": torch.tensor([8, 9]), "b": torch.tensor(4), "c": [torch.tensor(9)]},
    )


####################################
#     Tests for amax_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[4], [9]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": torch.tensor([4, 9], dtype=dtype), "b": torch.tensor([4])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[4], [9]], dtype=dtype), "b": torch.tensor([[4]])},
    )


def test_amax_along_seq_nested() -> None:
    assert objects_are_equal(
        amax_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": torch.tensor([4, 9]), "b": torch.tensor([4]), "c": [torch.tensor([9])]},
    )


######################################
#     Tests for amin_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 1]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {"a": torch.tensor([0, 1], dtype=dtype), "b": torch.tensor(0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0, 1]], dtype=dtype), "b": torch.tensor([0])},
    )


def test_amin_along_batch_nested() -> None:
    assert objects_are_equal(
        amin_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {"a": torch.tensor([0, 1]), "b": torch.tensor(0), "c": [torch.tensor(5)]},
    )


####################################
#     Tests for amin_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[0], [5]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": torch.tensor([0, 5], dtype=dtype), "b": torch.tensor([0])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0], [5]], dtype=dtype), "b": torch.tensor([[0]])},
    )


def test_amin_along_seq_nested() -> None:
    assert objects_are_equal(
        amin_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": torch.tensor([0, 5]), "b": torch.tensor([0]), "c": [torch.tensor([5])]},
    )


########################################
#     Tests for argmax_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4, 4]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {"a": torch.tensor([4, 4]), "b": torch.tensor(0)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[4, 4]]), "b": torch.tensor([0])},
    )


def test_argmax_along_batch_nested() -> None:
    assert objects_are_equal(
        argmax_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {"a": torch.tensor([4, 4]), "b": torch.tensor(0), "c": [torch.tensor(4)]},
    )


######################################
#     Tests for argmax_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4], [4]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": torch.tensor([4, 4]), "b": torch.tensor([0])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[4], [4]]), "b": torch.tensor([[0]])},
    )


def test_argmax_along_seq_nested() -> None:
    assert objects_are_equal(
        argmax_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": torch.tensor([4, 4]), "b": torch.tensor([0]), "c": [torch.tensor([4])]},
    )


########################################
#     Tests for argmin_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {"a": torch.tensor([0, 0]), "b": torch.tensor(4)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0, 0]]), "b": torch.tensor([4])},
    )


def test_argmin_along_batch_nested() -> None:
    assert objects_are_equal(
        argmin_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {"a": torch.tensor([0, 0]), "b": torch.tensor(4), "c": [torch.tensor(0)]},
    )


######################################
#     Tests for argmin_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0], [0]]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": torch.tensor([0, 0]), "b": torch.tensor([4])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0], [0]]), "b": torch.tensor([[4]])},
    )


def test_argmin_along_seq_nested() -> None:
    assert objects_are_equal(
        argmin_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {"a": torch.tensor([0, 0]), "b": torch.tensor([4]), "c": [torch.tensor([0])]},
    )


#####################################
#     Tests for max_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.max([torch.tensor([8, 9], dtype=dtype), torch.tensor([4, 4])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.max([torch.tensor([[8, 9]], dtype=dtype), torch.tensor([[4, 4]])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": torch.return_types.max([torch.tensor([8, 9], dtype=dtype), torch.tensor([4, 4])]),
            "b": torch.return_types.max([torch.tensor(4), torch.tensor(0)]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.max(
                [torch.tensor([[8, 9]], dtype=dtype), torch.tensor([[4, 4]])]
            ),
            "b": torch.return_types.max([torch.tensor([4]), torch.tensor([0])]),
        },
    )


def test_max_along_batch_nested() -> None:
    assert objects_are_equal(
        max_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.return_types.max(
                [torch.tensor([8, 9], dtype=torch.float), torch.tensor([4, 4])]
            ),
            "b": torch.return_types.max([torch.tensor(4), torch.tensor(0)]),
            "c": [torch.return_types.max([torch.tensor(9), torch.tensor(4)])],
        },
    )


###################################
#     Tests for max_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.max([torch.tensor([4, 9], dtype=dtype), torch.tensor([4, 4])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.return_types.max([torch.tensor([[4], [9]], dtype=dtype), torch.tensor([[4], [4]])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            }
        ),
        {
            "a": torch.return_types.max([torch.tensor([4, 9], dtype=dtype), torch.tensor([4, 4])]),
            "b": torch.return_types.max([torch.tensor([5]), torch.tensor([0])]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.max(
                [torch.tensor([[4], [9]], dtype=dtype), torch.tensor([[4], [4]])]
            ),
            "b": torch.return_types.max([torch.tensor([[5]]), torch.tensor([[0]])]),
        },
    )


def test_max_along_seq_nested() -> None:
    assert objects_are_equal(
        max_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.return_types.max(
                [torch.tensor([4, 9], dtype=torch.float), torch.tensor([4, 4])]
            ),
            "b": torch.return_types.max([torch.tensor([5]), torch.tensor([0])]),
            "c": [torch.return_types.max([torch.tensor([9]), torch.tensor([4])])],
        },
    )


######################################
#     Tests for mean_along_batch     #
######################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([4.0, 5.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4.0, 5.0]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            }
        ),
        {"a": torch.tensor([4.0, 5.0], dtype=dtype), "b": torch.tensor(2.0)},
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[4.0, 5.0]], dtype=dtype), "b": torch.tensor([2.0])},
    )


def test_mean_along_batch_nested() -> None:
    assert objects_are_equal(
        mean_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "c": [torch.tensor([5, 6, 7, 8, 9], dtype=torch.float)],
            }
        ),
        {"a": torch.tensor([4.0, 5.0]), "b": torch.tensor(2.0), "c": [torch.tensor(7.0)]},
    )


####################################
#     Tests for mean_along_seq     #
####################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([2.0, 7.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[2.0], [7.0]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            }
        ),
        {"a": torch.tensor([2.0, 7.0], dtype=dtype), "b": torch.tensor([2.0])},
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[2.0], [7.0]], dtype=dtype), "b": torch.tensor([[2.0]])},
    )


def test_mean_along_seq_nested() -> None:
    assert objects_are_equal(
        mean_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]], dtype=torch.float),
                "c": [torch.tensor([[5, 6, 7, 8, 9]], dtype=torch.float)],
            }
        ),
        {"a": torch.tensor([2.0, 7.0]), "b": torch.tensor([2.0]), "c": [torch.tensor([7.0])]},
    )


########################################
#     Tests for median_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.median([torch.tensor([4, 5], dtype=dtype), torch.tensor([2, 2])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.median([torch.tensor([[4, 5]], dtype=dtype), torch.tensor([[2, 2]])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            }
        ),
        {
            "a": torch.return_types.median(
                [torch.tensor([4, 5], dtype=dtype), torch.tensor([2, 2])]
            ),
            "b": torch.return_types.median([torch.tensor(2.0), torch.tensor(2)]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.median(
                [torch.tensor([[4, 5]], dtype=dtype), torch.tensor([[2, 2]])]
            ),
            "b": torch.return_types.median([torch.tensor([2.0]), torch.tensor([2])]),
        },
    )


def test_median_along_batch_nested() -> None:
    assert objects_are_equal(
        median_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0], dtype=torch.float),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.return_types.median([torch.tensor([4.0, 5.0]), torch.tensor([2, 2])]),
            "b": torch.return_types.median([torch.tensor(2.0), torch.tensor(2)]),
            "c": [torch.return_types.median([torch.tensor(7), torch.tensor(2)])],
        },
    )


######################################
#     Tests for median_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.median([torch.tensor([2, 7], dtype=dtype), torch.tensor([2, 2])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.median(
            [torch.tensor([[2], [7]], dtype=dtype), torch.tensor([[2], [2]])]
        ),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {
            "a": torch.return_types.median(
                [torch.tensor([2, 7], dtype=dtype), torch.tensor([2, 2])]
            ),
            "b": torch.return_types.median([torch.tensor([2]), torch.tensor([2])]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.median(
                [torch.tensor([[2], [7]], dtype=dtype), torch.tensor([[2], [2]])]
            ),
            "b": torch.return_types.median([torch.tensor([[2]]), torch.tensor([[2]])]),
        },
    )


def test_median_along_seq_nested() -> None:
    assert objects_are_equal(
        median_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.return_types.median([torch.tensor([2, 7]), torch.tensor([2, 2])]),
            "b": torch.return_types.median([torch.tensor([2]), torch.tensor([2])]),
            "c": [torch.return_types.median([torch.tensor([7]), torch.tensor([2])])],
        },
    )


#####################################
#     Tests for min_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.min([torch.tensor([0, 1], dtype=dtype), torch.tensor([0, 0])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.min([torch.tensor([[0, 1]], dtype=dtype), torch.tensor([[0, 0]])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            }
        ),
        {
            "a": torch.return_types.min([torch.tensor([0, 1], dtype=dtype), torch.tensor([0, 0])]),
            "b": torch.return_types.min([torch.tensor(0), torch.tensor(4)]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([4, 3, 2, 1, 0]),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.min(
                [torch.tensor([[0, 1]], dtype=dtype), torch.tensor([[0, 0]])]
            ),
            "b": torch.return_types.min([torch.tensor([0]), torch.tensor([4])]),
        },
    )


def test_min_along_batch_nested() -> None:
    assert objects_are_equal(
        min_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([4, 3, 2, 1, 0]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.return_types.min(
                [torch.tensor([0, 1], dtype=torch.float), torch.tensor([0, 0])]
            ),
            "b": torch.return_types.min([torch.tensor(0), torch.tensor(4)]),
            "c": [torch.return_types.min([torch.tensor(5), torch.tensor(0)])],
        },
    )


###################################
#     Tests for min_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.min([torch.tensor([0, 5], dtype=dtype), torch.tensor([0, 0])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.return_types.min([torch.tensor([[0], [5]], dtype=dtype), torch.tensor([[0], [0]])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            }
        ),
        {
            "a": torch.return_types.min([torch.tensor([0, 5], dtype=dtype), torch.tensor([0, 0])]),
            "b": torch.return_types.min([torch.tensor([1]), torch.tensor([4])]),
        },
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            },
            keepdim=True,
        ),
        {
            "a": torch.return_types.min(
                [torch.tensor([[0], [5]], dtype=dtype), torch.tensor([[0], [0]])]
            ),
            "b": torch.return_types.min([torch.tensor([[1]]), torch.tensor([[4]])]),
        },
    )


def test_min_along_seq_nested() -> None:
    assert objects_are_equal(
        min_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.return_types.min(
                [torch.tensor([0, 5], dtype=torch.float), torch.tensor([0, 0])]
            ),
            "b": torch.return_types.min([torch.tensor([1]), torch.tensor([4])]),
            "c": [torch.return_types.min([torch.tensor([5]), torch.tensor([0])])],
        },
    )


######################################
#     Tests for prod_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 945], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 945]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([5, 4, 3, 2, 1]),
            }
        ),
        {"a": torch.tensor([0, 945], dtype=dtype), "b": torch.tensor(120)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([5, 4, 3, 2, 1]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0, 945]], dtype=dtype), "b": torch.tensor([120])},
    )


def test_prod_along_batch_nested() -> None:
    assert objects_are_equal(
        prod_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([5, 4, 3, 2, 1]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.tensor([0, 945], dtype=torch.float),
            "b": torch.tensor(120),
            "c": [torch.tensor(15120)],
        },
    )


####################################
#     Tests for prod_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 15120], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[0], [15120]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            }
        ),
        {"a": torch.tensor([0, 15120], dtype=dtype), "b": torch.tensor([120])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[0], [15120]], dtype=dtype), "b": torch.tensor([[120]])},
    )


def test_prod_along_seq_nested() -> None:
    assert objects_are_equal(
        prod_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[5, 4, 3, 2, 1]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.tensor([0, 15120], dtype=torch.float),
            "b": torch.tensor([120]),
            "c": [torch.tensor([15120])],
        },
    )


#####################################
#     Tests for sum_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([20, 25], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[20, 25]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([5, 4, 3, 2, 1]),
            }
        ),
        {"a": torch.tensor([20, 25], dtype=dtype), "b": torch.tensor(15)},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype),
                "b": torch.tensor([5, 4, 3, 2, 1]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[20, 25]], dtype=dtype), "b": torch.tensor([15])},
    )


def test_sum_along_batch_nested() -> None:
    assert objects_are_equal(
        sum_along_batch(
            {
                "a": torch.tensor([[0.0, 1.0], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]]),
                "b": torch.tensor([5, 4, 3, 2, 1]),
                "c": [torch.tensor([5, 6, 7, 8, 9])],
            }
        ),
        {
            "a": torch.tensor([20, 25], dtype=torch.float),
            "b": torch.tensor(15),
            "c": [torch.tensor(35)],
        },
    )


###################################
#     Tests for sum_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_tensor(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([10, 35], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_tensor_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[10], [35]], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_dict(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            }
        ),
        {"a": torch.tensor([10, 35], dtype=dtype), "b": torch.tensor([10])},
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_dict_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
            },
            keepdim=True,
        ),
        {"a": torch.tensor([[10], [35]], dtype=dtype), "b": torch.tensor([[10]])},
    )


def test_sum_along_seq_nested() -> None:
    assert objects_are_equal(
        sum_along_seq(
            {
                "a": torch.tensor([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0, 9.0]]),
                "b": torch.tensor([[4, 3, 2, 1, 0]]),
                "c": [torch.tensor([[5, 6, 7, 8, 9]])],
            }
        ),
        {
            "a": torch.tensor([10, 35], dtype=torch.float),
            "b": torch.tensor([10]),
            "c": [torch.tensor([35])],
        },
    )
