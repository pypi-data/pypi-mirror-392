import os
from collections.abc import Callable
from contextlib import nullcontext

import h5py
import numpy as np
import torch
from omegaconf import DictConfig
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm
from transformers.models.vit.modeling_vit import ViTModel

from ..models.pretrained_models import load_pretrained_model
from ..utils.data import PatchDataset, get_data


def pre_computing_patch_embeddings(
    cfg: DictConfig,
    embeddings_folder: str,
    device: str,
    dataset_name: str,
    base_data_folder: str,
    data_compatible_tasks: list,
    adaptation_type: str,
    base_embeddings_folder: str,
    model_name: str,
    image_pre_loading: str,
    embedding_pre_loading: str,
    model_cls: Callable = None,
) -> None:
    """
    Pre-computing embeddings for each patch in a given dataset with a given pre-trained model.

    :param cfg: config defining the job to run.
    :param embeddings_folder: folder where to store computed embeddings.
    :param device: device to use (cpu, cuda).
    :param dataset_name: name of the dataset.
    :param base_data_folder: base folder storing data.
    :param data_compatible_tasks: list of tasks compatible with the dataset.
    :param adaptation_type: type of adaptation to use (frozen, lora).
    :param base_embeddings_folder: base folder storing embeddings.
    :param model_name: name of the pretrained model.
    :param image_pre_loading: whether to pre-load images in dataloader.
    :param embedding_pre_loading: whether to pre-load embeddings in dataloader.
    """
    # Loading data
    data = get_data(
        (
            dataset_name
            if not hasattr(cfg.dataset, "data_splits")
            else cfg.dataset.data_splits
        ),
        base_data_folder,
    )

    # Loading pretrained model
    if model_cls is not None:
        pretrained_model = model_cls
        transform = model_cls.get_transform()
        extract_embedding = model_cls.get_embeddings
        pretrained_model.to(device)
    else:
        pretrained_model, transform, extract_embedding = load_pretrained_model(
            cfg, adaptation_type, device
        )
    pretrained_model.eval()

    # Pre-computing (and saving) embeddings
    if "linear_probing" in data_compatible_tasks:
        dataset_task_type = "linear_probing"
    else:
        dataset_task_type = "segmentation"
    for split in ["train", "val", "test"]:
        split_dataset = PatchDataset(
            data[split]["images"],
            data[split]["labels"],
            transform,
            dataset_task_type,
            dataset_name,
            base_data_folder,
            os.path.join(base_embeddings_folder, dataset_name, model_name, split),
            image_pre_loading,
            embedding_pre_loading,
            hasattr(cfg.dataset, "div_patches") and cfg.dataset.div_patches,
            h5_format=(
                cfg.dataset.h5_format if hasattr(cfg.dataset, "h5_format") else False
            ),
        )
        split_dataloader = DataLoader(
            split_dataset,
            batch_size=cfg.task.pre_comp_emb_batch_size,
            shuffle=False,
            num_workers=1,
        )
        pre_computing_patch_embeddings_split(
            os.path.join(embeddings_folder, split),
            split_dataloader,
            pretrained_model,
            extract_embedding,
            dataset_task_type,
            device,
            id2classnames=(
                dict(cfg.dataset.id_to_classname)
                if dataset_task_type == "linear_probing"
                and (
                    cfg.pretrained_model.vlm
                    if model_cls is None
                    else pretrained_model.vlm
                )
                and split == "test"
                else None
            ),
            div_patches=hasattr(cfg.dataset, "div_patches") and cfg.dataset.div_patches,
        )


@torch.inference_mode()
def pre_computing_patch_embeddings_split(
    embeddings_folder: str,
    dataloader: DataLoader,
    pretrained_model: ViTModel,
    extract_embedding: Callable[[torch.Tensor, ViTModel, str], torch.Tensor],
    task_type: str,
    device: torch.device | str = "cuda",
    id2classnames: dict = None,
    div_patches: bool = False,
) -> None:
    """
    Pre-computing embeddings for each patch in a split of a given dataset with a given pre-trained model.

    :param embeddings_folder: folder where to store computed embeddings.
    :param dataloader: dataloader to load data batches.
    :param pretrained_model: pretrained model to use.
    :param extract_embedding: function to extract an embedding vector from an input image with the pretrained model.
    :param task_type: type of task to extract emebddings for (classification, segmentation).
    :param device: device to use (cpu, cuda).
    :param id2classnames: mapping from class ids to text labels.
    :param div_patches: whether to divide image into patches (instead of using full image).
    """
    os.makedirs(embeddings_folder, exist_ok=True)
    emb_path = os.path.join(embeddings_folder, "embeddings.h5")
    text_aligned_emb_path = os.path.join(
        embeddings_folder, "text_aligned_embeddings.h5"
    )
    label_path = os.path.join(embeddings_folder, "labels.h5")

    # Open / create the files once.
    with (
        h5py.File(emb_path, "a", libver="latest") as emb_h5,
        h5py.File(label_path, "a", libver="latest") as lab_h5,
        (
            h5py.File(text_aligned_emb_path, "a", libver="latest")
            if id2classnames is not None
            else nullcontext()
        ) as text_aligned_emb_h5,
    ):
        next_idx = max((int(k) for k in emb_h5.keys()), default=-1) + 1

        for batch in tqdm(dataloader, desc="Extracting patch embeddings"):
            imgs = batch["image"].to(device, non_blocking=True)
            labels = batch["label"].to(device, non_blocking=True)

            if div_patches:
                # Re-shaping and masking
                bs, nb_patches, c, h, w = imgs.shape
                masks = imgs.sum(dim=[2, 3, 4]) != 0
                imgs = imgs.view(-1, c, h, w)

            embeds = extract_embedding(imgs, pretrained_model, task_type=task_type)

            if div_patches:
                # Mean pooling
                embeds = embeds.view(bs, nb_patches, embeds.shape[-1])
                masks = masks.unsqueeze(-1)
                masks = masks.repeat(1, 1, embeds.shape[-1])
                embeds = (masks * embeds).sum(dim=1) / masks.sum(dim=1)

            embeds = embeds.cpu().numpy().astype(np.float32, copy=False)
            labels = labels.cpu().numpy().astype(np.int64, copy=False)

            # Text-aligned embeddings (VLM)
            if text_aligned_emb_h5 is not None:
                text_aligned_embeds = extract_embedding(
                    imgs,
                    pretrained_model,
                    task_type=task_type,
                    text_aligned_im_emb=True,
                )
                text_aligned_embeds = (
                    text_aligned_embeds.cpu().numpy().astype(np.float32, copy=False)
                )

            bs = embeds.shape[0]
            for i in range(bs):
                key = f"{next_idx + i}"

                emb_h5.create_dataset(
                    key,
                    data=embeds[i],
                    dtype="float32",
                )
                if text_aligned_emb_h5 is not None:
                    text_aligned_emb_h5.create_dataset(
                        key,
                        data=text_aligned_embeds[i],
                        dtype="float32",
                    )
                lab_h5.create_dataset(
                    key,
                    data=labels[i],
                    dtype="int64",
                )

            next_idx += bs

    # Zero-shot image-text embeddings
    if id2classnames is not None:
        from ..utils.constants import UtilsConstants

        text_emb_path = os.path.join(embeddings_folder, "text_embeddings.h5")
        with h5py.File(text_emb_path, "a", libver="latest") as text_emb_h5:
            next_idx = max((int(k) for k in text_emb_h5.keys()), default=-1) + 1
            nb_classes = len(list(id2classnames.keys()))
            for i in range(nb_classes):
                classname = id2classnames[i]
                text_prompts = [
                    template.replace("CLASSNAME", classname)
                    for template in UtilsConstants.VLM_TEMPLATES.value
                ]
                text_embeds = extract_embedding(
                    text_prompts, pretrained_model, task_type=task_type, text_emb=True
                )
                text_embed = text_embeds.mean(dim=0)
                text_embed = text_embed.cpu().numpy().astype(np.float32, copy=False)

                key = f"{i}"
                text_emb_h5.create_dataset(
                    key,
                    data=text_embed,
                    dtype="float32",
                )
