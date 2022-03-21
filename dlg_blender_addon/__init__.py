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
    importlib.reload(dlg_props)
    importlib.reload(dlg_utils)
    importlib.reload(dlg_anim_bake)
    importlib.reload(dlg_action_group_props)
    importlib.reload(dlg_action_groups)
else:
    from . import props as dlg_props
    from . import utils as dlg_utils
    from . import anim_bake as dlg_anim_bake
    from . import action_group_props as dlg_action_group_props
    from . import action_groups as dlg_action_groups

import bpy
from bpy.props import PointerProperty, BoolProperty


classes = dlg_props.__classes__ + \
          dlg_anim_bake.__classes__ + \
          dlg_action_group_props.__classes__ + \
          dlg_action_groups.__classes__


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.dlg_props = PointerProperty(type=dlg_props.DlgSceneProperties)
    bpy.types.Action.dlg_is_selected = BoolProperty(default=False)


def unregister():
    # Any done in register must be undone in register, otherwise chaos ensues.
    del bpy.types.Scene.dlg_props
    del bpy.types.Action.dlg_is_selected
    # bpy.types.VIEW3D_MT_object.remove(hello_world_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
