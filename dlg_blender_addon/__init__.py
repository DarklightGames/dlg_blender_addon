bl_info = {
    "name": "Darklight Games Blender Tools",
    "author": "Colin Basnett, Yurii Tinianskyi",
    "version": (0, 2, 0),
    "blender": (3, 0, 0),
    # "location": "File > Export > PSK Export (.psk)",
    "description": "Darklight Games Blender Tools",
    "warning": "",
    "doc_url": "https://github.com/DarklightGames/dlg_blender_addon",
    "tracker_url": "https://github.com/DarklightGames/dlg_blender_addon/issues",
    "category": "Animation"
}

if 'bpy' in locals():
    import importlib
    importlib.reload(dlg_anim_bake)
else:
    from . import anim_bake as dlg_anim_bake

import bpy
from bpy.props import PointerProperty, BoolProperty

classes = dlg_anim_bake.__classes__

# def hello_world_func(self, context):
#     self.layout.operator(dlg_operators.DLG_OT_HelloWorld.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # This needs to happen so that it shows up in F3 menus, not required for most other operators
    # bpy.types.VIEW3D_MT_object.append(hello_world_func)
    bpy.types.Scene.dlg_anim_bake_props = PointerProperty(type=dlg_anim_bake.DlgAnimationBakingPropertyGroup)
    bpy.types.Action.dlg_is_selected = BoolProperty(default=False)


def unregister():
    # Any done in register must be undone in register, otherwise chaos ensues.
    del bpy.types.Scene.dlg_anim_bake_props
    del bpy.types.Action.dlg_is_selected
    # bpy.types.VIEW3D_MT_object.remove(hello_world_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
