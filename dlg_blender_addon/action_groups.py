from bpy.props import StringProperty, BoolProperty
from bpy.types import Panel, UIList, Operator, Menu
from . import action_group_props as ag_popup
import re


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

        anim_group_control_col.operator(DLG_OP_AddActionGroup.bl_idname, text='', icon='ADD')
        anim_group_control_col.operator(DLG_OP_RemoveActionGroup.bl_idname, text='', icon='REMOVE')

        anim_group_control_col.separator()

        anim_group_control_col.operator(ag_popup.DLG_OP_EditActionGroup.bl_idname, text='', icon='PREFERENCES')
        anim_group_control_col.operator(DLG_OP_PushDownActionGroup.bl_idname, text='', icon='NLA_PUSHDOWN')

        anim_group_control_col.separator()

        anim_group_control_col.menu(DLG_MT_ActionGroupMenu.bl_idname, text='', icon='DOWNARROW_HLT')

        # anim_group_control_col.operator(DLG_OT_rename_selected_nla_strips.bl_idname, text='', icon='TRIA_RIGHT')


class DLG_UL_ActionGroupList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        # Have the name take up as much space as possible, and align the count to the right.
        row = layout.row()
        row.prop(item, 'name', text='', emboss=False)
        row.label(text=str(len(item.actions)), icon='ACTION')

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

    @classmethod
    def poll(cls, context):
        if context.object is None:
            cls.poll_message_set('No object selected')
            return False
        if context.active_nla_track is None:
            cls.poll_message_set('No NLA track selected')
            return False
        return True

    def execute(self, context):
        props = context.scene.dlg_props
        anim_data = context.object.animation_data
        action_group = props.get_selected_anim_group()

        if not anim_data:
            return {'FINISHED'}

        # Get the selected NLA track.
        track = context.active_nla_track
        next_strip_frame = context.scene.frame_current

        for action_item in action_group.actions:
            action = action_item.action
            track.strips.new(
                name=action.name,
                start=int(next_strip_frame),
                action=action)

            action_frame_start, action_frame_end = action.frame_range
            next_strip_frame += action_frame_end - action_frame_start + action_group.gap_frames

        return {'FINISHED'}


class DLG_MT_ActionGroupMenu(Menu):
    bl_idname = 'DLG_MT_ActionGroupMenu'
    bl_label = 'Action Group Menu'

    def draw(self, context):
        layout = self.layout

        layout.operator(DLG_OT_rename_selected_nla_strips.bl_idname)


class DLG_OT_rename_selected_nla_strips(Operator):
    bl_idname = 'dlg_action_groups.rename_selected_nla_strips'
    bl_label = 'Rename Selected NLA Strips'
    bl_options = {'INTERNAL', 'UNDO'}

    find_pattern: StringProperty(name='Find', description='Regular expression pattern to find')
    replace: StringProperty(name='Replace', description='Text to replace the found pattern with')
    dry: BoolProperty(name='Dry Run', default=True, description='Do not apply changes, but show what would be changed')

    @classmethod
    def poll(cls, context):
        if len(context.selected_nla_strips) == 0:
            cls.poll_message_set('No NLA strips selected')
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Get selected NLA strips.
        try:
            regex = re.compile(self.find_pattern)
        except re.error as e:
            self.report({'ERROR_INVALID_INPUT'}, str(e))
            return {'CANCELLED'}

        count = 0
        for strip in context.selected_nla_strips:
            # Check if the pattern is found in the strip name.
            if not regex.search(strip.name):
                continue
            new_strip_name = regex.sub(self.replace, strip.name)
            if self.dry:
                print(f'{strip.name} -> {regex.sub(self.replace, strip.name)}')
            else:
                strip.name = new_strip_name
            count += 1

        if self.dry:
            self.report({'INFO'}, f'{count} NLA strips would be renamed')

        return {'FINISHED'}


__classes__ = [
    DLG_PT_ActionGroups,
    DLG_UL_ActionGroupList,
    DLG_OP_AddActionGroup,
    DLG_OP_RemoveActionGroup,
    DLG_OP_PushDownActionGroup,
    DLG_OT_rename_selected_nla_strips,
    DLG_MT_ActionGroupMenu,
]
