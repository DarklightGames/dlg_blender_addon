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
        layout.operator(DLG_OP_GenerateMarkersForTracks.bl_idname, text='Generate for Tracks')
        layout.operator(DLG_OP_GenerateMarkersForStrips.bl_idname, text='Generate for Strips')
        layout.operator(DLG_OP_ClearAllMarkers.bl_idname, text='Clear All')


class DLG_OP_GenerateMarkersForTracks(Operator):
    bl_idname = 'dlg_action_groups.generate_markers_for_track'
    bl_label = 'Generate Markers for Tracks'
    bl_description = 'Generate timeline markers for strips on selected NLA tracks'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        ad = context.object.animation_data
        timeline_markers = context.scene.timeline_markers
        selected_nla_tracks = [*filter(lambda x: x.select, ad.nla_tracks)]

        for nla_track in selected_nla_tracks:
            for strip in nla_track.strips:
                # TODO: refactor duplicate code in DLG_OL_GenerateMarkersForStrips
                marker_name=strip.name.replace(props.marker_name_replace, props.marker_name_replace_with)
                timeline_markers.new(marker_name, frame=int(strip.frame_start))

        return {'FINISHED'}


class DLG_OP_GenerateMarkersForStrips(Operator):
    bl_idname = 'dlg_action_groups.generate_markers_for_strips'
    bl_label = 'Generate Markers for Strips'
    bl_description = 'Generate timeline markers for selected strips'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.dlg_props
        ad = context.object.animation_data
        timeline_markers = context.scene.timeline_markers
        strips = context.selected_nla_strips
        
        for strip in strips:
            # !
            marker_name=strip.name.replace(props.marker_name_replace, props.marker_name_replace_with)
            timeline_markers.new(marker_name, frame=int(strip.frame_start))

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
    DLG_OP_GenerateMarkersForTracks,
    DLG_OP_GenerateMarkersForStrips,
    DLG_OP_ClearAllMarkers
]
