The game is built using **Python** and **Pygame**.

## Features
- Nighttime environment with limited visibility
- Automatic searchlight system with target tracking
- Multiple aircraft types with different flight behaviors
- Physics-based destruction (burning and falling aircraft)
- Score, timer, and miss tracking system
- Simple control scheme (Aim + Shoot)

## Requirements
- Python 3.x
- Pygame library

Install Pygame (if not already installed):
```bash
pip install pygame
```

# Important Setup (Image Paths)

Before running the game, you must update the file paths for the aircraft and fire textures.
By default, the code uses local paths like this:

PLANE_PATHS = {
    "B17": Path(r"D:\Hamster\Material\B17.png"),
    "B29": Path(r"D:\Hamster\Material\B29.png"),
    "B36": Path(r"D:\Hamster\Material\B36.png"),
}
FIRE_PATH = Path(r"D:\Hamster\Material\FIRE.png")

**What you need to do**

Replace these paths with the correct locations on your own computer.

If your images are stored in:

C:\Users\YourName\Desktop\assets\

Then **update the code** to:

PLANE_PATHS = {
    "B17": Path(r"C:\Users\YourName\Desktop\assets\B17.png"),
    "B29": Path(r"C:\Users\YourName\Desktop\assets\B29.png"),
    "B36": Path(r"C:\Users\YourName\Desktop\assets\B36.png"),
}
FIRE_PATH = Path(r"C:\Users\YourName\Desktop\assets\FIRE.png")

**Notes**
Make sure all image filenames match exactly (including capitalization)
Use raw string format r"..." to avoid path errors
If paths are incorrect, the game may crash or use placeholder graphics

**How to Run**
python your_filename.py

**Controls**
A key → Change firing angle
SPACE → Shoot
Mouse Click → Use on-screen buttons
R key → Restart (after game over)

**Objective**
Shoot down as many aircraft as possible
Avoid letting too many escape
Survive until the timer ends

**Notes**

This project was developed under time constraints and focuses on system interaction rather than graphical complexity.

License: MIT License
