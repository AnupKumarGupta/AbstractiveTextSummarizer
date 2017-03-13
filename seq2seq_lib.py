import tensorflow as tf


# Adapted to support sampled_softmax loss function, which accepts activations instead of logits.

def sequence_loss_by_example(inputs, targets, weights, loss_function, average_across_timesteps=True, name=None):
    """Sampled softmax loss for a sequence of inputs (per example).

    Args:
      inputs: List of 2D Tensors of shape [batch_size x hid_dim].
      targets: List of 1D batch-sized int32 Tensors of the same length as logits.
      weights: List of 1D batch-sized float-Tensors of the same length as logits.
      loss_function: Sampled softmax function (inputs, labels) -> loss
      average_across_timesteps: If set, divide the returned cost by the total label weight.
      name: Optional name for this operation, default: 'sequence_loss_by_example'.

    Returns:
      1D batch-sized float Tensor: The log-perplexity for each sequence.

    Raises:
      ValueError: If len(inputs) is different from len(targets) or len(weights).

    Information:
        perplexity is a measurement of how well a probability distribution or probability
        model predicts a sample.
        It may be used to compare probability models.
        A low perplexity indicates the probability distribution is good at predicting the sample.
    """

    if len(targets) != len(inputs) or len(weights) != len(inputs):
        raise ValueError('Lengths of logits, weights, and targets must be the same '
                         '%d, %d, %d.' % (len(inputs), len(weights), len(targets)))

    with tf.name_scope(name, 'sequence_loss_by_example', inputs + targets + weights):
        log_perp_list = []
        for inp, target, weight in zip(inputs, targets, weights):
            crossent = loss_function(inp, target)
            log_perp_list.append(crossent * weight)
        log_perps = tf.add_n(log_perp_list)

        if average_across_timesteps:
            total_size = tf.add_n(weights)
            total_size += 1e-12
            # Just to avoid division by 0 for all-0 weights.
            log_perps /= total_size

    return log_perps


def sampled_sequence_loss(inputs, targets, weights, loss_function, average_across_timesteps=True,
                          average_across_batch=True, name=None):
    """Weighted cross-entropy loss for a sequence of logits, batch-collapsed.

    Args:
      inputs: List of 2D Tensors of shape [batch_size x hid_dim].
      targets: List of 1D batch-sized int32 Tensors of the same length as inputs.
      weights: List of 1D batch-sized float-Tensors of the same length as inputs.
      loss_function: Sampled softmax function (inputs, labels) -> loss
      average_across_timesteps: If set, divide the returned cost by the total
        label weight.
      average_across_batch: If set, divide the returned cost by the batch size.
      name: Optional name for this operation, defaults to 'sequence_loss'.

    Returns:
      A scalar float Tensor: The average log-perplexity per symbol (weighted).

    Raises:
      ValueError: If len(inputs) is different from len(targets) or len(weights).

    Information:
        'x' is [[1, 1, 1],[1, 1, 1]]
        tf.reduce_sum(x) ==> 6
    """

    with tf.name_scope(name, 'sequence_loss_by_example', inputs + targets + weights):
        cost = tf.reduce_sum(sequence_loss_by_example(inputs, targets, weights, loss_function,
                                                      average_across_timesteps=average_across_timesteps))
        if average_across_batch:
            batch_size = tf.shape(targets[0])[0]
            cost /= tf.cast(batch_size, tf.float32)

        return cost
