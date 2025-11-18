# Tensor

## Batch

`batchtensor` provides functions to manipulate tensors representing a batch of examples.
The functions assume the tensors have the following shape: `batch_size, *` where `*` means
any dimensions.

## Sequence

`batchtensor` provides functions to manipulate tensors representing a batch of sequences.
The functions assume the tensors have the following shape: `batch_size, seq_len, *` where `*` means
any dimensions.
