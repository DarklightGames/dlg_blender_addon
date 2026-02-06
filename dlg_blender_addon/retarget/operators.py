import bpy
from bpy.types import Action, UIList, Panel, Operator, UI_UL_list, bpy_prop_collection, Object, PoseBone, BoneCollection, PoseBone
from typing import Any, cast
from collections.abc import Sequence


def filter_actions_by_name(actions: bpy_prop_collection) -> list[int]:
    pg = bpy.context.scene.dlg_props
    filter_name = pg.filter_name
    bitflag = pg.bitflag_filter_item
    use_filter_invert = pg.use_filter_invert

    filter_flags = [bitflag] * len(actions)

    if filter_name:
        filter_flags = UI_UL_list.filter_items_by_name(filter_name, bitflag, actions, 'name', reverse=use_filter_invert)

    for (i, action) in enumerate(actions):
        if action.library is not None or action.asset_data is not None:
            filter_flags[i] &= ~bitflag

    return filter_flags


def set_pose_bone_selection(bone: PoseBone | None, value: bool) -> None:
    if not bone:
        return

    if bpy.app.version < (5, 0, 0):
        bone.bone.select = value  # pyright: ignore[reportAttributeAccessIssue]
    else:
        bone.select = value


def deselect_all_bones() -> None:
    for bone in cast(Sequence[PoseBone], bpy.context.selected_pose_bones):
        set_pose_bone_selection(bone, False)


def select_bone_collection(object: Object, collection_name: str) -> None:
    "Select all bones in a collection recursively (including child collections)"
    pg = bpy.context.scene.dlg_props

    try:
        bone_collection: BoneCollection = object.data.collections_all[collection_name]
    except KeyError:
        return

    for bone in bone_collection.bones_recursive:
        pose_bone = object.pose.bones[bone.name]
        set_pose_bone_selection(pose_bone, True)


def select_visible_actions(actions: bpy_prop_collection) -> None:
    "Select all items visible in the action list. Selection on hidden items (filtered out) is preserved"
    filter_flags = filter_actions_by_name(actions=actions)
    for i, flag in enumerate(filter_flags):
        # Do not select it if it is linked from another file.
        if actions[i].asset_data is not None:
            continue
        if not actions[i].dlg_is_selected:
            actions[i].dlg_is_selected = bool(
                flag & bpy.context.scene.dlg_props.bitflag_filter_item)


def deselect_all_actions(actions: bpy_prop_collection) -> None:
    "Deselect all actions including actions that were filtered out."
    for act in actions:
        act.dlg_is_selected = False


def set_action(object: Object, action: Action) -> None:
    anim_data = object.animation_data
    anim_data.action = action

    if hasattr(anim_data, 'action_slot'):
        anim_data.action_slot = anim_data.action_suitable_slots[0]


def mute_nla_tracks(object: Object) -> dict[str, bool]:
    "Mute all NLA tracks and return previous mute state."
    mute_state = {}

    for track in object.animation_data.nla_tracks:
        mute_state.update({track.name: track.mute})
        track.mute = True

    return mute_state


def apply_nla_mute_state(object: Object, mute_state: dict[str, bool]):
    "Mute/unmute NLA tracks from a dictionary"

    tracks = object.animation_data.nla_tracks
    for track in tracks:
        try:
            track.mute = mute_state[track.name]
        except KeyError:
            pass


def bake_action(action: Action) -> None:
    print('Baking {}'.format(action.name))

    pg = bpy.context.scene.dlg_props
    source_obj = pg.source_armature
    target_obj = bpy.context.object
    action_frame_start, action_frame_end = action.frame_range

    mute_state = mute_nla_tracks(target_obj)

    set_action(source_obj, action)
    set_action(target_obj, action)

    deselect_all_bones()
    select_bone_collection(target_obj, pg.target_bone_collection)

    bpy.ops.nla.bake(frame_start=int(action_frame_start),
                     frame_end=int(action_frame_end),
                     step=1,
                     only_selected=True,
                     visual_keying=True,
                     clear_constraints=False,
                     clear_parents=False,
                     use_current_action=True,
                     clean_curves=True,
                     bake_types={'POSE'})

    apply_nla_mute_state(target_obj, mute_state)


def bake_selected_actions() -> None:
    actions_to_bake = list(filter(lambda a: a.dlg_is_selected, bpy.data.actions))
    bpy.context.window_manager.progress_begin(0, len(actions_to_bake))
    for i, action in enumerate(actions_to_bake):
        bake_action(action)
        bpy.context.window_manager.progress_update(i)
    bpy.context.window_manager.progress_end()


def run_property_automations_on_bone(bone: PoseBone, autoprop_dict: dict[str, Any], old_props: dict[str, Any] = {}) -> None:
    for i, (key, value) in enumerate(autoprop_dict.items()):
        try:
            if value != bone[key]:
                print(f'Auto-prop: Setting {key} to {value} on bone {bone.name}')
                old_props[key] = bone[key]
                bone[key] = value

        except KeyError as err:
            print(f'Auto-prop failed: {err}')


def run_all_property_automations(autoprop_dict_name: str, old_props: dict[PoseBone, dict[str, Any]] = {}) -> None:
    for bone in bpy.context.object.pose.bones:
        try:
            old_bone_props = {}
            run_property_automations_on_bone(bone, bone[autoprop_dict_name], old_bone_props)
            old_props[bone] = old_bone_props
        except KeyError:
            pass


class DLG_OT_actions_retarget(Operator):
    bl_idname = 'dlg_retarget.actions_retarget'
    bl_label = 'Retarget Selected Actions'
    bl_description = 'Transfer animations from a source armature to targetted bones'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene.dlg_props.source_armature is None:
            cls.poll_message_set('No source armature selected')
            return False

        if not context.scene.dlg_props.target_bone_collection in context.object.data.collections_all:
            cls.poll_message_set('No valid bone collection selected')
            return False

        return True

    def execute(self, context):
        old_props = {}
        run_all_property_automations('_autoprop', old_props)

        bake_selected_actions()

        for bone in old_props:
            run_property_automations_on_bone(bone, old_props[bone])

        deselect_all_actions(bpy.data.actions)

        return {'FINISHED'}


class DLG_OT_actions_select_visible(Operator):
    bl_idname = 'dlg_retarget.actions_select_visible'
    bl_label = 'Select All Visible'
    bl_description = 'Select all visible actions'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        select_visible_actions(bpy.data.actions)
        return {'FINISHED'}


class DLG_OT_actions_deselect_all(Operator):
    bl_idname = 'dlg_retarget.actions_deselect_all'
    bl_label = 'Select None'
    bl_description = 'Deselect all actions (including hidden)'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        deselect_all_actions(bpy.data.actions)
        return {'FINISHED'}


class DLG_OP_target_bones_add(Operator):
    bl_idname = 'dlg_retarget.target_bones_add'
    bl_label = 'Add Target Bones'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        pg = context.scene.dlg_props
        sel_bones = context.selected_pose_bones
        added_bones = 0

        for bone in sel_bones:
            if any(x.name == bone.name for x in pg.target_bones):
                print('Bone {} is already on the list.'.format(bone.name))
            else:
                target_bone = pg.target_bones.add()
                target_bone.name = bone.name
                added_bones += 1
                print('Added bone {}'.format(bone.name))

        if added_bones > 0:
            self.report({'INFO'}, 'Added {bone_count} target bone{s}.'.format(bone_count=added_bones, s='s' if added_bones > 1 else ''))

        return {'FINISHED'}


class DLG_OT_target_bones_clear(Operator):
    bl_idname = 'dlg_retarget.target_bones_clear'
    bl_label = 'Clear Target Bones'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        pg = context.scene.dlg_props
        pg.target_bones.clear()

        self.report({'INFO'}, 'Cleared all target bones')

        return {'FINISHED'}


_classes = (
    DLG_OP_target_bones_add,
    DLG_OT_target_bones_clear,
    DLG_OT_actions_retarget,
    DLG_OT_actions_select_visible,
    DLG_OT_actions_deselect_all
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
