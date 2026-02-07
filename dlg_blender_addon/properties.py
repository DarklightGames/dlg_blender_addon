import bpy
from bpy.types import PropertyGroup, Action, PoseBone, Object, Context
from bpy.props import StringProperty, PointerProperty, CollectionProperty, BoolProperty, IntProperty
from .utils import is_armature_poll
# from . import utils

from typing import cast, Any
from fnmatch import fnmatch


class DLG_PG_action_group_item(PropertyGroup):
    action: PointerProperty(type=Action)
    is_selected: BoolProperty(default=False)


class DLG_PG_action_group(PropertyGroup):
    name: StringProperty(
        default='Actions',
        name='Group Name')

    gap_frames: IntProperty(
        default=1,
        soft_min=0,
        name='Spacing',
        description='The amount of frames to leave in between added strips')

    actions_index_left: IntProperty(
        name='Active Actions Index')

    actions_index_right: IntProperty(
        name='Active Grouped Actions Index')

    actions: CollectionProperty(type=DLG_PG_action_group_item)

    def get_active_action_left(self) -> Action:
        action: Action = cast(Action, bpy.data.actions[self.actions_index_left])
        return action

    def get_active_action_right(self) -> Action:
        return self.actions[self.actions_index_right].action

    def move_action_up(self, index) -> None:
        self.actions.move(index, index - 1)
        self.actions_index_right = max(0, self.actions_index_right - 1)

    def move_action_down(self, index) -> None:
        self.actions.move(index, index + 1)
        self.actions_index_right = min(max(0, len(self.actions) - 1), self.actions_index_right + 1)


class DLG_PG_scene_properties(PropertyGroup):

    def get_selected_anim_group(self) -> DLG_PG_action_group:
        groups = cast(DLG_PG_action_group, self.anim_groups[self.anim_groups_index])

        return self.anim_groups[self.anim_groups_index]

    def is_anim_group_selected(self) -> bool:
        return 0 <= self.anim_groups_index < len(self.anim_groups)

    data_action_group_items: CollectionProperty(type=DLG_PG_action_group_item)
    data_action_group_items_index: IntProperty()

    # NLA / Anim groups
    anim_groups: CollectionProperty(type=DLG_PG_action_group)
    anim_groups_index: IntProperty(name='Active Action Group')

    # Markers
    use_action_names_for_markers: BoolProperty(
        default=False,
        name='Use Action Names',
        description='Use names of referenced actions instead of strip names')

    marker_name_replace: StringProperty(name='Replace')
    marker_name_replace_with: StringProperty(name='With')

    # Action Bake
    action_index: IntProperty(default=0,
                              name='Active Action Index')

    filter_name: StringProperty(options={'TEXTEDIT_UPDATE'},
                                name='Filter by Name',
                                description='Only show items matching this name (use \'*\' as wildcard)')

    bitflag_filter_item = 1 << 30
    only_selected_bones: BoolProperty(default=True)
    visual_keying: BoolProperty(default=True)
    overwrite_current_action: BoolProperty(default=True)
    clean_curves: BoolProperty(default=True)

    use_filter_invert: BoolProperty(default=False,
                                    options={'TEXTEDIT_UPDATE'},
                                    name='Invert',
                                    description='Invert filtering (show hidden items, and vice versa)')

    source_armature: PointerProperty(type=Object,
                                     poll=is_armature_poll,
                                     name='Source Armature',
                                     description='Armature to transfer animations from')

    target_bone_collection: StringProperty(default='RETARGET',
                                           name='Bone Collection',
                                           description='Bone Collection to target on this armature. Animations will be tranferred from source armature onto the selected Bone Collection')


def get_scene_properties(context: Context) -> DLG_PG_scene_properties:
    return getattr(context.scene, 'dlg_props')


def filter_actions(filter_name: str, items: list[Any]) -> list[int]:
    bitflag_filter_item = 1 << 30
    flt_flags = [bitflag_filter_item] * len(items)

    if filter_name:
        for i, item in enumerate(items):
            if not fnmatch(item.action.name, f'*{filter_name}*'):
                flt_flags[i] &= ~bitflag_filter_item

    return flt_flags


_classes= (
    DLG_PG_action_group_item,
    DLG_PG_action_group,
    DLG_PG_scene_properties
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
