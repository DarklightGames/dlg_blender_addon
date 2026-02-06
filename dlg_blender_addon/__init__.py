from . import utils, properties
from .nla import (operators as nla_operators,
                  ui as nla_ui)
from .retarget import (operators as retarget_operators,
                  ui as retarget_ui)


if 'bpy' in locals():
    import importlib

    importlib.reload(utils)
    importlib.reload(properties)
    importlib.reload(nla_operators)
    importlib.reload(nla_ui)
    importlib.reload(retarget_operators)
    importlib.reload(retarget_ui)


import bpy
from bpy.props import PointerProperty, BoolProperty


_modules = (
    properties,
    nla_operators,
    nla_ui,
    retarget_operators,
    retarget_ui,
)


_properties = {
    'Scene': {
        'dlg_props': PointerProperty(type=properties.DLG_PG_scene_properties),
    },
    'Action': {
        'dlg_is_selected': BoolProperty(default=False),
    },
}


def register():
    for module in _modules:
        module.register()

    for attr, prop in _properties.items():
        bl_type = getattr(bpy.types, attr)

        for attr, prop in prop.items():
            setattr(bl_type, attr, prop)


def unregister():
    # Anything done in register() must be undone here
    for attr, prop in _properties.items():
        bl_type = getattr(bpy.types, attr)

        for attr, prop in prop.items():
            delattr(bl_type, attr)

    for module in _modules:
        module.unregister()


if __name__ == '__main__':
    register()
