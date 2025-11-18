# Tensor

## Batch

`batcharray` provides functions to manipulate arrays representing a batch of examples.
The functions assume the arrays have the following shape: `batch_size, *` where `*` means
any axes.

## Sequence

`batcharray` provides functions to manipulate arrays representing a batch of sequences.
The functions assume the arrays have the following shape: `batch_size, seq_len, *` where `*` means
any axes.
