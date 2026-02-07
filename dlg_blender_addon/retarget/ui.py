
import bpy
from bpy.types import UIList, Panel, bpy_prop_collection
from . import operators as ops


class DLG_PT_retarget_actions(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'
    bl_category = 'Retarget Actions (DLG)'
    bl_label = 'Retarget Actions (DLG)'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.active.mode == 'POSE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pg = scene.dlg_props
        ob = context.object

        # Properties
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop_search(
            pg, 'source_armature', context.scene, 'objects', icon='OUTLINER_OB_ARMATURE')
        col.prop_search(
            pg, 'target_bone_collection', ob.data, 'collections_all', icon='GROUP_BONE')

        layout.separator()

        # Selection buttons
        selection_row = layout.row(align=True)
        selection_row.label(text=f'Select')
        selection_row.operator(
            ops.DLG_OT_retarget_actions_select_visible.bl_idname, text=f'Visible', icon='CHECKBOX_HLT')
        selection_row.operator(
            ops.DLG_OT_retarget_actions_deselect_all.bl_idname, text=f'None', icon='CHECKBOX_DEHLT')

        # Action list
        action_list_row = layout.row()
        action_list_row.template_list(
            'DLG_UL_retarget_action_list', '', bpy.data, 'actions', pg, 'action_index', rows=10)

        # Controls
        bake_button_row = layout.row()
        bake_button_row.operator(ops.DLG_OT_retarget_actions_apply.bl_idname, text=f'Retarget')

        # debug_row = layout.row()
        # debug_row.operator(DLG_OP_DebugTest.bl_idname, text=f'DEBUG TEST')


class DLG_UL_retarget_action_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.alignment = 'LEFT'
        layout.prop(item, 'dlg_is_selected', icon_only=True, text=item.name)

    def draw_filter(self, context, layout):
        pg = context.scene.dlg_props

        row = layout.row()
        subrow = row.row(align=True)
        subrow.prop(pg, 'filter_name', text='')
        subrow.prop(pg, 'use_filter_invert', text='', icon='ARROW_LEFTRIGHT')

    def filter_items(self, context, data, property):
        actions = getattr(data, property)
        filter_flags = ops.filter_actions_by_name(actions)
        filter_neworder = bpy.types.UI_UL_list.sort_items_by_name(
            actions, 'name')

        return filter_flags, filter_neworder


_classes = (
    DLG_PT_retarget_actions,
    DLG_UL_retarget_action_list
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
