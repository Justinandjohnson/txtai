"""
Vectors module
"""

import pickle
import tempfile


class Vectors:
    """
    Base class for sentence embeddings/vector models.
    """

    def __init__(self, config, scoring):
        # Store parameters
        self.config = config
        self.scoring = scoring

        if config:
            # Detect if this is an initialized configuration
            self.initialized = "dimensions" in config

            # Enables optional string tokenization
            self.tokenize = config.get("tokenize")

            # pylint: disable=E1111
            self.model = self.load(config.get("path"))

    def load(self, path):
        """
        Loads vector model at path.

        Args:
            path: path to vector model

        Returns:
            vector model
        """

        raise NotImplementedError

    def encode(self, data):
        """
        Encodes a batch of data using vector model.

        Args:
            data: batch of data

        Return:
            transformed data
        """

        raise NotImplementedError

    def index(self, documents, batchsize=500):
        """
        Converts a list of documents to a temporary file with embeddings arrays. Returns a tuple of document ids,
        number of dimensions and temporary file with embeddings.

        Args:
            documents: list of (id, data, tags)
            batchsize: index batch size

        Returns:
            (ids, dimensions, stream)
        """

        ids, dimensions, batches, stream = [], None, 0, None

        # Convert all documents to embedding arrays, stream embeddings to disk to control memory usage
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".npy", delete=False) as output:
            stream = output.name
            batch = []
            for document in documents:
                batch.append(document)

                if len(batch) == batchsize:
                    # Convert batch to embeddings
                    uids, dimensions = self.batch(batch, output)
                    ids.extend(uids)
                    batches += 1

                    batch = []

            # Final batch
            if batch:
                uids, dimensions = self.batch(batch, output)
                ids.extend(uids)
                batches += 1

        return (ids, dimensions, batches, stream)

    def transform(self, document):
        """
        Transforms document into an embeddings vector.

        Args:
            document: (id, data, tags)

        Returns:
            embeddings vector
        """

        # Prepare input document for transformers model and build embeddings
        return self.encode([self.prepare(document[1])])[0]

    def batch(self, documents, output):
        """
        Builds a batch of embeddings.

        Args:
            documents: list of documents used to build embeddings
            output: output temp file to store embeddings

        Returns:
            (ids, dimensions) list of ids and number of dimensions in embeddings
        """

        # Extract ids and prepare input documents for transformers model
        ids = [uid for uid, _, _ in documents]
        documents = [self.prepare(data) for _, data, _ in documents]
        dimensions = None

        # Build embeddings
        embeddings = self.encode(documents)
        if embeddings is not None:
            dimensions = embeddings.shape[1]
            pickle.dump(embeddings, output, protocol=4)

        return (ids, dimensions)

    def prepare(self, data):
        """
        Prepares input data for vector model.

        Args:
            data: input data

        Returns:
            data formatted for vector model
        """

        return data
