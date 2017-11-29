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

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        FloatProperty,
        )

bl_info = {
    "name": "Vicon CSV",
    "author": "Sunny He",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "File > Import/Export > Vicon CSV (.csv)",
    "description": "Import Vicon tracking data as object animation",
    "warning": "",
    "category": "Import-Export",
}


# To support reload properly, try to access a package var,
# if it's there, reload everything
if "bpy" in locals():
    import importlib
    if "import_vicon_csv" in locals():
        importlib.reload(import_vicon_csv)


class ImportViconCSV(Operator, ImportHelper):
    """Import animation from .csv file, exported from Vicon Tracker """
    bl_idname = "import_scene.import_vicon_csv"
    bl_label = "Import Vicon CSV File"

    filename_ext = ".csv"

    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'})

    tracking_obj_name = StringProperty(
        name="Name",
        description="Name of the Vicon tracked object to import",
        default="",
        )

    frame_rate = FloatProperty(
        name="FPS",
        description="Tracking Frames per Second",
        default=100.0,
        )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        from . import import_vicon_csv
        self.report({'PROPERTY'}, self.filepath)

        with open(self.filepath, 'r') as csvfile:
            obj_list = import_vicon_csv.read_csv_header(context, csvfile)
            print(obj_list)
            if len(obj_list) == 0:
                self.report({'ERROR'}, "No tracked objects found!")
                return {'CANCELLED'}

            obj_index = 0
            if self.tracking_obj_name != "":
                if self.tracking_obj_name in obj_list:
                    obj_index = obj_list.index(self.tracking_obj_name)
                else:
                    # Also expand to full name and check
                    self.tracking_obj_name = "{0}:{0}".format(
                        self.tracking_obj_name)
                    if self.tracking_obj_name not in obj_list:
                        self.report({'ERROR'}, "Specified object not found")
                        return {'CANCELLED'}
                    else:
                        obj_index = obj_list.index(self.tracking_obj_name)

            import_vicon_csv.read_csv(context, obj_index,
                                      self.frame_rate, csvfile)

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Tracked Object:")
        row = layout.row(align=True)
        row.prop(self, "tracking_obj_name")
        row = layout.row(align=True)
        row.prop(self, "frame_rate")


def menu_func_import(self, context):
    self.layout.operator(ImportViconCSV.bl_idname, text="Vicon CSV (.csv)")


def register():
    bpy.utils.register_class(ImportViconCSV)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportViconCSV)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()
