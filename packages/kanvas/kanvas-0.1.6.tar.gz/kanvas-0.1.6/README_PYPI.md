# kanvas

A minimalist creative-coding toolkit for Python, inspired by Processing and p5.js.

**Key Features:**
- Simple setup/draw loop similar to Processing
- Built on pygame for cross-platform support
- Lightweight and hackable codebase
- Basic shape primitives (line, rect, circle)
- Educational focus with readable code

## Installation

```bash
pip install kanvas
```

### Requirements
- Python 3.9 or higher
- pygame 2.0+
- numpy 1.23+

## Quick Start

```python
from kanvas import run

def setup(model):
    model.clear(30)  # gray background

def draw(model, frame, dt):
    # Moving white line
    x = (frame // 2) % model.w
    for y in range(model.h):
        model.pixel(x, y, 255, 255, 255)

run(setup, draw, size=(800, 600), title="My First Sketch")
```

Press **ESC** to quit or **S** to save frame as PNG.

## Examples

### Basic Shapes
```python
from kanvas import run

def draw(model, frame, dt):
    model.clear(0)
    model.line(10, 10, model.w - 10, model.h - 10, 255, 255, 255)  # line
    model.rect(20, 20, 100, 60, 255, 0, 0)  # rectangle
    model.circle(model.w // 2, model.h // 2, 50, 0, 255, 0)  # circle

run(lambda m: None, draw, size=(400, 300))
```

### Animated Examples
Check the `examples/` folder for:
- **Fractal Tree**: Recursive tree with swaying motion
- **Orbiting Circle**: Circular motion animation  
- **Sierpinski Triangle**: Chaos game fractal generation

```python
from kanvas.core import run
import random

def setup(model):
    model.clear(20)

def draw(model, frame, dt):
    # Define triangle vertices
    a = {'x': int(model.w/2), 'y': 0}
    b = {'x': 0, 'y': model.h - 1}
    c = {'x': model.w - 1, 'y': model.h - 1}
    targets = [a, b, c]
    
    # Starting point
    p = {'x': int(model.w/2), 'y': int(model.h/2)}
    
    # Generate 1000 points
    for i in range(1000):
        target = random.choice(targets)
        p['x'] = (p['x'] + target['x']) // 2
        p['y'] = (p['y'] + target['y']) // 2
        model.pixel(p['x'], p['y'], 255, 255, 255)

run(setup, draw, size=(800, 800), title="Sierpinski Triangle")
```

### Ulam Spiral
Visualize prime numbers in a spiral pattern:

```python
from kanvas.core import run

def is_prime(n):
    if n <= 1:
        return False
    if n % 2 == 0:
        return n == 2
    r = int(n**0.5)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True

def setup(model):
    model.clear(20)
    
    # Spiral generation logic
    directions = [(1,0), (0,-1), (-1,0), (0,1)]  # right, up, left, down
    x, y = model.w // 2, model.h // 2
    
    n = 1
    dir_idx = 0
    steps_in_leg = 1
    steps_taken = 0
    legs_done_at_length = 0
    
    while 0 <= x < model.w and 0 <= y < model.h:
        if is_prime(n):
            model.pixel(x, y, 255, 255, 255)
        
        # Move in spiral
        dx, dy = directions[dir_idx]
        x += dx * 4  # Step size
        y += dy * 4
        
        n += 1
        steps_taken += 1
        
        # Turn logic for spiral pattern
        if steps_taken == steps_in_leg:
            dir_idx = (dir_idx + 1) % 4
            steps_taken = 0
            legs_done_at_length += 1
            if legs_done_at_length == 2:
                steps_in_leg += 1
                legs_done_at_length = 0

def draw(model, frame, dt):
    pass

run(setup, draw, size=(800, 800), title="Ulam Spiral")
```

## API Reference

### Core Functions

#### `run(setup_func, draw_func, **kwargs)`
Main entry point to start a kanvas sketch.

**Parameters:**
- `setup_func`: Function called once at startup, receives `model` parameter
- `draw_func`: Function called every frame, receives `model`, `frame`, and `dt` parameters
- `size`: Tuple of (width, height) for window size (default: (640, 360))
- `title`: Window title string (default: "kanvas")
- `target_fps`: Target frames per second (default: 60)

### Drawing API

```python
model.pixel(x, y, r, g, b)           # Set pixel color
model.clear(gray)                    # Clear to grayscale 
model.clear(r, g, b)                 # Clear to RGB color
model.line(x0, y0, x1, y1, r, g, b)  # Draw line
model.rect(x, y, w, h, r, g, b, fill=False)      # Draw rectangle
model.circle(cx, cy, radius, r, g, b, fill=False) # Draw circle
```

**Properties:** `model.w` (width), `model.h` (height)

### Loop Control
- `noLoop()` / `loop()` - Stop/start animation
- `isLooping()` - Check if animating

### Controls
- **ESC**: Quit  
- **S**: Save frame as PNG

## Philosophy

kanvas is designed for **learning by doing**. The codebase is simple and readable, perfect for understanding how creative coding frameworks work. Ideal for education, prototyping, and creative exploration.

## Source Code

Visit the project on GitHub: https://github.com/robinoscarsson/kanvas

## License

MIT License - see the GitHub repository for full details.

## Acknowledgments

- Inspired by Processing and p5.js
- Built with pygame
- Created for educational purposes and creative exploration