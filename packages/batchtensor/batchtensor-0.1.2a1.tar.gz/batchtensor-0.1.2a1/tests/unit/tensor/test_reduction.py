from __future__ import annotations

import pytest
import torch
from coola import objects_are_equal

from batchtensor.tensor import (
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

DTYPES = (torch.float, torch.double, torch.long)
FLOATING_DTYPES = (torch.float, torch.double)


######################################
#     Tests for amax_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([8, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[8, 9]], dtype=dtype),
    )


####################################
#     Tests for amax_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([4, 9], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amax_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[4], [9]], dtype=dtype),
    )


######################################
#     Tests for amin_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 1], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 1]], dtype=dtype),
    )


####################################
#     Tests for amin_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 5], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_amin_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        amin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[0], [5]], dtype=dtype),
    )


########################################
#     Tests for argmax_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4, 4]]),
    )


######################################
#     Tests for argmax_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([4, 4]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmax_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmax_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4], [4]]),
    )


########################################
#     Tests for argmin_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 0]]),
    )


######################################
#     Tests for argmin_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 0]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_argmin_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        argmin_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0], [0]]),
    )


#####################################
#     Tests for max_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.max([torch.tensor([8, 9], dtype=dtype), torch.tensor([4, 4])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.max([torch.tensor([[8, 9]], dtype=dtype), torch.tensor([[4, 4]])]),
    )


###################################
#     Tests for max_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.max([torch.tensor([4, 9], dtype=dtype), torch.tensor([4, 4])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_max_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        max_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.return_types.max([torch.tensor([[4], [9]], dtype=dtype), torch.tensor([[4], [4]])]),
    )


######################################
#     Tests for mean_along_batch     #
######################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([4.0, 5.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[4.0, 5.0]], dtype=dtype),
    )


####################################
#     Tests for mean_along_seq     #
####################################


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([2.0, 7.0], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", FLOATING_DTYPES)
def test_mean_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        mean_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[2.0], [7.0]], dtype=dtype),
    )


########################################
#     Tests for median_along_batch     #
########################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.median([torch.tensor([4, 5], dtype=dtype), torch.tensor([2, 2])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.median([torch.tensor([[4, 5]], dtype=dtype), torch.tensor([[2, 2]])]),
    )


######################################
#     Tests for median_along_seq     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.median([torch.tensor([2, 7], dtype=dtype), torch.tensor([2, 2])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_median_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        median_along_seq(
            torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.median(
            [torch.tensor([[2], [7]], dtype=dtype), torch.tensor([[2], [2]])]
        ),
    )


#####################################
#     Tests for min_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.return_types.min([torch.tensor([0, 1], dtype=dtype), torch.tensor([0, 0])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.return_types.min([torch.tensor([[0, 1]], dtype=dtype), torch.tensor([[0, 0]])]),
    )


###################################
#     Tests for min_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.return_types.min([torch.tensor([0, 5], dtype=dtype), torch.tensor([0, 0])]),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_min_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        min_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.return_types.min([torch.tensor([[0], [5]], dtype=dtype), torch.tensor([[0], [0]])]),
    )


######################################
#     Tests for prod_along_batch     #
######################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([0, 945], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[0, 945]], dtype=dtype),
    )


####################################
#     Tests for prod_along_seq     #
####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([0, 15120], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_prod_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        prod_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[0], [15120]], dtype=dtype),
    )


#####################################
#     Tests for sum_along_batch     #
#####################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype)),
        torch.tensor([20, 25], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_batch_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_batch(
            torch.tensor([[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]], dtype=dtype), keepdim=True
        ),
        torch.tensor([[20, 25]], dtype=dtype),
    )


###################################
#     Tests for sum_along_seq     #
###################################


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype)),
        torch.tensor([10, 35], dtype=dtype),
    )


@pytest.mark.parametrize("dtype", DTYPES)
def test_sum_along_seq_keepdim_true(dtype: torch.dtype) -> None:
    assert objects_are_equal(
        sum_along_seq(torch.tensor([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], dtype=dtype), keepdim=True),
        torch.tensor([[10], [35]], dtype=dtype),
    )
