import bpy
from bpy.types import Operator, NlaStrip
from bpy.props import EnumProperty, StringProperty, BoolProperty

from ..properties import get_scene_properties

from collections.abc import Iterable
from re import (
    compile as regex_comp,
    error as regex_err
)


def get_marker_name(strip: NlaStrip) -> str:
    props = bpy.context.scene.dlg_props
    name = strip.action.name if props.use_action_names_for_markers else strip.name

    return name.replace(props.marker_name_replace, props.marker_name_replace_with)


def generate_markers(strips: Iterable[NlaStrip]) -> None:
    timeline_markers = bpy.context.scene.timeline_markers

    for strip in strips:
        timeline_markers.new(get_marker_name(strip), frame=int(strip.frame_start))


class DLG_OT_action_group_add(Operator):
    bl_idname = 'dlg_nla.action_group_add'
    bl_label = 'Add Action Group'
    bl_description = 'Create a new action group. Actions can be added to this group and pushed to NLA track in a batch'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = get_scene_properties(context)
        props.anim_groups.add()
        props.anim_groups_index = len(props.anim_groups) - 1

        return {'FINISHED'}


class DLG_OT_action_group_remove(Operator):
    bl_idname = 'dlg_nla.action_group_remove'
    bl_label = 'Remove Action Group'
    bl_description = 'Remove the active action group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not get_scene_properties(context):
            cls.poll_message_set('No action group selected')
            return False

        return True

    def execute(self, context):
        props = get_scene_properties(context)
        props.anim_groups.remove(props.anim_groups_index)

        if props.anim_groups_index >= len(props.anim_groups):
            props.anim_groups_index = len(props.anim_groups) - 1

        return {'FINISHED'}


class DLG_OT_action_group_push(Operator):
    bl_idname = 'dlg_nla.action_group_push'
    bl_label = 'Add Actions to Selected Track'
    bl_description = 'Add actions in the active group to the selected NLA track'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.object is None:
            cls.poll_message_set('No object selected')
            return False

        if context.active_nla_track is None:
            cls.poll_message_set('No NLA track selected')
            return False

        if not get_scene_properties(context).is_anim_group_selected():
            cls.poll_message_set('No action group selected')
            return False

        return True

    def execute(self, context):
        props = get_scene_properties(context)

        if not context.object:
            self.report({'ERROR'}, f'No object')
            return {'CANCELLED'}

        anim_data = context.object.animation_data

        if not anim_data:
            self.report({'ERROR'}, f'No animation data')
            return {'CANCELLED'}

        scene = context.scene

        if not scene:
            self.report({'ERROR'}, f'No scene')
            return {'CANCELLED'}

        action_group = props.get_selected_anim_group()

        # Get the selected NLA track.
        track = context.active_nla_track
        next_strip_frame: int = getattr(context.scene, 'frame_current')

        push_count = 0

        try:
            for action_item in action_group.actions:
                action = action_item.action

                # TODO: Push to the end of the track
                track.strips.new(
                    name=action.name,
                    start=int(next_strip_frame),
                    action=action)

                push_count += 1

                action_frame_start, action_frame_end = action.frame_range
                next_strip_frame += action_frame_end - action_frame_start + action_group.gap_frames

        except BaseException as e:
            self.report({'ERROR'}, str(e))

        if push_count < 0:
            self.report({'INFO'}, f'No NLA strips were added')
            return {'CANCELLED'}

        self.report({'INFO'}, f'Added {push_count} NLA strips')
        return {'FINISHED'}


class DLG_OT_action_group_edit(Operator):
    bl_idname = 'dlg_nla.action_group_edit'
    bl_label = 'Edit Action Group'
    bl_description = 'Edit selected action group (add/remove actions, change name and other properties)'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if not get_scene_properties(context).is_anim_group_selected():
            cls.poll_message_set('No action group selected')
            return False

        return True

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        pg = get_scene_properties(context)
        pg.data_action_group_items.clear()

        for action in bpy.data.actions:
            item = pg.data_action_group_items.add()
            item.action = action

        if context.window_manager is None:
            raise TypeError

        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        pg = get_scene_properties(context)
        anim_group = pg.get_selected_anim_group()
        layout = self.layout

        if layout is None:
            return

        # ACTION LISTS
        row = layout.row()
        left_col = row.column()
        left_col.template_list('DLG_UL_data_action_list', '', pg,
                               'data_action_group_items', pg, 'data_action_group_items_index', rows=10)

        control_col = row.column(align=True)

        control_col.operator(DLG_OT_action_add.bl_idname, text='', icon='TRIA_RIGHT')
        control_col.operator(DLG_OT_action_remove.bl_idname, text='', icon='TRIA_LEFT')
        control_col.separator()
        control_col.operator(DLG_OT_action_move.bl_idname, text='', icon='TRIA_UP').direction = 'UP'
        control_col.operator(DLG_OT_action_move.bl_idname, text='', icon='TRIA_DOWN').direction = 'DOWN'

        right_col = row.column()
        right_col.template_list('DLG_UL_action_list', '', anim_group,
                                'actions', anim_group, 'actions_index_right', rows=10)

        layout.separator()

        # PROPERTIES
        col = layout.column(align=True)
        col.use_property_split = True
        col.use_property_decorate = False
        col.prop(anim_group, 'name')
        col.prop(anim_group, 'gap_frames')

        layout.separator()


class DLG_OT_action_add(Operator):
    bl_idname = 'dlg_nla.action_add'
    bl_label = 'Add to Action Group'
    bl_description = 'Add selected actions to the action group. These actions will be added as NLA strips when action group is pushed to NLA track'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if any actions are selected.
        pg = get_scene_properties(context)

        for item in pg.data_action_group_items:
            if item.is_selected:
                return True

        cls.poll_message_set('No actions selected')

        return False

    def execute(self, context):
        pg = get_scene_properties(context)

        for i in reversed(range(len(pg.data_action_group_items))):
            item = pg.data_action_group_items[i]
            if item.is_selected:
                action_group = pg.get_selected_anim_group()
                action_item = action_group.actions.add()
                action_item.action = item.action
                item.is_selected = False

        return {'FINISHED'}


class DLG_OT_action_remove(Operator):
    bl_idname = 'dlg_nla.action_remove'
    bl_label = 'Remove from Action Group'
    bl_description = 'Remove selected actions from the action group'
    bl_options = {'INTERNAL', 'UNDO'}

    @classmethod
    def poll(cls, context):
        pg = get_scene_properties(context)
        action_group = pg.get_selected_anim_group()

        for item in action_group.actions:
            if item.is_selected:
                return True

        cls.poll_message_set('No actions selected')
        return False

    def execute(self, context):
        pg = get_scene_properties(context)
        action_group = pg.get_selected_anim_group()

        for i in reversed(range(len(action_group.actions))):
            item = action_group.actions[i]
            if item.is_selected:
                action_group.actions.remove(i)

        return {'FINISHED'}


class DLG_OT_action_move(Operator):
    bl_idname = 'dlg_nla.action_move'
    bl_label = 'Move Action'
    bl_description = 'Change position of actions in the group'
    bl_options = {'INTERNAL', 'UNDO'}

    direction: EnumProperty(
        name='Move Direction',
        items=(
            ('UP','Up', ''),
            ('DOWN', 'Down', '')
        ),
        default='UP',
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        ag = get_scene_properties(context).get_selected_anim_group()
        return len(ag.actions) > 1

    def execute(self, context):
        props = get_scene_properties(context)
        ag = props.get_selected_anim_group()

        active_index = ag.actions_index_right
        new_index = active_index + (-1 if self.direction == 'UP' else 1)

        if 0 <= new_index < len(ag.actions):
            ag.actions.move(active_index, new_index)
            ag.actions_index_right = new_index

        return {'FINISHED'}


class DLG_OT_rename_selected_nla_strips(Operator):
    bl_idname = 'dlg_nla.rename_selected_nla_strips'
    bl_label = 'Rename Selected NLA Strips'
    bl_options = {'INTERNAL', 'UNDO'}

    find_pattern: StringProperty(
        name='Find',
        description='Regular expression pattern to find'
    )

    replace: StringProperty(
        name='Replace',
        description='Text to replace the found pattern with'
    )

    dry: BoolProperty(
        name='Dry Run',
        default=True,
        description='Do not apply changes, but show what would be changed'
    )

    @classmethod
    def poll(cls, context):
        if len(context.selected_nla_strips) == 0:
            cls.poll_message_set('No NLA strips selected')
            return False

        return True

    def invoke(self, context, event):
        if context.window_manager is None:
            raise TypeError

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        # Get selected NLA strips.
        try:
            regex = regex_comp(self.find_pattern)
        except regex_err as e:
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


class DLG_OT_markers_push_tracks(Operator):
    bl_idname = 'dlg_nla.generate_markers_for_track'
    bl_label = 'Mark Strips on Selected Tracks'
    bl_description = 'Generate timeline markers for strips on selected NLA tracks'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        ad = context.object.animation_data
        selected_nla_tracks = [*filter(lambda x: x.select, ad.nla_tracks)]

        for nla_track in selected_nla_tracks:
            generate_markers(nla_track.strips)

        return {'FINISHED'}


class DLG_OT_markers_push_strips(Operator):
    bl_idname = 'dlg_nla.generate_markers_for_strips'
    bl_label = 'Mark Selected Strips'
    bl_description = 'Generate timeline markers for selected strips'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        generate_markers(context.selected_nla_strips)

        return {'FINISHED'}


class DLG_OT_markers_clear_all(Operator):
    bl_idname = 'dlg_nla.clear_all_markers'
    bl_label = 'Clear All'
    bl_label = 'Remove all markers from the NLA editor'
    bl_options = {'INTERNAL', 'UNDO'}

    def execute(self, context):
        context.scene.timeline_markers.clear()
        return {'FINISHED'}


_classes= (
    DLG_OT_action_group_add,
    DLG_OT_action_group_remove,
    DLG_OT_action_group_push,
    DLG_OT_action_group_edit,
    DLG_OT_action_add,
    DLG_OT_action_remove,
    DLG_OT_action_move,
    DLG_OT_rename_selected_nla_strips,
    DLG_OT_markers_push_tracks,
    DLG_OT_markers_push_strips,
    DLG_OT_markers_clear_all
)


from bpy.utils import register_classes_factory
register, unregister = register_classes_factory(_classes)
