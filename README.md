# Vicon Motion Capture Importer
Blender addon for importing motion capture data stored in CSV files exported by [Vicon Tracker](https://www.vicon.com/products/software/tracker).

# Usage

<img src='doc/ImportMenu.png' alt='Import menu option' width=30%/>

To use the addon, select the Blender object you wish to map the motion tracking data to and select Vicon CSV (.csv) under File->Import.

<img src='doc/ImportOptions.png' alt='Import dialog options' width=30%/>

In the resulting dialog select the CSV file containing the exported motion capture data. On the left sidebar, specify the motion capture data frame rate and optionally the name of the tracked object to import. If no name is given, the addon defaults to the first object to appear in the CSV file.

# Recording Process