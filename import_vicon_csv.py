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

from math import ceil
import csv


def read_csv_header(context, csvfile):
    """
    Parse the header of a Vicon csv file.
    Returns list of tracked object names.
    """
    # Skip garbage object count
    csvfile.readline()
    csvfile.readline()

    csvreader = csv.reader(csvfile)
    object_name_row = next(csvreader, None)

    # Skip column labels
    next(csvreader)
    next(csvreader)

    # Also remove the "Global Angle " prefix from the object names
    return [object_name_row[i][len("Global Angle "):]
            for i in range(2, len(object_name_row) - 1, 6)]


def get_frame_num(row):
    '''Return the 0 based frame number of the given row of the csv'''
    return int(row[0]) - 1


def get_rotloc(row, col_index):
    '''
    Extract the rotation and location values from a given row of the parse csv.
    row is a list of strings representing the contents of each column from
    the exported csv file. col_index is the integer index of the column
    number corresponding to the object whose data is to be extracted.

    Returns a tuple of lists containing the location and rotation values
    as floats. Locations are reported in units of meters.
    '''

    # First three columns contain rotation x,y,z
    rotation = [float(row[i])
                for i in range(col_index, col_index + 3)]
    # Next three columns contain location x,y,z
    location = [float(row[i]) / 1000
                for i in range(col_index + 3, col_index + 6)]
    return (location, rotation)


def linear_interp(bl_frame, bl_fps, prevrow, nextrow, col_index, frame_rate):
    '''
    Perform linear interpolation to estimate the rotation and location for
    the Blender frame number bl_frame based on the data for previous and
    next rows in sequence. If prevrow is None, return location and rotation
    data from nextrow

    Returns a tuple of lists containing the location and rotation values
    as floats. Locations are reported in units of meters.
    '''

    if prevrow is None or len(prevrow) == 0:
        return get_rotloc(nextrow, col_index)

    # Calculate interpolation factor
    alpha = (bl_frame / bl_fps * frame_rate) - get_frame_num(prevrow)
    alpha /= get_frame_num(nextrow) - get_frame_num(prevrow)

    prev_loc, prev_rot = get_rotloc(prevrow, col_index)
    next_loc, next_rot = get_rotloc(nextrow, col_index)

    location = [(1 - alpha) * prev_loc[i] + alpha * next_loc[i]
                for i in range(len(prev_loc))]
    rotation = [(1 - alpha) * prev_rot[i] + alpha * next_rot[i]
                for i in range(len(prev_loc))]

    return (location, rotation)


def read_csv(context, obj_index, frame_rate, csvfile):

    scene = context.scene
    obj = context.active_object
    bl_fps = scene.render.fps

    # Each object's data takes six columns, plus two for frame/subframe number
    col_index = obj_index * 6 + 2
    csvreader = csv.reader(csvfile)

    # prevrow and nextrow bracket the current Blender frame in time. If the
    # current Blender frame aligns with a motion capture sample, it shall align
    # with nextrow.
    # Thus, prevrow's time < Blender frame's time <= nextrow's time
    prevrow = None
    nextrow = next(csvreader, [])

    # Note all frame numbers are 0 based for easier time conversion
    bl_frame = 0

    # Read data
    while len(nextrow) > 0:

        # Skip samples until we get a pair that brackets our target frame
        while (len(nextrow) > 0 and
               get_frame_num(nextrow) < (bl_frame / bl_fps * frame_rate)):
            prevrow = nextrow
            nextrow = next(csvreader, [])

            # Skip samples with no data
            while len(nextrow) == 1:
                nextrow = next(csvreader, [])

            # Stop if end of file is reached
            if len(nextrow) == 0:
                scene.frame_end = max(scene.frame_end, bl_frame)
                return {'FINISHED'}

        # Increase by one since Blender starts with frame 1 by default
        scene.frame_set(bl_frame + 1)
        obj.location, obj.rotation_euler = linear_interp(bl_frame, bl_fps,
                                                         prevrow, nextrow,
                                                         col_index, frame_rate)
        obj.keyframe_insert("location")
        obj.keyframe_insert("rotation_euler")

        bl_frame += 1

    scene.frame_end = max(scene.frame_end, bl_frame)
    return {'FINISHED'}
