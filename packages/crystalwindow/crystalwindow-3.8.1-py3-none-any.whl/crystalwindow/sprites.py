# sprites.py
from tkinter import PhotoImage
from PIL import Image, ImageTk


class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        self.x, self.y = pos
        self.pos = pos

        self.image = None
        self.color = color

        # If fallback dict provided from assets
        if isinstance(image, dict) and image.get("fallback"):
            self.width, self.height = image["size"]
            self.color = image["color"]

        # Normal image
        elif isinstance(image, PhotoImage):
            self.set_image(image)

        # Rectangle sprite
        elif size is not None:
            self.width, self.height = size

        else:
            raise ValueError("Sprite needs 'size' or 'image'")

        # Movement physics
        self.vel_x = 0
        self.vel_y = 0

        # Optional direction flag
        self.facing_left = False

    # --------------------------------------
    # Constructors
    # --------------------------------------
    @classmethod
    def image(cls, img, pos):
        if isinstance(img, dict) and img.get("fallback"):
            w, h = img["size"]
            color = img["color"]
            return cls(pos, size=(w, h), color=color)
        return cls(pos, image=img)

    @classmethod
    def rect(cls, pos, w, h, color=(255, 0, 0)):
        return cls(pos, size=(w, h), color=color)

    # --------------------------------------
    # Draw
    # --------------------------------------
    def draw(self, win, cam=None):
        if cam:
            draw_x, draw_y = cam.apply(self)
        else:
            draw_x, draw_y = self.x, self.y

        if self.image:
            win.canvas.create_image(draw_x, draw_y, anchor="nw", image=self.image)
        else:
            win.draw_rect(self.color, (draw_x, draw_y, self.width, self.height))

    # --------------------------------------
    # Movement
    # --------------------------------------
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.pos = (self.x, self.y)

    def apply_velocity(self, dt=1):
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.pos = (self.x, self.y)

    # --------------------------------------
    # Image setter
    # --------------------------------------
    def set_image(self, new_image):
        """Set sprite image and update size."""
        self.image = new_image
        self.width = new_image.width()
        self.height = new_image.height()

    # --------------------------------------
    # In-place flipping (optional)
    # --------------------------------------
    def flip_horizontal(self):
        if not self.image:
            return
        pil = ImageTk.getimage(self.image)
        flipped = pil.transpose(Image.FLIP_LEFT_RIGHT)
        self.set_image(ImageTk.PhotoImage(flipped))
        self.facing_left = not self.facing_left

    def flip_vertical(self):
        if not self.image:
            return
        pil = ImageTk.getimage(self.image)
        flipped = pil.transpose(Image.FLIP_TOP_BOTTOM)
        self.set_image(ImageTk.PhotoImage(flipped))

    # --------------------------------------
    # Collision
    # --------------------------------------
    def colliderect(self, other):
        return (
            self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y
        )
