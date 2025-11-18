import random
from tkinter import PhotoImage

class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        """
        pos: (x, y)
        size: (w, h) optional
        image: PhotoImage (Tkinter)
        color: fill color if no image
        """
        self.pos = pos
        self.x, self.y = pos
        self.image = image
        self.color = color

        if image is not None:
            self.width = image.width()
            self.height = image.height()
        elif size is not None:
            self.width, self.height = size
        else:
            raise ValueError("Sprite needs either 'size' or 'image'")

        # optional velocity fields for physics
        self.vel_x = 0
        self.vel_y = 0

    # === CLASS METHODS ===
    @classmethod
    def image(cls, img, pos):
        # fallback if img is missing
        if isinstance(img, dict) and img.get("fallback"):
            print("⚠️ Missing image, making RANDOM rect fallback.")
            w, h = img["size"]
            color = img["color"]
            return cls.rect(pos, w, h, color=color)
        return cls(pos, image=img)

    @classmethod
    def rect(cls, pos, w, h, color=(255, 0, 0)):
        """Create sprite using a plain colored rectangle"""
        return cls(pos, size=(w, h), color=color)

    # === METHODS ===
    def draw(self, win, cam=None):
        """Draw sprite on a CrystalWindow or Tkinter canvas"""
        if cam:
            draw_x, draw_y = cam.apply(self)
        else:
            draw_x, draw_y = self.x, self.y

        if self.image:
            win.canvas.create_image(draw_x, draw_y, anchor="nw", image=self.image)
        else:
            win.draw_rect(self.color, (draw_x, draw_y, self.width, self.height))

    def move(self, dx, dy):
        """Move sprite manually by dx/dy"""
        self.x += dx
        self.y += dy
        self.pos = (self.x, self.y)

    def apply_velocity(self, dt=1):
        """Apply vel_x/vel_y to x/y for physics"""
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.pos = (self.x, self.y)

    # === COLLISION ===
    def colliderect(self, other):
        """Check if self collides with another sprite"""
        return (
            self.x < other.x + getattr(other, "width", 0) and
            self.x + getattr(self, "width", 0) > other.x and
            self.y < other.y + getattr(other, "height", 0) and
            self.y + getattr(self, "height", 0) > other.y
        )
