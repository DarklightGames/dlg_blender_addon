import bpy
from bpy.types import PropertyGroup, Action, UIList, Panel, Operator, UI_UL_list, bpy_prop_collection, Object
from bpy.props import IntProperty, PointerProperty, StringProperty, BoolProperty
from typing import List


def is_armature_poll(self, object: Object) -> bool:
    return object.type == 'ARMATURE'


def filter_actions_by_name(actions: bpy_prop_collection) -> List[int]:
    pg = bpy.context.scene.dlg_anim_bake_props
    filter_name = pg.filter_name
    bitflag = pg.bitflag_filter_item
    use_filter_invert = pg.use_filter_invert

    if filter_name:
        return UI_UL_list.filter_items_by_name(filter_name, bitflag, actions, 'name', reverse=use_filter_invert)

    return [bitflag] * len(actions)


def select_visible_actions(actions: bpy_prop_collection) -> None:
    "Select all items visible in the action list. Selection on hidden items (filtered out) is preserved"
    filter_flags = filter_actions_by_name(actions=actions)
    for i, flag in enumerate(filter_flags):
        if not actions[i].dlg_is_selected:
            actions[i].dlg_is_selected = bool(flag & bpy.context.scene.dlg_anim_bake_props.bitflag_filter_item)


def deselect_all_actions(actions: bpy_prop_collection) -> None:
    "Deselect all actions including actions that were filtered out."
    for act in actions:
        act.dlg_is_selected = False


def bake_action(action: Action) -> None:
    print(action)

    pg = bpy.context.scene.dlg_anim_bake_props
    source_ao = pg.source_armature
    target_ao = bpy.context.object
    source_ao.animation_data.action = target_ao.animation_data.action = action
    action_frame_start, action_frame_end = action.frame_range

    bpy.ops.nla.bake(frame_start=action_frame_start,
                        frame_end=action_frame_end, 
                        step=1, 
                        only_selected=True, 
                        visual_keying=True, 
                        clear_constraints=False, 
                        clear_parents=False, 
                        use_current_action=True, 
                        clean_curves=True, 
                        bake_types={'POSE'})


def bake_selected_actions() -> None:
    for action in filter(lambda a: a.dlg_is_selected, bpy.data.actions):
        bake_action(action)


class DlgAnimationBakingPropertyGroup(PropertyGroup):
    action_index: IntProperty(default=0)
    only_selected_bones: BoolProperty(default=True)
    visual_keying: BoolProperty(default=True)
    overwrite_current_action: BoolProperty(default=True)
    clean_curves: BoolProperty(default=True)
    filter_name: StringProperty(options={'TEXTEDIT_UPDATE'})
    use_filter_invert: BoolProperty(default=False, options={'TEXTEDIT_UPDATE'})
    bitflag_filter_item = 1 << 30
    source_armature: PointerProperty(type=Object, poll=is_armature_poll)


class DLG_PT_AnimationBaking(Panel):
    bl_label = 'Animation Baking'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DLG Tools'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pg = scene.dlg_anim_bake_props

        # Source/target armature objects
        ao_split = layout.split(factor=0.2)
        ao_left_col = ao_split.column()
        ao_left_col.label(text=f'Source')
        ao_left_col.label(text=f'Target')
        ao_right_col = ao_split.column()
        ao_right_col.prop_search(pg, 'source_armature', context.scene, 'objects', text='', icon='OUTLINER_OB_ARMATURE')
        ao_right_col.label(text=context.object.name, icon='OUTLINER_OB_ARMATURE')

        layout.separator()

        selection_row = layout.row(align=True)
        selection_row.label(text=f'Select')
        selection_row.operator(DLG_OP_SelectVisibleActions.bl_idname, text=f'Visible')
        selection_row.operator(DLG_OP_DeselectAllActions.bl_idname, text=f'None')

        action_list_row = layout.row()
        action_list_row.template_list('DLG_UL_ActionList', '', bpy.data, 'actions', pg, 'action_index', rows=10)

        bake_button_row = layout.row()
        bake_button_row.operator(DLG_OP_BakeActions.bl_idname, text=f'Bake Actions')

        # debug_row = layout.row()
        # debug_row.operator(DLG_OP_debug_test.bl_idname, text=f'DEBUG TEST')


class DLG_UL_ActionList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.alignment = 'LEFT'
        layout.prop(item, 'dlg_is_selected', icon_only=True)
        layout.label(text=item.name)

    def draw_filter(self, context, layout):
        pg = context.scene.dlg_anim_bake_props

        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(pg, 'filter_name', text='')
        subrow.prop(pg, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')

    def filter_items(self, context, data, property):
        actions = getattr(data, property)
        filter_flags = filter_actions_by_name(actions)
        filter_neworder = bpy.types.UI_UL_list.sort_items_by_name(actions, 'name')

        return filter_flags, filter_neworder


class DLG_OP_BakeActions(Operator):
    bl_idname = 'dlg_anim_bake.bake_actions'
    bl_label = 'Bakey Bakey'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        bake_selected_actions()
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


class DLG_OP_DebugTest(Operator):
    bl_idname = 'dlg_anim_bake.debug_test'
    bl_label = 'Debug Test'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        pg = context.scene.dlg_anim_bake_props
        source_ao = pg.source_armature
        target_ao = context.object
        print('Source Armature:', source_ao)
        print('Source AnimData:', source_ao.animation_data)
        print('Target Armature:', target_ao)
        print('Target AnimData:', target_ao.animation_data)
        return {'FINISHED'}


__classes__ = [
    DlgAnimationBakingPropertyGroup,
    DLG_PT_AnimationBaking,
    DLG_UL_ActionList,
    DLG_OP_BakeActions,
    DLG_OP_SelectVisibleActions,
    DLG_OP_DeselectAllActions,
    DLG_OP_DebugTest
]
