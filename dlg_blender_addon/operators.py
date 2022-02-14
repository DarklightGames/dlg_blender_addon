from bpy.types import Operator


class DLG_OT_HelloWorld(Operator):
    bl_idname = 'dlg_operator.do_nothing'
    bl_label = 'Hello, World!'
    bl_options = {'REGISTER'}
    bl_description = 'Hello, World!'

    def execute(self, context):
        self.report({'INFO'}, 'Hello, World!')
        return {'FINISHED'}


classes = (
    DLG_OT_HelloWorld
)
