import bpy
from bpy.types import PropertyGroup, Action, PoseBone, Object
from bpy.props import StringProperty, PointerProperty, CollectionProperty, BoolProperty, IntProperty
from . import utils


class DlgActionGroupItem(PropertyGroup):
    action: PointerProperty(type=Action)
    is_selected: BoolProperty(default=False)


class DlgActionGroup(PropertyGroup):
    name: StringProperty(
        default='AnimGroup',
        name='Name')

    gap_frames: IntProperty(
        default=1,
        name='Gap Frames',
        description='Size of the gap between strips')

    actions_index_left: IntProperty(
        name='Active Actions Index')

    actions_index_right: IntProperty(
        name='Active Grouped Actions Index')

    actions: CollectionProperty(type=DlgActionGroupItem)


    def get_selected_action_left(self) -> Action:
        # TODO: Make sure list is not empty
        return bpy.data.actions[self.actions_index_left]

    def get_selected_action_right(self) -> Action:
        # TODO: Make sure list is not empty
        return self.actions[self.actions_index_right].action


class DlgSceneProperties(PropertyGroup):

    def get_selected_anim_group(self) -> DlgActionGroup:
        return self.anim_groups[self.anim_groups_index]

    data_action_group_items: CollectionProperty(type=DlgActionGroupItem)
    data_action_group_items_index: IntProperty()

    # NLA / Anim groups
    anim_groups: CollectionProperty(type=DlgActionGroup)
    anim_groups_index: IntProperty(
        name='Active Action Group')

    # Markers
    use_action_names_for_markers: BoolProperty(
        default=False,
        name='Use Action Names',
        description='Use names of referenced actions instead of strip names')
    marker_name_replace: StringProperty(name='Replace')
    marker_name_replace_with: StringProperty(name='With')

    # Action Bake
    action_index: IntProperty(default=0)
    filter_name: StringProperty(options={'TEXTEDIT_UPDATE'})
    bitflag_filter_item = 1 << 30
    only_selected_bones: BoolProperty(default=True)
    visual_keying: BoolProperty(default=True)
    overwrite_current_action: BoolProperty(default=True)
    clean_curves: BoolProperty(default=True)
    use_filter_invert: BoolProperty(default=False, options={'TEXTEDIT_UPDATE'})

    source_armature: PointerProperty(type=Object,
                                     poll=utils.is_armature_poll,
                                     name='Source Armature',
                                     description='Armature to transfer animations from')

    target_bone_collection: StringProperty(default='RETARGET',
                                           name='Target Bone Collection',
                                           description='Bone collection to target for baking')


__classes__ = [
    DlgTargetBone,
    DlgActionGroupItem,
    DlgActionGroup,
    DlgSceneProperties
]
