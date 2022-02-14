bl_info = {
    "name": "Darklight Games Blender Tools",
    "author": "Colin Basnett",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    # "location": "File > Export > PSK Export (.psk)",
    "description": "Darklight Games Blender Tools",
    "warning": "",
    "doc_url": "https://github.com/DarklightGames/addon_darklight",
    "tracker_url": "https://github.com/DarklightGames/io_scene_psk_psa/issues",
    "category": "Import-Export"
}

if 'bpy' in locals():
    import importlib
    importlib.reload(dlg_operators)
else:
    from . import operators as dlg_operators

import bpy

classes = (
    dlg_operators.classes,
)


def hello_world_func(self, context):
    self.layout.operator(dlg_operators.DLG_OT_HelloWorld.bl_idname)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # This needs to happen so that it shows up in F3 menus, not required for most other operators
    bpy.types.VIEW3D_MT_object.append(hello_world_func)


def unregister():
    # Any done in register must be undone in register, otherwise chaos ensues.
    bpy.types.VIEW3D_MT_object.remove(hello_world_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
