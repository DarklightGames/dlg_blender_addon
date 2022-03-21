
import bpy
from bpy.types import Action, Operator, UIList

class DLG_UL_ActionListLeft(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.alignment = 'LEFT'
        layout.label(text=item.name)


class DLG_UL_ActionListRight(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        print(item, item.action, item.action.name)
        layout.alignment = 'LEFT'
        layout.label(text=item.action.name)


class DLG_OP_EditActionGroup(Operator):
    bl_idname = 'dlg_action_groups.edit_group'
    bl_label = 'Edit Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        pg = context.scene.dlg_props
        pg.edit_anim_group = pg.get_selected_anim_group()
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        pg = context.scene.dlg_props
        anim_group = pg.get_selected_anim_group()

        layout = self.layout
        layout.prop(anim_group, 'name')
        layout.prop(anim_group, 'gap_frames')
        layout.prop(anim_group, 'actions')

        row = layout.row()

        left_col = row.column()
        left_col.template_list('DLG_UL_ActionListLeft', '', bpy.data,
                               'actions', anim_group, 'actions_index_left', rows=10)

        control_col = row.column(align=True)
        control_col.operator(DLG_OP_AddActionToGroup.bl_idname, text='', icon='TRIA_RIGHT')
        control_col.operator(DLG_OP_RemoveActionFromGroup.bl_idname, text='', icon='TRIA_LEFT')

        right_col = row.column()
        right_col.template_list('DLG_UL_ActionListRight', '', anim_group,
                                'actions', anim_group, 'actions_index_right', rows=10)


class DLG_OP_AddActionToGroup(Operator):
    bl_idname = 'dlg_action_groups.add_action'
    bl_label = 'Add to Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    def get_selected_action(self, context) -> Action:
        action_group = context.scene.dlg_props.get_selected_anim_group()
        return action_group.get_selected_action_left()

    @classmethod
    def poll(self, context):
        return bool(bpy.data.actions)

    def execute(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()
        action_item = action_group.actions.add()
        action_item.action = action_group.get_selected_action_left()

        return {'FINISHED'}


class DLG_OP_RemoveActionFromGroup(Operator):
    bl_idname = 'dlg_action_groups.remove_action'
    bl_label = 'Remove from Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()

        return bool(action_group.actions)

    def execute(self, context):
        pg = context.scene.dlg_props
        action_group = pg.get_selected_anim_group()
        action_group.actions.remove(action_group.actions_index_right)
        
        return {'FINISHED'}


__classes__ = [
    DLG_OP_EditActionGroup,
    DLG_UL_ActionListLeft,
    DLG_UL_ActionListRight,
    DLG_OP_AddActionToGroup,
    DLG_OP_RemoveActionFromGroup
]