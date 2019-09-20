from tensorflow.keras import layers

import nalp.utils.logging as l
from nalp.neurals.simple import SimpleNeural

logger = l.get_logger(__name__)


class StackedRNN(SimpleNeural):
    """A StackedRNN class is the one in charge of stacked Recurrent Neural Networks implementation.

    References:
        http://psych.colorado.edu/~kimlab/Elman1990.pdf

    """

    def __init__(self, vocab_size=1, embedding_size=1, hidden_size=[1, 1]):
        """Initialization method.

        Args:
            vocab_size (int): The size of the vocabulary.
            embedding_size (int): The size of the embedding layer.
            hidden_size (list): Amount of hidden neurons per cell.

        """

        logger.info('Overriding class: Neural -> StackedRNN.')

        # Overrides its parent class with any custom arguments if needed
        super(StackedRNN, self).__init__(name='stacked_rnn')

        # Creates an embedding layer
        self.embedding = layers.Embedding(
            vocab_size, embedding_size, name='embedding')

        # Creating a stack of RNN cells
        self.cells = [layers.SimpleRNNCell(size, name=f'rnn_cell{i}') for (i, size) in enumerate(hidden_size)]

        # Creates the RNN loop itself
        self.rnn = layers.RNN(self.cells, name='rnn_layer',
                              return_sequences=True)

        # Creates the linear (Dense) layer
        self.linear = layers.Dense(vocab_size, name='dense')

        logger.debug(f'Number of cells: {len(hidden_size)}')

    def call(self, x):
        """Method that holds vital information whenever this class is called.

        Args:
            x (tf.Tensor): A tensorflow's tensor holding input data.

        Returns:
            The same tensor after passing through each defined layer.

        """

        # Firstly, we apply the embedding layer
        x = self.embedding(x)

        # We need to apply the input into the first recorrent layer
        x = self.rnn(x)

        # The input also suffers a linear combination to output correct shape
        x = self.linear(x)

        return x
