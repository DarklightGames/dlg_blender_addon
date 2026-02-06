from bpy.types import Object

def is_armature_poll(self, object: Object) -> bool:
    return object.type == 'ARMATURE'
