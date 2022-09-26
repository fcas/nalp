"""Text-based discriminator.
"""

from typing import Optional, Tuple

import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Dense, Dropout, MaxPool1D

from nalp.core import Discriminator
from nalp.utils import logging

logger = logging.get_logger(__name__)


class TextDiscriminator(Discriminator):
    """A TextDiscriminator class stands for the
    text-discriminative part of a Generative Adversarial Network.

    """

    def __init__(
        self,
        max_length: Optional[int] = 1,
        embedding_size: Optional[int] = 32,
        n_filters: Optional[Tuple[int, ...]] = (64),
        filters_size: Optional[Tuple[int, ...]] = (1),
        dropout_rate: Optional[float] = 0.25,
    ) -> None:
        """Initialization method.

        Args:
            max_length: Maximum length of the sequences.
            embedding_size: The size of the embedding layer.
            n_filters: Number of filters to be applied.
            filters_size: Size of filters to be applied.
            dropout_rate: Dropout activation rate.

        """

        logger.info("Overriding class: Discriminator -> TextDiscriminator.")

        super(TextDiscriminator, self).__init__(name="D_text")

        self.embedding = Dense(embedding_size, name="embedding")

        self.conv = [
            Conv2D(
                n,
                (k, embedding_size),
                strides=(1, 1),
                padding="valid",
                name=f"conv_{k}",
            )
            for n, k in zip(n_filters, filters_size)
        ]

        self.pool = [
            MaxPool1D(max_length - k + 1, 1, name=f"pool_{k}") for k in filters_size
        ]

        self.highway = Dense(sum(n_filters), name="highway")

        self.drop = Dropout(dropout_rate, name="drop")

        logger.info("Class overrided.")

    def call(self, x: tf.Tensor, training: Optional[bool] = True) -> tf.Tensor:
        """Method that holds vital information whenever this class is called.

        Args:
            x: A tensorflow's tensor holding input data.
            training: Whether architecture is under training or not.

        Returns:
            (tf.Tensor): The same tensor after passing through each defined layer.

        """

        x = self.embedding(x)
        x = tf.expand_dims(x, -1)

        convs = [tf.squeeze(tf.nn.relu(conv(x)), 2) for conv in self.conv]
        pools = [pool(conv) for pool, conv in zip(self.pool, convs)]

        x = tf.concat(pools, 2)
        hw = self.highway(x)
        x = tf.math.sigmoid(hw) * tf.nn.relu(hw) + (1 - tf.math.sigmoid(hw)) * x

        x = self.drop(x, training=training)

        return x
