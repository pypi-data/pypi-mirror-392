from __future__ import annotations

import logging
import random
from typing import Callable, Dict, Tuple, Union

import cv2
import numpy as np
import torch
import torchvision.transforms.functional as F
import torchvision.transforms.v2 as v2
from PIL import Image
from torchvision.transforms import ColorJitter, InterpolationMode

try:
    import kornia.morphology as _kmorph
except ModuleNotFoundError:
    _kmorph = None

_Image = Union[Image.Image, torch.Tensor, np.ndarray]


_AUG_RNG = random.Random()


# Constants for RandStain transformation
randstain_constants = {
    "bach": {
        "L": {
            "avg": {"mean": 176.212, "std": 13.677, "distribution": "laplace"},
            "std": {"mean": 38.368, "std": 8.739, "distribution": "laplace"},
        },
        "A": {
            "avg": {"mean": 150.281, "std": 8.22, "distribution": "laplace"},
            "std": {"mean": 10.942, "std": 3.087, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 101.909, "std": 8.559, "distribution": "laplace"},
            "std": {"mean": 12.358, "std": 3.998, "distribution": "laplace"},
        },
    },
    "ccrcc": {
        "L": {
            "avg": {"mean": 162.086, "std": 23.691, "distribution": "norm"},
            "std": {"mean": 45.72, "std": 9.992, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 152.298, "std": 7.65, "distribution": "norm"},
            "std": {"mean": 10.916, "std": 2.58, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 117.695, "std": 4.044, "distribution": "norm"},
            "std": {"mean": 9.185, "std": 1.973, "distribution": "norm"},
        },
    },
    "crc": {
        "L": {
            "avg": {"mean": 160.658, "std": 28.507, "distribution": "laplace"},
            "std": {"mean": 35.602, "std": 12.938, "distribution": "laplace"},
        },
        "A": {
            "avg": {"mean": 155.721, "std": 8.59, "distribution": "laplace"},
            "std": {"mean": 8.644, "std": 3.222, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 113.101, "std": 4.914, "distribution": "laplace"},
            "std": {"mean": 5.326, "std": 1.834, "distribution": "laplace"},
        },
    },
    "esca": {
        "L": {
            "avg": {"mean": 162.977, "std": 28.455, "distribution": "laplace"},
            "std": {"mean": 38.103, "std": 9.602, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 153.457, "std": 10.034, "distribution": "laplace"},
            "std": {"mean": 9.525, "std": 3.285, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 112.414, "std": 7.494, "distribution": "norm"},
            "std": {"mean": 5.663, "std": 1.883, "distribution": "norm"},
        },
    },
    "patch_camelyon": {
        "L": {
            "avg": {"mean": 157.616, "std": 40.322, "distribution": "norm"},
            "std": {"mean": 47.41, "std": 12.984, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 151.256, "std": 10.978, "distribution": "norm"},
            "std": {"mean": 7.997, "std": 3.214, "distribution": "laplace"},
        },
        "B": {
            "avg": {"mean": 113.587, "std": 12.046, "distribution": "laplace"},
            "std": {"mean": 6.327, "std": 2.779, "distribution": "laplace"},
        },
    },
    "tcga_crc_msi": {
        "L": {
            "avg": {"mean": 157.412, "std": 17.274, "distribution": "norm"},
            "std": {"mean": 41.626, "std": 8.558, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 155.497, "std": 4.807, "distribution": "norm"},
            "std": {"mean": 8.973, "std": 2.735, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 113.043, "std": 4.678, "distribution": "laplace"},
            "std": {"mean": 5.587, "std": 1.552, "distribution": "laplace"},
        },
    },
    "tcga_tils": {
        "L": {
            "avg": {"mean": 159.268, "std": 33.309, "distribution": "norm"},
            "std": {"mean": 40.325, "std": 12.098, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 151.63, "std": 9.875, "distribution": "norm"},
            "std": {"mean": 8.519, "std": 3.292, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 117.799, "std": 6.768, "distribution": "norm"},
            "std": {"mean": 7.612, "std": 2.546, "distribution": "laplace"},
        },
    },
    "tcga_uniform": {
        "L": {
            "avg": {"mean": 140.328, "std": 26.043, "distribution": "norm"},
            "std": {"mean": 42.271, "std": 8.964, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 156.3, "std": 7.71, "distribution": "norm"},
            "std": {"mean": 7.451, "std": 2.719, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 114.37, "std": 5.652, "distribution": "norm"},
            "std": {"mean": 5.814, "std": 1.605, "distribution": "norm"},
        },
    },
    "wilds": {
        "L": {
            "avg": {"mean": 169.551, "std": 32.673, "distribution": "norm"},
            "std": {"mean": 34.248, "std": 11.67, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 148.907, "std": 7.386, "distribution": "norm"},
            "std": {"mean": 6.937, "std": 2.683, "distribution": "laplace"},
        },
        "B": {
            "avg": {"mean": 116.235, "std": 5.245, "distribution": "laplace"},
            "std": {"mean": 5.577, "std": 1.418, "distribution": "norm"},
        },
    },
    "break_his": {
        "L": {
            "avg": {"mean": 184.174, "std": 15.589, "distribution": "laplace"},
            "std": {"mean": 25.219, "std": 7.311, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 149.7, "std": 12.966, "distribution": "laplace"},
            "std": {"mean": 7.763, "std": 3.242, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 116.526, "std": 7.479, "distribution": "laplace"},
            "std": {"mean": 5.346, "std": 1.618, "distribution": "norm"},
        },
    },
    "mhist": {
        "L": {
            "avg": {"mean": 179.178, "std": 16.974, "distribution": "norm"},
            "std": {"mean": 51.886, "std": 5.499, "distribution": "norm"},
        },
        "A": {
            "avg": {"mean": 142.941, "std": 4.153, "distribution": "norm"},
            "std": {"mean": 9.835, "std": 1.666, "distribution": "norm"},
        },
        "B": {
            "avg": {"mean": 114.176, "std": 3.819, "distribution": "norm"},
            "std": {"mean": 9.391, "std": 1.522, "distribution": "norm"},
        },
    },
}


def set_transform_seed(seed: int) -> None:
    """
    Seed only the augmentation RNG.  Call this once per‐dataset before you apply any of the get_invariance_transforms().
    :param seed: an integer seed value.
    """
    _AUG_RNG.seed(seed)
    global _AUG_SEED
    _AUG_SEED = seed


def get_transform_seed() -> int | None:
    """
    Get the seed (for debugging)
    """
    return _AUG_SEED


def _to_tensor(img: _Image) -> torch.Tensor:
    """
    Converting image to float tensor in [0, 1] while preserving contents.

    :param img: input image (PIL, Tensor or ndarray).
    :return: tensor representation of image.
    """
    if isinstance(img, torch.Tensor):
        t = img.clone()
        if t.dtype == torch.uint8:
            t = t.float() / 255.0
        return t
    if isinstance(img, Image.Image):
        return F.to_tensor(img)
    arr = img
    if arr.dtype == np.uint8:
        arr = arr.astype(np.float32) / 255.0
    t = torch.from_numpy(arr)
    if t.shape[-1] in (1, 3):
        t = t.permute(2, 0, 1)
    return t


def _from_tensor(t: torch.Tensor, ref: _Image) -> _Image:
    """
    Returning tensor in the same container type as reference image (PIL, Tensor or ndarray).

    :param t: tensor to convert.
    :param ref: reference image for output type.
    :return: output image.
    """
    t_clamped = t.clamp(0.0, 1.0)
    if isinstance(ref, torch.Tensor):
        if ref.dtype == torch.uint8:
            return (t_clamped * 255).to(torch.uint8)
        return t_clamped
    if isinstance(ref, Image.Image):
        return F.to_pil_image(t_clamped)
    arr = t_clamped.permute(1, 2, 0).cpu().numpy()
    if ref.dtype == np.uint8:
        return (arr * 255).astype(np.uint8)
    return arr


def _identity(img: _Image) -> Tuple[_Image, _ParamDict]:
    """
    Identity transform (no change).

    :param img: input image.
    :return: same input image.
    """
    return img, {}


def _random_flip(p: float = 0.5) -> Callable[[_Image], _Image]:
    """
    Randomly flip image horizontally or vertically with probability p.

    :param p: flip probability.
    :return: flip transform.
    """

    def _inner(img: _Image):
        horizontal = _AUG_RNG.random() < p
        out = F.hflip(img) if horizontal else F.vflip(img)
        return out, {"orientation": "horizontal" if horizontal else "vertical"}

    return _inner


def _random_rotate() -> Callable[[_Image], _Image]:
    """
    Random rotation by 90°, 180°, or 270°.

    :return: rotation transform.
    """

    def _inner(img: _Image):
        angle = _AUG_RNG.randint(1, 3) * 90
        return (
            F.rotate(img, angle, InterpolationMode.BILINEAR, expand=True),
            {"angle": angle},
        )

    return _inner


def _random_translate(max_frac: float = 0.20) -> Callable[[_Image], _Image]:
    """
    Random translation, scale, and shear transform.

    :param max_frac: maximum fraction for translation and scaling.
    :return: affine transform.
    """

    def _inner(img: _Image):
        if isinstance(img, Image.Image):
            w, h = img.size
        elif isinstance(img, torch.Tensor):
            _, h, w = img.shape
        else:
            h, w = img.shape[:2]
        dx = int(_AUG_RNG.uniform(-max_frac, max_frac) * w)
        dy = int(_AUG_RNG.uniform(-max_frac, max_frac) * h)
        scale = 1.0 + _AUG_RNG.uniform(-max_frac, max_frac)
        shear = _AUG_RNG.uniform(-max_frac * 10 / 2, max_frac * 10 / 2)
        out = F.affine(
            img,
            angle=0.0,
            translate=(dx, dy),
            scale=scale,
            shear=shear,
            interpolation=InterpolationMode.BILINEAR,
        )
        return out, {"dx": dx, "dy": dy, "scale": scale, "shear": shear}

    return _inner


def _random_gaussian_blur(kernel_size: int = 15) -> Callable[[_Image], _Image]:
    """
    Applying Gaussian blur with fixed kernel size.

    :param kernel_size: size of the Gaussian kernel.
    :return: blur transform.
    """

    def _inner(img: _Image):
        return F.gaussian_blur(img, kernel_size=kernel_size), {
            "kernel_size": kernel_size
        }

    return _inner


def _random_color_jitter(
    brightness: float = 0.5,
    contrast: float = 0.5,
    saturation: float = 0.5,
    hue: float = 0.35,
) -> Callable[[_Image], _Image]:
    """
    Randomly adjusts brightness, contrast, saturation, and hue within specified max ranges.

    :param brightness: Max brightness jitter factor.
    :param contrast: Max contrast jitter factor.
    :param saturation: Max saturation jitter factor.
    :param hue: Max hue jitter factor
    :return: Color jitter transform.
    """

    def _sample_factor(max_delta: float) -> float:
        return _AUG_RNG.uniform(max(0, 1.0 - max_delta), 1.0 + max_delta)

    def _inner(img: _Image):
        bf = _sample_factor(brightness)
        cf = _sample_factor(contrast)
        sf = _sample_factor(saturation)
        hf = _AUG_RNG.uniform(-hue, hue)

        out = F.adjust_brightness(img, bf)
        out = F.adjust_contrast(out, cf)
        out = F.adjust_saturation(out, sf)
        out = F.adjust_hue(out, hf)

        return out, {
            "brightness_factor": bf,
            "contrast_factor": cf,
            "saturation_factor": sf,
            "hue_factor": hf,
        }

    return _inner


def _random_gamma(
    gamma_range: Tuple[float, float] = (-0.5, 0.5)
) -> Callable[[_Image], _Image]:
    """
    Random gamma adjustment: gamma is sampled in [1 + min, 1 + max] = [0.5, 1.5].

    :param gamma_range: range for additive gamma sampling (e.g., [-0.5, 0.5]).
    :return: gamma adjustment transform.
    """

    def _inner(img: _Image):
        gamma = 1 + _AUG_RNG.uniform(*gamma_range)
        return F.adjust_gamma(img, gamma=gamma, gain=1.0), {"gamma": gamma}

    return _inner


def _random_hed(sigma: float = 0.025) -> Callable[[_Image], _Image]:
    """
    Applying HED-shift augmentation to an image.

    HED augmentation method as described in:
    [1] Faryna, K., Van der Laak, J., Litjens, G., 2021. Tailoring automated data augmentation to H&E-stained histopathology.
    In Medical Imaging with Deep Learning.

    :param sigma: standard deviation for perturbations in HED space.
    :return: HED augmentation transform.
    """

    def _inner(img: _Image):
        M = torch.tensor(
            np.array(
                [[0.65, 0.70, 0.29], [0.07, 0.99, 0.11], [0.27, 0.57, 0.78]],
                dtype="float32",
            )
        )
        RGB2HED = torch.linalg.inv(M)

        # Handle input type
        if isinstance(img, Image.Image):
            # Convert PIL Image to tensor
            img = F.to_tensor(img)
            is_pil = True  # Flag to check if input was a PIL image
        elif isinstance(img, torch.Tensor):
            if img.dim() != 3:
                raise ValueError("Input tensor must have shape C x H x W.")
            is_pil = False
        else:
            raise TypeError("Input must be a PIL Image or a PyTorch tensor.")

        epsilon = 3.14159
        C, X, Y = img.shape  # Remove batch dimension

        # Reshape image P \in R^(N,3)
        P = img.reshape(C, -1).movedim(0, -1)  # Move channel to the last dimension

        # HED images
        S = torch.matmul(-torch.log(P + epsilon), RGB2HED)

        # Channel-wise perturbations
        alpha = torch.normal(mean=1, std=sigma, size=[1, 3])  # Change B to 1
        beta = torch.normal(mean=0, std=sigma, size=[1, 3])  # Change B to 1
        Shat = alpha * S + beta

        # Augmented RGB images
        Phat = torch.exp(-torch.matmul(Shat, M)) - epsilon

        # Clip values to range [0, 255]
        Phat_clipped = torch.clip(Phat, min=0.0, max=1.0)

        out = Phat_clipped.movedim(-1, 0).reshape(
            C, X, Y
        )  # Move channel back to the first dimension

        out = F.to_pil_image(out) if is_pil else out

        # Return the output in the same format as input
        return out, {
            "alpha": alpha.squeeze().tolist(),
            "beta": beta.squeeze().tolist(),
            "sigma": sigma,
        }

    return _inner


def _random_cutout(max_mask_frac: float = 0.50) -> Callable[[_Image], _Image]:
    """
    Applying a random square cutout covering up to max fraction of min(H, W).

    :param max_mask_frac: maximum mask size fraction.
    :return: cutout transform.
    """

    def _inner(img: _Image):
        tensor = _to_tensor(img)
        _, h, w = tensor.shape
        size = int(_AUG_RNG.uniform(0.10, max_mask_frac) * min(h, w))
        top = _AUG_RNG.randint(0, h - size)
        left = _AUG_RNG.randint(0, w - size)
        tensor[:, top : top + size, left : left + size] = 0.0
        out = _from_tensor(tensor, img)
        return out, {
            "size": size,
            "top": top,
            "left": left,
            "mask_frac": max_mask_frac,
        }

    return _inner


def _random_dilation(max_kernel: int = 5) -> Callable[[_Image], _Image]:
    """
    Random dilation with square kernel of random size.

    :param max_kernel: maximum kernel size.
    :return: dilation transform.
    """
    if _kmorph is None:
        raise ImportError(
            "kornia is required for the dilation transform; install via `pip install kornia`."
        )

    def _inner(img: _Image):
        t = _to_tensor(img).unsqueeze(0)
        k = _AUG_RNG.randint(2, max_kernel)
        if k % 2 == 0:
            k += 1
        kernel = torch.ones((k, k), device=t.device)
        out = _kmorph.dilation(t, kernel).squeeze(0)
        return _from_tensor(out, img), {"kernel_size": k}

    return _inner


def _random_erosion(max_kernel: int = 5) -> Callable[[_Image], _Image]:
    """
    Random erosion with square kernel of random size.

    :param max_kernel: maximum kernel size.
    :return: erosion transform.
    """
    if _kmorph is None:
        raise ImportError(
            "kornia is required for the erosion transform; install via `pip install kornia`."
        )

    def _inner(img: _Image):
        t = _to_tensor(img).unsqueeze(0)
        k = _AUG_RNG.randint(2, max_kernel)
        if k % 2 == 0:
            k += 1
        kernel = torch.ones((k, k), device=t.device)
        out = _kmorph.erosion(t, kernel).squeeze(0)
        return _from_tensor(out, img), {"kernel_size": k}

    return _inner


def _random_opening(max_kernel: int = 5) -> Callable[[_Image], _Image]:
    """
    Random opening with square kernel of random size.

    :param max_kernel: maximum kernel size.
    :return: opening transform.
    """
    if _kmorph is None:
        raise ImportError(
            "kornia is required for the opening transform; install via `pip install kornia`."
        )

    def _inner(img: _Image):
        t = _to_tensor(img).unsqueeze(0)
        k = _AUG_RNG.randint(2, max_kernel)
        if k % 2 == 0:
            k += 1
        kernel = torch.ones((k, k), device=t.device)
        out = _kmorph.opening(t, kernel).squeeze(0)
        return _from_tensor(out, img), {"kernel_size": k}

    return _inner


def _five_crop_random():
    """
    Choose one of torchvision’s 5 standard crops (4 corners + center).

    Returns (cropped_img, {"crop_id": 1‑5, "size": size})
    """

    def _inner(img):
        # 5‑tuple of (TL, TR, BL, BR, center)
        width, height = img.size
        size = min(width, height) // 2
        crops = F.five_crop(img, size)
        crop_id = _AUG_RNG.randint(0, 4)  # 1‑based like your example
        out = crops[crop_id]  # replicate `img = img[param-1]`
        return out, {"crop_id": crop_id, "size": size}

    return _inner


def _random_closing(max_kernel: int = 5) -> Callable[[_Image], _Image]:
    """
    Random closing with square kernel of random size.

    :param max_kernel: maximum kernel size.
    :return: closing transform.
    """
    if _kmorph is None:
        raise ImportError(
            "kornia is required for the closing transform; install via `pip install kornia`."
        )

    def _inner(img: _Image):
        t = _to_tensor(img).unsqueeze(0)
        k = _AUG_RNG.randint(2, max_kernel)
        if k % 2 == 0:
            k += 1
        kernel = torch.ones((k, k), device=t.device)
        out = _kmorph.closing(t, kernel).squeeze(0)
        return _from_tensor(out, img), {"kernel_size": k}

    return _inner


def _elastic_transform(alpha: float = 250.0, sigma: float = 6.0):
    """
    Wraps torchvision.v2.ElasticTransform so it fits (img)->(img,params).
    alpha: magnitude; sigma: Gaussian smoothing of displacement field.
    """
    transform = v2.ElasticTransform(alpha=alpha, sigma=sigma)

    def _inner(img):
        out = transform(img)
        return out, {"alpha": alpha, "sigma": sigma}

    return _inner


def _random_randstain(
    dataset_name: str, std_hyper: float = -0.3
) -> Callable[[_Image], Tuple[_Image, Dict]]:
    """
    RandStain transformation.
    Code inspired from https://github.com/yiqings/RandStainNA/blob/master/randstainna.py
    """

    stats = randstain_constants[dataset_name]

    def _inner(img: _Image) -> Tuple[_Image, Dict]:

        rng_seed = _AUG_RNG.randint(0, 2**20 - 1)
        rng = np.random.RandomState(rng_seed)

        if isinstance(img, Image.Image):
            rgb = np.array(img)
            if rgb.dtype != np.uint8:
                rgb = np.clip(rgb, 0, 255).astype(np.uint8)
            container = "pil"
        elif isinstance(img, torch.Tensor):
            t = _to_tensor(img)
            rgb = (
                (t.permute(1, 2, 0).cpu().numpy() * 255.0)
                .round()
                .clip(0, 255)
                .astype(np.uint8)
            )
            container = "tensor"
        elif isinstance(img, np.ndarray):
            rgb = img
            if rgb.dtype != np.uint8:
                if rgb.max() <= 1.0 + 1e-6:
                    rgb = rgb * 255.0
                rgb = np.round(rgb).clip(0, 255).astype(np.uint8)
            container = "ndarray"
        else:
            raise TypeError(
                "Unsupported image type; expected PIL.Image, torch.Tensor, or np.ndarray."
            )

        # ---- RGB -> LAB ----
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

        flat = lab.reshape(-1, 3)
        img_avgs = flat.mean(axis=0)
        img_stds = flat.std(axis=0)
        img_stds = np.clip(img_stds, 1e-4, 255.0)

        # ---- sample target avgs/stds per channel (L, A, B) ----
        tar_avgs = []
        tar_stds = []
        sampled = {}
        for i, ch in enumerate(("L", "A", "B")):
            ch_stats = stats[ch]
            # avg
            loc_avg = ch_stats["avg"]["mean"]
            scale_avg = ch_stats["avg"]["std"] * (1.0 + std_hyper)
            dist_avg = ch_stats["avg"]["distribution"].lower()
            if dist_avg in ("norm", "normal"):
                tavg = float(rng.normal(loc=loc_avg, scale=max(1e-8, scale_avg)))
            else:
                tavg = float(rng.laplace(loc=loc_avg, scale=max(1e-8, scale_avg)))
            # std
            loc_std = ch_stats["std"]["mean"]
            scale_std = ch_stats["std"]["std"] * (1.0 + std_hyper)
            dist_std = ch_stats["std"]["distribution"].lower()
            if dist_std in ("norm", "normal"):
                tstd = float(rng.normal(loc=loc_std, scale=max(1e-8, scale_std)))
            else:
                tstd = float(rng.laplace(loc=loc_std, scale=max(1e-8, scale_std)))
            tstd = max(1e-4, tstd)

            tar_avgs.append(tavg)
            tar_stds.append(tstd)
            sampled[ch] = {
                "target_avg": tavg,
                "target_std": tstd,
                "avg_loc": loc_avg,
                "avg_scale": scale_avg,
                "avg_dist": dist_avg,
                "std_loc": loc_std,
                "std_scale": scale_std,
                "std_dist": dist_std,
            }

        tar_avgs = np.array(tar_avgs, dtype=np.float32)
        tar_stds = np.array(tar_stds, dtype=np.float32)

        out_lab = (lab - img_avgs) * (tar_stds / img_stds) + tar_avgs
        out_lab = np.clip(out_lab, 0.0, 255.0).astype(np.uint8)

        # ---- LAB -> RGB ----
        out_rgb = cv2.cvtColor(out_lab, cv2.COLOR_LAB2RGB)

        if container == "pil":
            out = Image.fromarray(out_rgb)
        elif container == "tensor":
            t = torch.from_numpy(out_rgb).permute(2, 0, 1).float() / 255.0
            out = _from_tensor(t, img)  # use existing to match dtype
        else:  # ndarray
            if isinstance(img, np.ndarray) and img.dtype != np.uint8:
                out = (out_rgb.astype(np.float32) / 255.0).astype(img.dtype)
            else:
                out = out_rgb

        params = {
            "seed": rng_seed,
            "sampled": sampled,
        }
        return out, params

    return _inner


def get_invariance_transforms(
    dataset_name: str,
) -> Dict[str, Callable[[_Image], _Image]]:
    """
    Getting dictionary of available data augmentation transformations.

    :return: dictionary {name: transform callable}.
    """
    transforms_dict = {
        "identity": _identity,
        "random_flip": _random_flip(),
        "random_rotate": _random_rotate(),
        "random_translate": _random_translate(),
        "random_gaussian_blur": _random_gaussian_blur(),
        "random_color_jitter": _random_color_jitter(),
        "random_gamma": _random_gamma(),
        "random_hed": _random_hed(),
        "random_cutout": _random_cutout(),
        "random_dilation": _random_dilation(),
        "random_erosion": _random_erosion(),
        "random_opening": _random_opening(),
        "random_closing": _random_closing(),
        "five_crop": _five_crop_random(),
        "elastic_transform": _elastic_transform(),
    }

    if dataset_name not in randstain_constants:
        logging.info(
            f"RandStain transformation: Unknown dataset_name '{dataset_name}'. "
            f"Available: {list(randstain_constants.keys())}. "
            f"RandStain is not implemented for custom datasets (as it requires pre-computed dataset-specific statistics)."
        )
    else:
        transforms_dict["random_randstain"] = _random_randstain(dataset_name)

    return transforms_dict


__all__ = ["get_invariance_transforms"]
