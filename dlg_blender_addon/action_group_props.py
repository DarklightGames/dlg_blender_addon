from fnmatch import fnmatch
from typing import List

import bpy
from bpy.types import Operator, UIList


def filter_sequences(filter_name: str, items) -> List[int]:
    bitflag_filter_item = 1 << 30
    flt_flags = [bitflag_filter_item] * len(items)

    if filter_name:
        for i, item in enumerate(items):
            if not fnmatch(item.action.name, f'*{filter_name}*'):
                flt_flags[i] &= ~bitflag_filter_item

    return flt_flags


class UIActionList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        split = layout.split(align=True, factor=1.0)
        column = split.row(align=True)
        column.alignment = 'LEFT'
        column.prop(item, 'is_selected', icon_only=True)
        column.label(text=item.action.name)


class DLG_UL_ActionListLeft(UIActionList):
    def filter_items(self, context, data, prop):
        pg = context.scene.dlg_props
        items = pg.data_action_group_items
        flt_flags = filter_sequences(self.filter_name, items)
        flt_neworder = list(range(len(items)))
        return flt_flags, flt_neworder


class DLG_UL_ActionListRight(UIActionList):
    pass


class DLG_OP_EditActionGroup(Operator):
    bl_idname = 'dlg_action_groups.edit_group'
    bl_label = 'Edit Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not context.scene.dlg_props.is_anim_group_selected():
            cls.poll_message_set('No action group selected')
            return False

        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        pg = context.scene.dlg_props
        pg.edit_anim_group = pg.get_selected_anim_group()

        # TODO: populate the actions list with actions that are not already in the group.
        pg.data_action_group_items.clear()
        for action in bpy.data.actions:
            # Check if action is already in the group.
            for item in pg.edit_anim_group.actions:
                if item.action == action:
                    continue
            item = pg.data_action_group_items.add()
            item.action = action

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        pg = context.scene.dlg_props
        anim_group = pg.get_selected_anim_group()

        layout = self.layout
        layout.prop(anim_group, 'name')
        layout.prop(anim_group, 'gap_frames')

        row = layout.row()

        left_col = row.column()
        left_col.template_list('DLG_UL_ActionListLeft', '', pg,
                               'data_action_group_items', pg, 'data_action_group_items_index', rows=10)

        control_col = row.column(align=True)

        control_col.operator(DLG_OP_AddActionToGroup.bl_idname, text='', icon='TRIA_RIGHT')
        control_col.operator(DLG_OP_RemoveActionFromGroup.bl_idname, text='', icon='TRIA_LEFT')
        control_col.separator()
        control_col.operator(DLG_OP_MoveActionUp.bl_idname, text='', icon='TRIA_UP')
        control_col.operator(DLG_OP_MoveActionDown.bl_idname, text='', icon='TRIA_DOWN')

        right_col = row.column()
        right_col.template_list('DLG_UL_ActionListRight', '', anim_group,
                                'actions', anim_group, 'actions_index_right', rows=10)


class DLG_OP_AddActionToGroup(Operator):
    bl_idname = 'dlg_action_groups.add_action'
    bl_label = 'Add to Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if any actions are selected.
        pg = context.scene.dlg_props
        for item in pg.data_action_group_items:
            if item.is_selected:
                return True
        cls.poll_message_set('No actions selected')
        return False

    def execute(self, context):
        pg = context.scene.dlg_props

        for i in reversed(range(len(pg.data_action_group_items))):
            item = pg.data_action_group_items[i]
            if item.is_selected:
                action_group = pg.get_selected_anim_group()
                action_item = action_group.actions.add()
                action_item.action = item.action
                pg.data_action_group_items.remove(i)

        return {'FINISHED'}


class DLG_OP_RemoveActionFromGroup(Operator):
    bl_idname = 'dlg_action_groups.remove_action'
    bl_label = 'Remove from Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()

        for item in action_group.actions:
            if item.is_selected:
                return True

        cls.poll_message_set('No actions selected')
        return False

    def execute(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()

        for i in reversed(range(len(action_group.actions))):
            item = action_group.actions[i]
            if item.is_selected:
                pg.data_action_group_items.add().action = item.action
                action_group.actions.remove(i)

        return {'FINISHED'}


class DLG_OP_MoveActionUp(Operator):
    bl_idname = 'dlg_action_groups.move_action_up'
    bl_label = 'Move Action Up'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(self, context):
        action_group = context.scene.dlg_props.get_selected_anim_group()
        return bool(action_group.actions) and action_group.actions_index_right - 1 >= 0

    def execute(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()
        action_group.move_action_up(action_group.actions_index_right)

        return {'FINISHED'}


class DLG_OP_MoveActionDown(Operator):
    bl_idname = 'dlg_action_groups.move_action_down'
    bl_label = 'Move Action Down'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(self, context):
        try:
            action_group = context.scene.dlg_props.get_selected_anim_group()
            action_group.actions[action_group.actions_index_right + 1]
            return True
        except IndexError:
            return False

    def execute(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()
        action_group.move_action_down(action_group.actions_index_right)

        return {'FINISHED'}


__classes__ = [
    DLG_OP_EditActionGroup,
    DLG_UL_ActionListLeft,
    DLG_UL_ActionListRight,
    DLG_OP_AddActionToGroup,
    DLG_OP_RemoveActionFromGroup,
    DLG_OP_MoveActionUp,
    DLG_OP_MoveActionDown
]
