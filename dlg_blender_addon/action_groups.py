import bpy
from bpy.types import PropertyGroup, Action, Panel, UIList, Operator
from bpy.props import StringProperty, PointerProperty, CollectionProperty, BoolProperty, IntProperty
from . import action_group_props as ag_popup


class DLG_PT_ActionGroups(Panel):
    bl_label = 'Action Groups'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'DLG Tools'

    def draw(self, context):
        props = context.scene.dlg_props
        layout = self.layout

        anim_group_row = layout.row()
        anim_group_row.template_list( 'DLG_UL_ActionGroupList', '', props, 'anim_groups', props, 'anim_groups_index', rows=5)

        anim_group_control_col = anim_group_row.column()

        anim_group_control_col.operator( DLG_OP_AddActionGroup.bl_idname, text='', icon='ADD')
        anim_group_control_col.operator( DLG_OP_RemoveActionGroup.bl_idname, text='', icon='REMOVE')

        anim_group_control_col.separator()

        anim_group_control_col.operator( ag_popup.DLG_OP_EditActionGroup.bl_idname, text='', icon='PREFERENCES')
        anim_group_control_col.operator( DLG_OP_PushDownActionGroup.bl_idname, text='', icon='NLA_PUSHDOWN')


class DLG_UL_ActionGroupList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        item_label = '{name} [{actions}]'.format(name=item.name, actions=len(item.actions))
        layout.alignment = 'LEFT'
        layout.label(text=item_label)

    def draw_filter(self, context, layout):
        return


class DLG_OP_AddActionGroup(Operator):
    bl_idname = 'dlg_action_group.add_group'
    bl_label = 'Add Action Group'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        props.anim_groups.add()

        return {'FINISHED'}


class DLG_OP_RemoveActionGroup(Operator):
    bl_idname = 'dlg_action_groups.remove_group'
    bl_label = 'Remove Animation Group'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        props.anim_groups.remove(props.anim_groups_index)

        return {'FINISHED'}


class DLG_OP_PushDownActionGroup(Operator):
    bl_idname = 'dlg_action_groups.push_down_group'
    bl_label = 'Push Down Animation Group'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        anim_data = context.object.animation_data
        nla_tracks = anim_data.nla_tracks
        action_group = props.get_selected_anim_group()

        if not anim_data:
            return {'FINISHED'}

        track = nla_tracks.new()
        track.name = action_group.name

        next_strip_frame = 0

        for action_item in action_group.actions:
            action = action_item.action
            strip = track.strips.new(
                name=action.name,
                start=int(next_strip_frame),
                action=action)

            action_frame_start, action_frame_end = action.frame_range
            next_strip_frame += action_frame_end - action_frame_start + action_group.gap_frames

        return {'FINISHED'}


__classes__ = [
    DLG_PT_ActionGroups,
    DLG_UL_ActionGroupList,
    DLG_OP_AddActionGroup,
    DLG_OP_RemoveActionGroup,
    DLG_OP_PushDownActionGroup
]
