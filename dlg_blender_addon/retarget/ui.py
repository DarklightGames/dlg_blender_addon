
import bpy
from bpy.types import UIList, Panel, bpy_prop_collection
from . import operators as ops


class DLG_PT_retarget(Panel):
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
        label_split_factor = 0.34

        # Source/target armature objects
        ao_split = layout.split(factor=label_split_factor)
        ao_left_col = ao_split.column().label(text=f'Source Armature')
        ao_right_col = ao_split.column().prop_search(
            pg, 'source_armature', context.scene, 'objects', text='', icon='OUTLINER_OB_ARMATURE')

        # Bones
        bones_split = layout.split(factor=label_split_factor)
        bones_left_col = bones_split.column().label(text=f'Target Bones')
        bones_right_col = bones_split.column().prop_search(
            pg, 'target_bone_collection', ob.data, 'collections_all', text='', icon='GROUP_BONE')

        layout.separator()

        # Selection buttons
        selection_row = layout.row(align=True)
        selection_row.label(text=f'Select')
        selection_row.operator(
            ops.DLG_OT_actions_select_visible.bl_idname, text=f'Visible', icon='CHECKBOX_HLT')
        selection_row.operator(
            ops.DLG_OT_actions_deselect_all.bl_idname, text=f'None', icon='CHECKBOX_DEHLT')

        # Action list
        action_list_row = layout.row()
        action_list_row.template_list(
            'DLG_UL_retarget_action_list', '', bpy.data, 'actions', pg, 'action_index', rows=10)

        # Controls
        bake_button_row = layout.row()
        bake_button_row.operator(ops.DLG_OT_actions_retarget.bl_idname, text=f'Bake Actions')

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
    DLG_PT_retarget,
    DLG_UL_retarget_action_list
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
