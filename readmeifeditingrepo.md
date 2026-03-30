## FINAL PROJECT - PAINT CSIT200

## reference imports:
for gui container: PyQt6 - misha will complete
    - create mouse detection, debating whether to use local detection or provide raw coordinate data, tba
    - create tray to hold brush modules created
    - STRETCH : create undo button , dependent on mouse click duration being tracked in order to identify strokes, for last held duration, make all points on stroke transparent
    - SAVE STATES : application must be able to save and recall canvas as files , implementation tba
    - 
    - 
    - ADD MORE SUGGESTIONS HERE AS NEEDED ***

## Other core modules
    - save states : brushes must be able to edit canvas and store stroke duration, attributes, location
    - brush sizing : brushes must have editable size
    - eraser : absolutely necessary, will have brush sizing attribute and opacity attribute
        2 potential modes:
            - bg color mode : takes background color and persistently matches hex code, acts as brush with persistent bg match attribute
            - transparency overwrite mode : acts as brush that sets opacity of any pixels it overwrites to 0
            +
    - opacity : STRETCH GOAL : may be implemented, if not successful set to fixed value @ 100
    - rotation : STRETCH GOAL : may be implemented, if not successful set to fixed value @ 0
    - background color : save as "backgroundColor" , must have hex code selector (text box) and color picker (gui)
        - stretch : implement recently used background colors, 8 recents similar to mspaint, allow click to select
    - STRETCH : fill bucket module, must track color of all values in clicked region, fill region surrounded by other color, attempt to fill all values but stop at other color values and do not overwrite, *flood fill essentially
    -
    - ADD MORE SUGGESTIONS HERE AS NEEDED ***

## BRUSH SUGGESTIONS
    - 
    - 
    - ADD SUGGESTIONS HERE



added 03/30/2026:
## VARIABLES AND CONVENTIONS:

#Global Canvas State Variables
These variables track the actual drawing surface and file management. 
---
current_image (QPixmap or QImage): Stores the actual pixel data of the current drawing.
file_path (String): Stores the location of the currently opened or saved file (defaults to None).
is_drawing (Boolean): Tracks whether the mouse button is currently held down on the canvas.
last_mouse_pos (QPoint): Stores the last known X/Y coordinate of the mouse to draw continuous lines.

History Control Variables
Used by the Undo and Redo buttons.
---
history_stack (List of QImage or QPixmap): An array storing snapshots of the canvas after every stroke.
history_index (Integer): Tracks the current position within the history_stack array.
Undo Button: Decrements history_index and restores that snapshot.
Redo Button: Increments history_index and restores that snapshot.

Tool Selection Variables
Used by the Left Panel buttons.
---
current_tool (String): Tracks the active drawing mode.
Eraser Button: Sets current_tool to "eraser".
    eraser will be permanently set to bg color (white) at 100% opacity, takes on size and rotation attributes. Rotation irrelevant however because eraser will be circular only. 
Fill Button: Sets current_tool to "fill".
Brush Grid Buttons: Sets current_tool to "brush".
current_brush_type (String): Tracks which of the 12 brush grid buttons was clicked ("solid", "spray", "calligraphy"). * SUBTYPE OF BRUSH 

Brush Property Variables
Used by the sliders and dials in the top toolbar.
---
brush_size (Integer): Linked to the Size SliderControl. Controls the pixel radius of the pen/brush. emphasis on radius, simplifies all workflows. radius is measured from widest point to center.
brush_opacity (Integer): Linked to the Opacity SliderControl. Controls transparency of brush. 
brush_rotation (Integer): Linked to the RotationControl dial. Controls the angle of directional brushes (like a calligraphy pen as discussed). works for all noncircular brushes. 

Color Management Variables
Used by the color picker, hex input, and recent color swatches.
---
current_color (QColor): The currently selected color for drawing or filling.
Color Button: Opens a QColorDialog and updates current_color.
Hex Input: Reads the text, parses the hex code, and updates current_color.
recent_colors (List of QColor): An array with a maximum length of 5.
Recent Swatches (1-5): When a new color is picked via the Color Button or Hex, it is added to the front of this list, and the last color is dropped. Clicking a swatch sets the current_color to that swatch's value.

File Action Operations
These do not necessarily need new variables, but here is how they interact with the ones above:
---
New Button: Clears the current_image to a white background, resets the file_path to None, and clears the history_stack.
Save Button: Writes the current_image data to the disk at file_path (prompting a file dialog if file_path is None).
Load Button: Reads a file from the disk, replaces current_image with it, sets file_path, and resets the history_stack.