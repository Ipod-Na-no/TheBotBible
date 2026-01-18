# Non Planar GCODE:
(Brick Layers, Non-Planar Infill, Alternating/Interlocking Walls)

Non-Planar printing techniques are part of Afterburner’s secret sauce. I had great luck with interlocking walls!

However, this process is inherently difficult. 

Requirements:

- A 3D printer with a low nozzle (clearance between the heat block and the tip) that can accept modified ASCII GCODE

- If you are trying to print with Brick Layers, you cannot use a Bambulabs printer or Bambu Studio. From what I know, interlocking walls should work just fine.

- A Slic3r derived slicer (SuperSlicer, PrusaSlicer, OrcaSlicer) 
_Many have had good luck with PrusaSlicer, including myself. Cura does not work._

- Python 3 on your computer. _I’ve had good luck with Python 3.11, 3.13, and 3.14._

### If you need Python:

Open Terminal as an administrator.

Type `winget install python3`

# Before even attempting to run the script, understand these conditions:

- You must be fluent in Marlin GCODE. Python experience helps too. 

- You must be comfortable with modifying slicers and reading terminal outputs.

- You must be very comfortable with your 3D printer. 

- **YOU MAY DAMAGE YOUR PRINTER with corrupted paths.**

- **YOU MAY DAMAGE YOUR PRINTER due to incorrect clearances.**

- **I am NOT RESPONSIBLE for damage to your printer.**

- If you are not comfortable with these risks, DO NOT TRY THIS!

If you choose to continue, here’s the [Repository.](https://github.com/TengerTechnologies/Bricklayers/tree/main) 



## Tips:

Turn off Arc Fitting and bgcode. Results tend to be better.

Check your file in a DEDICATED GCODE viewer. The slicer preview doesn’t show everything. This helps you find corrupt paths. 


![alt text](/media/corrupt.png?raw=true)

_Looks pretty corrupt to me! I wouldn’t want to print that._


If your printer has a multicolor unit (Prusa MMU, Bambu AMS, Creality CFS, etc), disable it and use a single color profile. The script doesn’t know how to deal with filament changes. This does mean that you cannot run a non-planar multicolor print.

_(Prusa MMU3 users: MMU3 enabled printers can read single color profile GCODEs with no issues or configuration changes. Disabling the MMU3 is not necessary. If you decide to disable the MMU3, keep the toolhead set to MMU3)_

Toolchanging/IDEX/Dual Nozzle printers (Prusa XL, Bambu H2D, E3D Toolchanger, etc) may only use one tool.

If your printer uses a discrete, fixed leveling probe (BL/CR/3DTouch, SuperPINDA, etc), remove it after the leveling process (M600 at the end of your start GCODE, remove it, then resume). Integrated solutions (Bambu LiDAR, Prusa Loadcell) or toolchanging solutions (Klicky) do not need this line.

Transfer the file manually with a local storage device, like a USB flash drive or an SD card.  DO NOT use the cloud! Non-planar GCODEs can be several hundreds of megabytes. This will take a long time for a cloud upload.


