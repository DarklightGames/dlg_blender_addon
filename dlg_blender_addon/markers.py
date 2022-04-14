import bpy
from typing import Iterable
from bpy.types import Panel, Operator, NlaStrip


def get_marker_name(strip: NlaStrip) -> str:
    props = bpy.context.scene.dlg_props
    name = strip.action.name if props.use_action_names_for_markers else strip.name

    return name.replace(props.marker_name_replace, props.marker_name_replace_with)


def generate_markers(strips: Iterable[NlaStrip]) -> None:
    timeline_markers = bpy.context.scene.timeline_markers

    for strip in strips:
        timeline_markers.new(get_marker_name(strip), frame=int(strip.frame_start))


class DLG_PT_Markers(Panel):
    bl_label = 'Markers'
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'DLG Tools'

    def draw(self, context):
        props = context.scene.dlg_props
        layout = self.layout

        layout.prop(props, 'use_action_names_for_markers')
        layout.prop(props, 'marker_name_replace')
        layout.prop(props, 'marker_name_replace_with')
        layout.separator()
        layout.operator(DLG_OP_GenerateMarkersForTracks.bl_idname, text='Generate for Tracks')
        layout.operator(DLG_OP_GenerateMarkersForStrips.bl_idname, text='Generate for Strips')
        layout.operator(DLG_OP_ClearAllMarkers.bl_idname, text='Clear All')


class DLG_OP_GenerateMarkersForTracks(Operator):
    bl_idname = 'dlg_action_groups.generate_markers_for_track'
    bl_label = 'Generate Markers for Tracks'
    bl_description = 'Generate timeline markers for strips on selected NLA tracks'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        ad = context.object.animation_data
        selected_nla_tracks = [*filter(lambda x: x.select, ad.nla_tracks)]

        for nla_track in selected_nla_tracks:
            generate_markers(nla_track.strips)

        return {'FINISHED'}


class DLG_OP_GenerateMarkersForStrips(Operator):
    bl_idname = 'dlg_action_groups.generate_markers_for_strips'
    bl_label = 'Generate Markers for Strips'
    bl_description = 'Generate timeline markers for selected strips'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        generate_markers(context.selected_nla_strips)
        
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
