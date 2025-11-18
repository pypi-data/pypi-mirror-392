# sprites.py
import random
from tkinter import PhotoImage

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        """
        pos: (x, y)
        size: (w, h) optional
        image: PhotoImage or PIL ImageTk.PhotoImage
        color: fallback rectangle color
        """
        self.pos = pos
        self.x, self.y = pos
        self.image = image
        self.color = color

        # Determine width/height
        if image is not None:
            try:
                # Tkinter PhotoImage
                self.width = image.width()
                self.height = image.height()
            except Exception:
                try:
                    # PIL ImageTk.PhotoImage
                    self.width = image.width
                    self.height = image.height
                except Exception:
                    raise ValueError("Sprite image has no size info")
        elif size is not None:
            self.width, self.height = size
        else:
            raise ValueError("Sprite needs 'size' or 'image'")

        # Optional velocity
        self.vel_x = 0
        self.vel_y = 0

    # === CLASS METHODS ===
    @classmethod
    def image(cls, img, pos):
        """
        Create a sprite from an image.
        Accepts fallback dict or actual PhotoImage.
        """
        if isinstance(img, dict) and img.get("fallback"):
            w, h = img["size"]
            color = img["color"]
            return cls(pos, size=(w, h), color=color)
        return cls(pos, image=img)

    @classmethod
    def rect(cls, pos, w, h, color=(255, 0, 0)):
        """Create sprite using a plain colored rectangle"""
        return cls(pos, size=(w, h), color=color)

    # === METHODS ===
    def draw(self, win, cam=None):
        """Draw sprite on CrystalWindow / Tk canvas"""
        if cam:
            draw_x, draw_y = cam.apply(self)
        else:
            draw_x, draw_y = self.x, self.y

        if self.image:
            win.canvas.create_image(draw_x, draw_y, anchor="nw", image=self.image)
        else:
            win.draw_rect(self.color, (draw_x, draw_y, self.width, self.height))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.pos = (self.x, self.y)

    def apply_velocity(self, dt=1):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.pos = (self.x, self.y)

    def colliderect(self, other):
        return (
            self.x < other.x + getattr(other, "width", 0) and
            self.x + getattr(self, "width", 0) > other.x and
            self.y < other.y + getattr(other, "height", 0) and
            self.y + getattr(self, "height", 0) > other.y
        )  # returns tuple for consistency

    def set_image(self, img):
        """Update sprite's image at runtime (like flipping)"""
        self.image = img
        # update width/height
        if img is not None:
            try:
                self.width = img.width()
                self.height = img.height()
            except Exception:
                try:
                    self.width = img.width
                    self.height = img.height
                except:
                    pass
