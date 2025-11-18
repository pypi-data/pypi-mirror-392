import os
import random
from tkinter import PhotoImage

try:
    from PIL import Image
except:
    Image = None

ASSETS = {}

def load_image(path):
    # try normal load
    if os.path.exists(path):
        try:
            img = PhotoImage(file=path)
            ASSETS[path] = img
            return img
        except:
            print(f"⚠️ Ops!, could not load img: {path}")
    else:
        print(f"⚠️ Ops!, file not found: {path}")

    # fallback: get natural size using PIL if possible
    if Image is not None:
        try:
            pil_img = Image.open(path)
            w, h = pil_img.size
        except:
            w, h = 64, 64
    else:
        w, h = 64, 64

    # RANDOM COLOR FALLBACK (chaos energy)
    rand_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

    return {
        "fallback": True,
        "size": (w, h),
        "color": rand_color
    }


def load_folder_images(folder, nested=True):
    if not os.path.exists(folder):
        print(f"⚠️ Ops!, folder not found: {folder}")
        return {}

    result = {}
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)

        if os.path.isdir(full_path) and nested:
            result[item] = load_folder_images(full_path, nested=True)

        elif item.lower().endswith((".png", ".gif")):
            result[item] = load_image(full_path)

    return result


def load_music(path):
    print(f"[assets] Music loading not supported in this crystalwindow ver, sorry! ~Crystal: {path}")
    return None


def play_music(loop=-1):
    print("[assets] Music playback not supported in this ver sorry! ~Crystal")
