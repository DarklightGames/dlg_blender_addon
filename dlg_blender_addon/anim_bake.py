import bpy
from bpy.types import Action, UIList, Panel, Operator, UI_UL_list, bpy_prop_collection, Object, PoseBone
from typing import List, Dict, Any


def deselect_all_bones() -> None:
    for pose_bone in bpy.context.selected_pose_bones:
        pose_bone.bone.select = False


def select_bone(object: Object, name: str) -> None:
    pose_bone = object.pose.bones[name]
    if pose_bone:
        pose_bone.bone.select = True


def select_target_bones(object: Object) -> None:
    pg = bpy.context.scene.dlg_props

    for bone in pg.target_bones:
        select_bone(object, bone.name)


def filter_actions_by_name(actions: bpy_prop_collection) -> List[int]:
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


def bake_action(action: Action) -> None:
    print('Baking {}'.format(action.name))

    pg = bpy.context.scene.dlg_props
    source_ao = pg.source_armature
    target_ao = bpy.context.object
    source_ao.animation_data.action = target_ao.animation_data.action = action
    action_frame_start, action_frame_end = action.frame_range

    deselect_all_bones()
    select_target_bones(target_ao)

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


def bake_selected_actions() -> None:
    actions_to_bake = list(filter(lambda a: a.dlg_is_selected, bpy.data.actions))
    bpy.context.window_manager.progress_begin(0, len(actions_to_bake))
    for i, action in enumerate(actions_to_bake):
        bake_action(action)
        bpy.context.window_manager.progress_update(i)
    bpy.context.window_manager.progress_end()


def run_property_automations_on_bone(bone: PoseBone, autoprop_dict: Dict[str, Any], old_props: Dict[str, Any] = {}) -> None:
    for i, (key, value) in enumerate(autoprop_dict.items()):
        try:
            if value != bone[key]:
                print(f'Auto-prop: Setting {key} to {value} on bone {bone.name}')
                old_props[key] = bone[key]
                bone[key] = value

        except KeyError as err:
            print(f'Auto-prop failed: {err}')


def run_all_property_automations(autoprop_dict_name: str, old_props: Dict[PoseBone, Dict[str, Any]] = {}) -> None:
    for bone in bpy.context.object.pose.bones:
        try:
            old_bone_props = {}
            run_property_automations_on_bone(bone, bone[autoprop_dict_name], old_bone_props)
            old_props[bone] = old_bone_props
        except KeyError:
            pass


class DLG_PT_AnimationBaking(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_category = 'Darklight Animation Baker'
    bl_label = 'Darklight Animation Baker'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active.mode == 'POSE' 

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pg = scene.dlg_props
        ob = context.object

        # Source/target armature objects
        ao_split = layout.split(factor=0.2)
        ao_left_col = ao_split.column()
        ao_left_col.label(text=f'Source')
        ao_right_col = ao_split.column()
        ao_right_col.prop_search(
            pg, 'source_armature', context.scene, 'objects', text='', icon='OUTLINER_OB_ARMATURE')

        layout.separator()

        # Bones
        selected_pose_bones = context.selected_pose_bones
        pose_bones = ob.pose.bones
        
        layout.label(text='Target Bones: {}'.format(len(pg.target_bones)), icon='BONE_DATA')

        set_bones_row = layout.row(align=True)
        set_bones_row.operator(
            DLG_OP_AddTargetBones.bl_idname, 
            text='Add ({})'.format(len(selected_pose_bones)), 
            icon='ADD')
        set_bones_row.operator(
            DLG_OP_ClearTargetBones.bl_idname, 
            text='Clear', 
            icon='REMOVE')

        layout.separator()

        # Selection buttons
        selection_row = layout.row(align=True)
        selection_row.label(text=f'Select')
        selection_row.operator(
            DLG_OP_SelectVisibleActions.bl_idname, text=f'All', icon='CHECKBOX_HLT')
        selection_row.operator(
            DLG_OP_DeselectAllActions.bl_idname, text=f'None', icon='CHECKBOX_DEHLT')

        # Action list
        action_list_row = layout.row()
        action_list_row.template_list(
            'DLG_UL_ActionList', '', bpy.data, 'actions', pg, 'action_index', rows=10)

        # Controls
        bake_button_row = layout.row()
        bake_button_row.operator(DLG_OP_BakeActions.bl_idname, text=f'Bake Actions')

        # debug_row = layout.row()
        # debug_row.operator(DLG_OP_DebugTest.bl_idname, text=f'DEBUG TEST')


class DLG_UL_ActionList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.alignment = 'LEFT'
        layout.prop(item, 'dlg_is_selected', icon_only=True)
        layout.label(text=item.name)

    def draw_filter(self, context, layout):
        pg = context.scene.dlg_props

        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(pg, 'filter_name', text='')
        subrow.prop(pg, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')

    def filter_items(self, context, data, property):
        actions = getattr(data, property)
        filter_flags = filter_actions_by_name(actions)
        filter_neworder = bpy.types.UI_UL_list.sort_items_by_name(
            actions, 'name')

        return filter_flags, filter_neworder


class DLG_OP_BakeActions(Operator):
    bl_idname = 'dlg_anim_bake.bake_actions'
    bl_label = 'Bakey Bakey'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene.dlg_props.source_armature is None:
            cls.poll_message_set('No source armature selected')
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


class DLG_OP_SelectVisibleActions(Operator):
    bl_idname = 'dlg_anim_bake.select_visible_actions'
    bl_label = 'Select All'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        select_visible_actions(bpy.data.actions)
        return {'FINISHED'}


class DLG_OP_DeselectAllActions(Operator):
    bl_idname = 'dlg_anim_bake.deselect_all_actions'
    bl_label = 'Select None'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        deselect_all_actions(bpy.data.actions)
        return {'FINISHED'}


class DLG_OP_AddTargetBones(Operator):
    bl_idname = 'dlg_anim_bake.add_target_bones'
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


class DLG_OP_ClearTargetBones(Operator):
    bl_idname = 'dlg_anim_bake.clear_target_bones'
    bl_label = 'Clear Target Bones'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        pg = context.scene.dlg_props
        pg.target_bones.clear()

        self.report({'INFO'}, 'Cleared all target bones')

        return {'FINISHED'}


class DLG_OP_DebugTest(Operator):
    bl_idname = 'dlg_anim_bake.debug_test'
    bl_label = 'Debug Test'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


__classes__ = [
    DLG_OP_AddTargetBones,
    DLG_OP_ClearTargetBones,
    DLG_PT_AnimationBaking,
    DLG_UL_ActionList,
    DLG_OP_BakeActions,
    DLG_OP_SelectVisibleActions,
    DLG_OP_DeselectAllActions,
    DLG_OP_DebugTest
]
