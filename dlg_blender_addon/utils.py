import bpy

def is_armature_poll(self, object: bpy.types.Object) -> bool:
    return object.type == 'ARMATURE'

