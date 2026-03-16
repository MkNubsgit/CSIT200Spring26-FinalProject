## FINAL PROJECT - PAINT CSIT200

## reference imports:
for gui container: tkinter - misha will complete
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

### FOR ALL BRUSHES
    - make brush size tied to variable "brushSize"
    - make color of brush tied to variable "brushColor"
    - make opacity of brush tied to variable "brushOpacity"
    - Crucial for non-symmetric brushes: Brush Rotation : rotation should be on center pivot 0-360 degrees, will create    variable "brushRotation"
    - 
    - 
    - ADD MORE SUGGESTIONS HERE AS NEEDED ***