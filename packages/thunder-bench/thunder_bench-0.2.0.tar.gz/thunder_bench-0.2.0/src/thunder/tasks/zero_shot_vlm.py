import json
import logging
import os

import numpy as np

from ..tasks.image_retrieval import topk_retrieval
from ..utils.utils import log_metrics, save_outputs


def zero_shot_vlm(
    image_embs: np.array,
    text_embs: np.array,
    labels: np.array,
    res_folder: str,
    wandb_base_folder: str,
) -> None:
    """
    Performing zero-shot VLM classification.
    :param image_embs: test image embeddings.
    :param text_embs: classname embeddings.
    :param labels: ground-truth labels.
    :param res_folder: folder to save results.
    :param wandb_base_folder: w&b folder.
    """

    test_metrics, *_ = topk_retrieval(
        text_embs,
        np.arange(text_embs.shape[0]),
        image_embs,
        labels,
        [1],
    )

    # Logging
    log_metrics(wandb_base_folder, test_metrics[1], "test", step=1)
    save_outputs(res_folder, test_metrics)
