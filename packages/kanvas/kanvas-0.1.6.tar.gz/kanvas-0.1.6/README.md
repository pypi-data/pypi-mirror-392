# kanvas

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A minimalist creative-coding toolkit for Python, inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/).

**Key Features:**
- Simple setup/draw loop similar to Processing
- Built on pygame for cross-platform support
- Basic shape primitives (pixel, line, rect, circle)
- Lightweight and hackable codebase (~200 lines)
- Educational focus with clean MVC architecture

## Installation

### Requirements
- Python 3.9 or higher
- pygame 2.0+
- numpy 1.23+

### Install from source
```bash
git clone https://github.com/robinoscarsson/kanvas.git
cd kanvas
pip install -e .
```

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

Press **ESC** to quit, **S** to save frame.

## Examples

## Examples

### Basic Shapes
```python
from kanvas import run

def draw(model, frame, dt):
    model.clear(0)
    model.line(10, 10, model.w - 10, model.h - 10, 255, 255, 255)
    model.rect(20, 20, 100, 60, 255, 0, 0)
    model.circle(model.w // 2, model.h // 2, 50, 0, 255, 0)

run(lambda m: None, draw, size=(400, 300))
```

### More Examples
Check the `examples/` directory:
- **Fractal Tree**: Recursive tree with swaying motion
- **Orbiting Circle**: Circular motion animation  
- **Sierpinski Triangle**: Chaos game fractal
- **Ulam Spiral**: Prime number visualization

![Sierpinski Triangle](examples/output/Sierpinski%20Triangle%20Demo_20251110_204627.png)
![Ulam Spiral](examples/output/Ulam%20Spiral%20Demo%20(fixed)_20251110_204254.png)

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
# Basic drawing functions
model.pixel(x, y, r, g, b)                      # Set pixel
model.clear(gray) / model.clear(r, g, b)        # Clear canvas
model.line(x0, y0, x1, y1, r, g, b)             # Draw line  
model.rect(x, y, w, h, r, g, b, fill=False)     # Draw rectangle
model.circle(cx, cy, radius, r, g, b, fill=False) # Draw circle

# Properties
model.w, model.h  # Canvas dimensions
```

### Loop Control & Input

```python
from kanvas import noLoop, loop, isLooping

noLoop()      # Stop animation
loop()        # Resume animation  
isLooping()   # Check if running
```

**Controls:** ESC (quit), S (save frame)



## Architecture & Philosophy

Clean MVC pattern in ~200 lines. Designed for **learning by doing** with simple, readable code.

```
src/kanvas/
├── core.py         # Main loop
├── controller.py   # Input handling  
├── view.py         # Pygame rendering
├── model.py        # Canvas & drawing
└── utils.py        # Utilities
```

## Contributing & License

Educational project welcoming contributions! MIT License - see GitHub for details.

## Roadmap

- [x] Shape primitives (pixel, line, rect, circle) ✅
- [ ] Color management system
- [ ] Mouse and keyboard input
- [ ] Animation recording & export

## Acknowledgments

Inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/), built with [pygame](https://pygame.org).

---

## 🎨 Overview

kanvas aims to capture the *feel* of Processing:  
`setup()` runs once, `draw()` runs every frame, and the rest is up to you.

Under the hood it uses [pygame](https://www.pygame.org/news) for the window and rendering, and a small core loop written to be readable, hackable, and educational.

The goal isn’t performance or feature parity — it’s **understanding**.  
If you’ve ever wondered *“how would I build p5 myself?”*, this is that journey.

---

## ⚙️ Installation

Clone the repository and install it locally in editable mode:

```bash
git clone https://github.com/yourname/kanvas.git
cd kanvas
pip install -e .
```

kanvas requires **Python 3.9+** and **pygame** (automatically installed via pip).

---

## 🚀 Quick Start

Create a new Python file, for example `example.py`:

```python
from kanvas import run

def setup(model):
    model.clear(30)  # background gray

def draw(model, frame, dt):
    x = (frame // 2) % model.w
    for y in range(model.h):
        model.pixel(x, y, 255, 255, 255)

run(setup, draw, size=(320, 200), title="kanvas Example")
```

Then run it:

```bash
python example.py
```

A small window should appear with a white line sweeping across the screen.  
Press **ESC** or click the **X** to quit.

---

## 🧩 Project Structure

```
src/kanvas/
├── core.py         # Main loop orchestration
├── controller.py   # Handles input (ESC / window close)
├── view.py         # Pygame window and rendering
├── model.py        # Framebuffer and pixel operations
└── __init__.py
examples/
└── pixelsmoke.py   # Simple demonstration sketch
```

---

## ✨ Features (so far)

- Minimal setup/draw loop  
- Clean separation of core / view / controller / model  
- ESC and window close handling  
- Simple pixel drawing via NumPy framebuffer  
- Beginner-friendly codebase (~200 lines total)

---

## 🧠 Philosophy

kanvas exists to **learn by building**.  
Every function is deliberately simple and explicit. There’s no magic, no global state, and no framework hiding the logic from you.

You can trace the entire rendering path from `run()` → `controller.handle_input()` → `model.pixel()` → `view.present_framebuffer()` in less than a minute.

If you’re curious about:
- How Processing or p5’s loop actually works  
- How to handle events and rendering cleanly in Python  
- Or just want a compact sandbox for creative-coding ideas  

…this project might make you happy.

---

## 🧩 Roadmap (subject to whim)

- [ ] Basic shape primitives (`line`, `circle`, `rect`)
- [ ] `background()`, `fill()`, `stroke()` API layer
- [ ] Mouse position and keyboard input
- [ ] Higher-level color & transformation helpers
- [ ] Export to image / animation

This is a **hobby project**, not a product. Expect it to evolve (and break) as it grows.

---

## ❤️ Acknowledgements

- Inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/)  
- Built with [pygame](https://www.pygame.org/news)  
- Written out of pure curiosity and love for creative coding.

---

## 📄 License

MIT License — do whatever you want, but if you learn something, or make something cool, pass it on.
