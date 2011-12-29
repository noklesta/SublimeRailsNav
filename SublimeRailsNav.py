import os
import sublime
import sublime_plugin
from recursive_glob import rglob


class RailsMixin:
    def get_setting(self, key):
        settings = None
        view = self.window.active_view()

        if view:
            settings = self.window.active_view().settings()

        if settings and settings.has('SublimeRailsNav') and key in settings.get('SublimeRailsNav'):
            # Get project-specific setting
            dirs = settings.get('SublimeRailsNav')[key]
        else:
            # Get user-specific or default setting
            settings = sublime.load_settings('SublimeRailsNav.sublime-settings')
            dirs = settings.get(key)
        return dirs

    def show_files(self, segment_groups, file_pattern='\.rb$'):
        self.root = self.rails_root()
        if not self.root:
            sublime.error_message('No Gemfile found. Not a Rails 3 application?')
            return False

        start_index = len(self.root) + 1
        paths = self.construct_glob_paths(segment_groups)

        self.files = []
        for path in paths:
            self.files.extend(rglob(path, file_pattern))

        # Need to add a couple of spaces to avoid getting the file names cut off
        relative_paths = map(lambda x: x[start_index:] + '  ', self.files)

        self.window.show_quick_panel(relative_paths, self.file_selected)

    def rails_root(self):
        directory = self.window.folders()[0]
        while directory:
            if os.path.exists(os.path.join(directory, 'Gemfile')):
                return directory
            parent = os.path.realpath(os.path.join(directory, os.path.pardir))
            if parent == directory:
                # /.. == /
                return False
            directory = parent
        return False

    def construct_glob_paths(self, segment_groups):
        paths = []
        for segment_group in segment_groups:
            paths.append(os.path.join(self.root, *segment_group))
        return paths

    def file_selected(self, selected_index):
        if selected_index != -1:
            self.window.open_file(self.files[selected_index])


class ListRailsModelsCommand(sublime_plugin.WindowCommand, RailsMixin):
    def run(self):
        self.show_files([['app', 'models']])


class ListRailsControllersCommand(sublime_plugin.WindowCommand, RailsMixin):
    def run(self):
        self.show_files([['app', 'controllers']])


class ListRailsViewsCommand(sublime_plugin.WindowCommand, RailsMixin):
    def run(self):
        self.show_files([['app', 'views']], '\.(?:erb|haml)$')


class ListRailsJavascriptsCommand(sublime_plugin.WindowCommand, RailsMixin):
    def run(self):
        dirs = self.get_setting('javascript_locations')
        self.show_files(dirs, '\.(?:js|coffee|erb)$')


class ListRailsStylesheetsCommand(sublime_plugin.WindowCommand, RailsMixin):
    def run(self):
        dirs = self.get_setting('stylesheet_locations')
        self.show_files(dirs, '\.(?:s?css)$')
