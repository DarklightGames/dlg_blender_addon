import bpy
from bpy.types import Panel, Operator

class DLG_PT_Markers(Panel):
    bl_label = 'Markers'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'DLG Tools'

    def draw(self, context):
        props = context.scene.dlg_props
        layout = self.layout

        layout.prop(props, 'marker_name_replace')
        layout.prop(props, 'marker_name_replace_with')
        layout.operator(DLG_OP_CreateMarkers.bl_idname)
        layout.operator(DLG_OP_ClearAllMarkers.bl_idname)


class DLG_OP_GenerateMarkers(Operator):
    bl_idname = 'dlg_action_groups.generate_markers'
    bl_label = 'Generate For Selected Track'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        ad = context.object.animation_data
        timeline_markers = context.scene.timeline_markers
        selected_nla_tracks = [*filter(lambda x: x.select, ad.nla_tracks)]

        for nla_track in selected_nla_tracks:
            for strip in nla_track.strips:
                marker_name=strip.name.replace(props.marker_name_replace, props.marker_name_replace_with)
                timeline_markers.new(marker_name, frame=strip.frame_start)

        return {'FINISHED'}


class DLG_OP_ClearAllMarkers(Operator):
    bl_idname = 'dlg_action_groups.clear_all_markers'
    bl_label = 'Clear All'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        context.scene.timeline_markers.clear()
        return {'FINISHED'}


__classes__ = [
    DLG_PT_Markers,
    DLG_OP_GenerateMarkers,
    DLG_OP_ClearAllMarkers
]
