# assets.py
import os
import random
from tkinter import PhotoImage

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

ASSETS = {}  # cache for all loaded images


# --------------------------------------------------------
# MAIN IMAGE LOADER
# --------------------------------------------------------
def load_image(path, flip_h=False, flip_v=False):
    """
    Loads an image and returns a Tk PhotoImage.
    Supports flipping using Pillow.
    """

    key = f"{path}|h={flip_h}|v={flip_v}"
    if key in ASSETS:
        return ASSETS[key]

    if not os.path.exists(path):
        print(f"⚠️ Missing file: {path}")
        img = generate_fallback(path)
        ASSETS[key] = img
        return img

    # If Pillow is missing → load normal image
    if Image is None or ImageTk is None:
        try:
            img = PhotoImage(file=path)
            ASSETS[key] = img
            return img
        except:
            fb = generate_fallback(path)
            ASSETS[key] = fb
            return fb

    # Load with PIL to allow flipping
    try:
        pil_img = Image.open(path)

        if flip_h:
            pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_v:
            pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)

        tk_img = ImageTk.PhotoImage(pil_img)
        ASSETS[key] = tk_img
        return tk_img

    except Exception as e:
        print(f"⚠️ Error loading {path}: {e}")
        fb = generate_fallback(path)
        ASSETS[key] = fb
        return fb


# --------------------------------------------------------
# FALLBACK NODE
# --------------------------------------------------------
def generate_fallback(path):
    """Fallback colored block used when an image is missing."""
    rand_color = (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255),
    )

    if Image:
        try:
            pil_img = Image.open(path)
            w, h = pil_img.size
        except:
            w, h = 64, 64
    else:
        w, h = 64, 64

    return {
        "fallback": True,
        "size": (w, h),
        "color": rand_color
    }


# --------------------------------------------------------
# PYGAME-STYLE FLIP HELPERS
# --------------------------------------------------------
def flip_image(img, flip_h=False, flip_v=False):
    """
    Returns a NEW flipped PhotoImage.
    Like pygame.transform.flip().
    """
    if Image is None or ImageTk is None:
        print("⚠️ Pillow not installed; cannot flip images.")
        return img

    pil_img = ImageTk.getimage(img)

    if flip_h:
        pil_img = pil_img.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)

    return ImageTk.PhotoImage(pil_img)


def flip_horizontal(img):
    return flip_image(img, flip_h=True)


def flip_vertical(img):
    return flip_image(img, flip_v=True)


# --------------------------------------------------------
# FOLDER LOADING
# --------------------------------------------------------
def load_folder_images(folder, nested=True):
    if not os.path.exists(folder):
        print(f"⚠️ Folder not found: {folder}")
        return {}

    result = {}
    for item in os.listdir(folder):
        full = os.path.join(folder, item)

        if os.path.isdir(full) and nested:
            result[item] = load_folder_images(full)

        elif item.lower().endswith((".png", ".gif")):
            result[item] = load_image(full)

    return result


# --------------------------------------------------------
# MUSIC PLACEHOLDER
# --------------------------------------------------------
def load_music(path):
    print(f"[assets] Music load not supported: {path}")

def play_music(loop=-1):
    print("[assets] Music playback not supported.")
