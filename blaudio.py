bl_info = {
    "name": "Blaudio",
    "author": "Shraga the Mighty Sky Worm",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "Scene > Blaudio",
    "description": "Adds an audio visualizer.",
    "warning": "",
    "wiki_url": "http://ShragasServer.ddns.net",
    "category": "Audio",
}


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


import bpy
import os
from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def makeMaterial(name, diffuse, alpha):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    return mat

def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)


def audiofy(file, bars, barheight, maxfreq, minfreq, barwidth, interval, cubes, ds):

    c = 1
    l = 1
    h = 1

    base = ( maxfreq / minfreq ) ** ( 1 / ( bars - 1 ) )

    white = makeMaterial('EQ', (1, 1, 1, 1), 1)

    collection = bpy.data.collections.new("Blaudio")
    bpy.context.scene.collection.children.link(collection)

    for i in range(0, bars):

        l = h

        #calculate the frequency
        h = minfreq * base ** ( c - 1 )

        # add a plane / cube
        if (cubes):
            bpy.ops.mesh.primitive_cube_add(location = (c * interval, 1, 0))
        else:
            bpy.ops.mesh.primitive_plane_add(location = (c * interval, 1, 0))
        obj = bpy.context.active_object
        # set the material
        setMaterial(obj, white)
        # move it to a new Collection
        bpy.ops.collection.objects_remove_all()
        bpy.data.collections['Blaudio'].objects.link(obj)
        # move the cursor location to the plane location
        bpy.context.scene.cursor.location = obj.location
        # move the cursor 1 unit down
        bpy.context.scene.cursor.location.y -= 1
        # move the object origin to the cursor location
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # scale the plane
        obj.scale.x = barwidth
        obj.scale.y = barheight
        obj.scale.z = barwidth

        # apply the scale
        bpy.ops.object.transform_apply(scale=True)

        # insert a scale keyframe
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')

        # lock X and Z for scaling
        obj.animation_data.action.fcurves[0].lock = True
        obj.animation_data.action.fcurves[2].lock = True

        # change this to a graph editor because baking sound only works with that
        bpy.context.area.type = 'GRAPH_EDITOR'

        # bake the sound into the plane
        bpy.ops.graph.sound_bake(filepath=file, low=l, high=h, attack=0.001, release=0.2)

        # lock the y scaling just because
        obj.animation_data.action.fcurves[1].lock = True

        obj.animation_data.action.fcurves[0].lock = False
        obj.animation_data.action.fcurves[2].lock = False
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.delete()

        # reset origin
        if (ds):
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        # add 1 to the C value that is used to determine the frequency for the plane
        c += 1

    bpy.context.area.type = 'PROPERTIES'
    bpy.ops.object.speaker_add(enter_editmode=False, location=(0, 0, 0))

    obj = bpy.context.active_object
    bpy.ops.collection.objects_remove_all()
    bpy.data.collections['Blaudio'].objects.link(obj)

    bpy.ops.sound.open(filepath=file, relative_path=False)

    bpy.context.scene.cursor.location = [0, 0, 0]




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class OT_TestOpenFilebrowser(Operator, ImportHelper):

    bl_idname = "blaudio.select"
    bl_label = "Select a sound..."
    bl_description = "Turn music into shapes"

    filter_glob:  StringProperty(
        default='*.mp3;*.wav;*.flac;',
        options={'HIDDEN'}
    )

    Bars: IntProperty(
        default=24,
        soft_min=0
    )

    Bar_height: FloatProperty(
        default=5
    )

    Max_frequency: IntProperty(
        default=20000,
        soft_min=1
    )

    Min_frequency: IntProperty(
        default=20,
        soft_min=1
    )

    Bar_width: FloatProperty(
        default=0.4,
        soft_min=0
    )

    Interval: FloatProperty(
        default=1.0,
        soft_min=0
    )

    Cubes: BoolProperty(
        default=False
    )

    Dual_sided: BoolProperty(
        default=False
    )

    # scenelength: BoolProperty(
    #     default=True
    # )

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        audiofy(self.filepath, self.Bars, self.Bar_height, self.Max_frequency, self.Min_frequency, self.Bar_width, self.Interval, self.Cubes, self.Dual_sided)
        # if (self.scenelength):
        #     print("ok")
        return {'FINISHED'}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



class BlaudioPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Blaudio"
    bl_idname = "SCENE_PT_Blaudio"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        # Big render button
        row = layout.row()
        row.scale_y = 1.0
        row.operator("blaudio.select")



def register():
    bpy.utils.register_class(OT_TestOpenFilebrowser)
    bpy.utils.register_class(BlaudioPanel)


def unregister():
    bpy.utils.unregister_class(OT_TestOpenFilebrowser)
    bpy.utils.unregister_class(BlaudioPanel)


if __name__ == "__main__":
    register()
