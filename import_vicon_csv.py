# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

""" This script is an importer for Vicon CSV motion capture data """

from math import radians, degrees
import csv

def read_csv_header(context, csvfile):
    """
    Parse the header of a Vicon csv file.
    Returns list of tracked object names.
    """
    # Skip garbage object count
    csvfile.readline();
    csvfile.readline();

    csvreader = csv.reader(csvfile);
    object_name_row = next(csvreader, None);

    # Skip column labels
    next(csvreader, None);
    next(csvreader, None);

    return [object_name_row[i][len("Global Angle "):] for i in range(2, len(object_name_row) - 1, 6)]

def read_csv(context, obj_index, frame_rate, csvfile):

    # get the active object
    scene = context.scene
    obj = context.active_object

    col_index = obj_index * 6 + 2;
    csvreader = csv.reader(csvfile);

    decimation = int(frame_rate / scene.render.fps);

    # Read data
    for i, row in enumerate(csvreader):
        if len(row) == 0:
            break;
        if i % decimation != 0:
            continue;
        # print(row);
        scene.frame_set(int(round(float(row[0]) / decimation)));

        obj.location = [float(row[j]) / 1000 for j in range(col_index + 3, col_index + 6)]
        obj.keyframe_insert("location")

        obj.rotation_euler.x = float(row[col_index])
        obj.rotation_euler.y = float(row[col_index + 1])
        obj.rotation_euler.z = float(row[col_index + 2])
        obj.keyframe_insert("rotation_euler");

        # print("Location:", obj.location, "Rotation:", obj.rotation_euler);

    return {'FINISHED'}
