
from bpy.types import Panel, UIList, Menu, Context, bpy_prop_array

from ..properties import DLG_PG_action_group, get_scene_properties, filter_actions
from . import operators as ops


class DLG_PT_actions(Panel):
    bl_label = 'Add Actions'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        props = get_scene_properties(context)

        layout = self.layout
        if layout == None:
            return

        row = layout.row()

        # ACTION GROUPS

        col = row.column()
        col.template_list('DLG_UL_action_group_list', '', props, 'anim_groups', props, 'anim_groups_index', rows=5)


        # SIDE CONTROLS

        col = row.column()

        button_stack = col.column(align=True)
        button_stack.operator(ops.DLG_OT_action_group_add.bl_idname, text='', icon='ADD')
        button_stack.operator(ops.DLG_OT_action_group_remove.bl_idname, text='', icon='REMOVE')

        col.separator()

        col.operator(ops.DLG_OT_action_group_edit.bl_idname, text='', icon='PREFERENCES')

        col.separator()

        col.menu(DLG_MT_add_actions_context_menu.bl_idname, text='', icon='DOWNARROW_HLT')

        # PUSH BUTTON
        row = layout.row(align=True)
        row.operator(ops.DLG_OT_action_group_push.bl_idname, text='Add to Selected Track', icon='NLA_PUSHDOWN')


class DLG_UL_action_group_list(UIList):
    def draw_item(self, context, layout, data, item: DLG_PG_action_group | None, icon, active_data, active_property, index, flt_flag):
        split = layout.split(align=True, factor=0.7)

        # ACTION GROUP NAME
        row = split.row(align=True)
        row.alignment = 'LEFT'
        row.prop(item, 'name', text='', emboss=False)

        # ACTION COUNTER
        row = split.row(align=True)
        row.alignment = 'RIGHT'

        if item:
            row.label(text=str(len(item.actions)), icon='ACTION')

    def draw_filter(self, context, layout):
        return


class DLG_UL_action_list_mixin(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):
        split = layout.split(align=True, factor=1.0)
        column = split.row(align=True)
        column.alignment = 'LEFT'
        column.prop(item, 'is_selected', icon_only=True)
        column.label(text=item.action.name)


class DLG_UL_data_action_list(DLG_UL_action_list_mixin):
    def filter_items(self, context, data, prop):
        pg = get_scene_properties(context)
        items = pg.data_action_group_items
        flt_flags = filter_actions(self.filter_name, items)
        flt_neworder = list(range(len(items)))
        return flt_flags, flt_neworder


class DLG_UL_action_list(DLG_UL_action_list_mixin):
    pass


class DLG_MT_add_actions_context_menu(Menu):
    bl_idname = 'DLG_MT_ActionGroupMenu'
    bl_label = 'Action Group Menu'

    def draw(self, context: Context):
        if self.layout is None:
            return

        self.layout.operator(ops.DLG_OT_rename_selected_nla_strips.bl_idname)


class DLG_PT_markers(Panel):
    bl_label = 'Add Markers'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        props = context.scene.dlg_props
        layout = self.layout

        layout.prop(props, 'use_action_names_for_markers')
        layout.prop(props, 'marker_name_replace')
        layout.prop(props, 'marker_name_replace_with')
        layout.separator()
        layout.operator(ops.DLG_OT_markers_push_tracks.bl_idname, icon='SEQ_STRIP_DUPLICATE')
        layout.operator(ops.DLG_OT_markers_push_strips.bl_idname, icon='SEQ_STRIP_META')
        layout.operator(ops.DLG_OT_markers_clear_all.bl_idname, text='Clear All', icon='TRASH')


_classes = (
    DLG_PT_actions,
    DLG_UL_data_action_list,
    DLG_UL_action_list,
    DLG_UL_action_group_list,
    DLG_MT_add_actions_context_menu,
    DLG_PT_markers
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
