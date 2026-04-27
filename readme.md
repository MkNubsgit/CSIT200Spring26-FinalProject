CSIT 200 Group Project!

    This project was built using PyQt6. PyQt6 is the only dependency at this time. 

    Our project is a simple "MSPaint" Clone that has adjustable brush size, color, and opacity, and supports saving and loading drawings. 

_________________________________________________________________________________________________

Features:
    - Brush drawing
    - Eraser tool
    - Saving/Loading (1)
    - Color Picking (using premade QColorDialog)
    - Size Adjustment of Eraser and Brush
    - Rough opacity adjustment (Does not *fully work across 0-100 range due to linear mapping but early portions of range do display function (roughly 0-20 %ish i might fix if i have time))

File operations: (1)
    The program is fairly simple. We allow users to export a fixed canvas size and import images that are the same size. 

    - Loading supports png, jpg
    - Saving supports png

_________________________________________________________________________________________________

Structure:
    the program runs in this encapsulation sequence. Listed Components with * are classes. 

-- Main * 
    # (you know what this does)
-- SliderControl *  
    # Sliders + spinboxes.
-- RotationControl * 
    # Dial and degree input for rotation (implemented but not used as of yet)
-- Canvas * 
    # Most important module by far, handles all our drawing logic and buffer for image.
-- MainWindow * 
    # Holds the other components in our PyQt6 GUI

_________________________________________________________________________________________________

STRETCH GOALS THAT I HAVE *****NOT ****** IMPLEMENTED AS OF YET WINK WINK GROUP

Undo/redo system
Zoom/pan on canvas
Brush Shapes
Layer Support
Selection tools

_________________________________________________________________________________________________

Additional Info:

The program currently does not utilize gpu acceleration. Anything drawn is being done via CPU rendering which unfortunately limits performance. 
I did not want to deal with implementing multithreading though. 