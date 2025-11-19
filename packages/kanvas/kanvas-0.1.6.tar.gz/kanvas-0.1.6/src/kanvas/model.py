import numpy as np

class Model:
    """A framebuffer model for pixel-based graphics rendering.
    
    The Model class provides a 2D framebuffer for storing and manipulating pixel data.
    It supports basic operations like clearing the screen and setting individual pixels
    with RGB color values.
    
    Attributes:
        w (int): Width of the framebuffer in pixels.
        h (int): Height of the framebuffer in pixels.
        fb (numpy.ndarray): 3D numpy array storing RGB pixel data with shape (width, height, 3).
    """
    
    def __init__(self, w: int, h: int):
        """Initialize a new Model with specified dimensions.
        
        Creates a framebuffer with the given width and height, initialized to black (0,0,0).
        
        Args:
            w (int): Width of the framebuffer in pixels.
            h (int): Height of the framebuffer in pixels.
        """
        self.w, self.h = w, h
        self.fb = np.zeros((w, h, 3), dtype=np.uint8)

    def clear(self, r: int, g: int = None, b: int = None):
        """Clear the entire framebuffer with a specified color.
        
        Sets all pixels in the framebuffer to the specified RGB color.
        If only the red component is provided, it will be used for all three
        color components (creating a grayscale color).
        
        Args:
            r (int): Red color component (0-255).
            g (int, optional): Green color component (0-255). If None, uses the value of r.
            b (int, optional): Blue color component (0-255). If None, uses the value of r.
        """
        if g is None: g = b = r
        self.fb[:] = (r, g, b)

    def pixel(self, x: int, y: int, r: int, g: int, b: int):
        """Set a single pixel to the specified RGB color.
        
        Sets the pixel at coordinates (x, y) to the given RGB color values.
        The operation is bounds-checked; pixels outside the framebuffer dimensions
        are ignored to prevent array index errors.
        
        Args:
            x (int): X-coordinate of the pixel (0 to width-1).
            y (int): Y-coordinate of the pixel (0 to height-1).
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
        """
        if 0 <= x < self.w and 0 <= y < self.h:
            self.fb[x, y] = (r, g, b)

    def line(self, x0, y0, x1, y1, r, g, b):
        """Draw a line between two points using Bresenham's line algorithm.
        
        Draws a line from point (x0, y0) to point (x1, y1) with the specified RGB color.
        Uses Bresenham's line algorithm for efficient rasterization. The line is clipped
        to the framebuffer boundaries to prevent out-of-bounds errors.
        
        Args:
            x0 (int): X-coordinate of the starting point.
            y0 (int): Y-coordinate of the starting point.
            x1 (int): X-coordinate of the ending point.
            y1 (int): Y-coordinate of the ending point.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
        """
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy  # initial error

        while True:
            # bounds check to prevent crashes if coordinates are outside framebuffer
            if 0 <= x0 < self.w and 0 <= y0 < self.h:
                self.pixel(x0, y0, r, g, b)

            if x0 == x1 and y0 == y1:
                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def rect(self, x, y, w, h, r, g, b, fill=False):
        """Draw a rectangle with the specified position, size, and color.
        
        Draws a rectangle starting at position (x, y) with the given width and height.
        The rectangle can be drawn as either an outline (default) or filled based on
        the fill parameter. Uses the line() method to draw the outline and horizontal
        lines for filling.
        
        Args:
            x (int): X-coordinate of the top-left corner.
            y (int): Y-coordinate of the top-left corner.
            w (int): Width of the rectangle in pixels.
            h (int): Height of the rectangle in pixels.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
            fill (bool, optional): If True, fills the rectangle; if False, draws only the outline. Defaults to False.
        """
        # outer frame
        self.line(x, y, x + w - 1, y, r, g, b)               # top
        self.line(x, y, x, y + h - 1, r, g, b)               # left
        self.line(x + w - 1, y, x + w - 1, y + h - 1, r, g, b)  # right
        self.line(x, y + h - 1, x + w - 1, y + h - 1, r, g, b)  # bottom

        if fill:
            # simple fill: horizontal lines between left/right edges
            for yy in range(y + 1, y + h - 1):
                self.line(x + 1, yy, x + w - 2, yy, r, g, b)

    def circle(self, cx, cy, radius, r, g, b, fill=False):
        """Draw a circle with the specified center, radius, and color.
        
        Draws a circle centered at position (cx, cy) with the given radius and RGB color.
        The circle can be drawn as either an outline (default) or filled based on the
        fill parameter. Uses a simple pixel-by-pixel approach with distance calculations
        to determine which pixels belong to the circle.
        
        Args:
            cx (int): X-coordinate of the circle's center.
            cy (int): Y-coordinate of the circle's center.
            radius (int): Radius of the circle in pixels.
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
            fill (bool, optional): If True, fills the circle; if False, draws only the outline. Defaults to False.
        """
        r2 = radius * radius

        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dx = x - cx
                dy = y - cy
                dist2 = dx*dx + dy*dy

                if fill:
                    # all points *inside* the circle
                    if dist2 <= r2:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
                else:
                    # only points near the edge (tolerance band)
                    if r2 - radius <= dist2 <= r2 + radius:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            self.pixel(x, y, r, g, b)
