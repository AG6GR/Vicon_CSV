# Vicon Motion Capture Importer
Blender addon for importing motion capture data stored in CSV files exported by [Vicon Tracker](https://www.vicon.com/products/software/tracker).

# Usage

<center><img src='doc/ImportMenu.PNG' alt='Import menu option' width=75%/></center>

To use the addon, select the Blender object you wish to map the motion tracking data to and select Vicon CSV (.csv) under File->Import.

<center><img src='doc/ImportOptions.PNG' alt='Import dialog options' width=30%/></center>

In the resulting dialog select the CSV file containing the exported motion capture data. On the left sidebar, specify the motion capture data frame rate and optionally the name of the tracked object to import. If no name is given, the addon defaults to the first object to appear in the CSV file.

After clicking "Import Vicon CSV," the motion capture data will be written to the object as a series of keyframes. If the frame rate of the Blender scene does not match the motion capture data's framerate, the addon will perform simple interpolation to compensate.

# Recording Process
