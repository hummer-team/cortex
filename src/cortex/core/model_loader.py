from cortex.logger.logger import get_logger
import gc
import torch

log = get_logger(__name__)

# Note: The embedding model is now managed by ChromaDB's SentenceTransformerEmbeddingFunction.
# This file is kept for potential future use, such as managing other types of models
# or implementing more complex model release logic if needed.


def release_all_models():
    """
    A general-purpose function to release model memory.
    Currently, it focuses on clearing CUDA cache if available.
    """
    log.info("Attempting to release model memory...")
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        log.info("CUDA cache cleared.")
    log.info("Memory release process complete.")
