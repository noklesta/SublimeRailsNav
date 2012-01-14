import os
import re
import sublime
import sublime_plugin
from recursive_glob import rglob
from lib.inflector import *


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
            sublime.error_message('No Rails root directory found. Not a Rails application?')
            return False

        paths = self.construct_glob_paths(segment_groups)
        self.find_files(paths, file_pattern)

        view = self.window.active_view()
        if view:
            current_file = view.file_name()
            if self.is_listing_current_file_group(current_file):
                self.remove_from_list(current_file)
            else:
                self.move_related_file_to_top(current_file)

        start_index = len(self.root) + 1
        # Need to add a couple of spaces to avoid getting the file names cut off
        relative_paths = map(lambda x: x[start_index:] + '  ', self.files)

        self.window.show_quick_panel(relative_paths, self.file_selected)

    def rails_root(self):
        # Look for a Gemfile first, since that should always be found in the
        # root directory of a Rails 3 project. If no Gemfile is found, we
        # might have a Rails 2 (or earlier) project, so look for a Rakefile
        # instead. However, since Rakefiles may be found in subdirectories as
        # well, in that case we also check for a number for additional
        # standard Rails directories.
        for root_indicator in ['Gemfile', 'Rakefile']:
            folders = self.window.folders()
            if len(folders) == 0:
                return False

            directory = folders[0]
            while directory:
                if os.path.exists(os.path.join(directory, root_indicator)):
                    if root_indicator == 'Gemfile':
                        return directory
                    else:
                        looks_like_root = True
                        for additional_dir in ['app', 'config', 'lib', 'vendor']:
                            if not (os.path.exists(os.path.join(directory, additional_dir))):
                                looks_like_root = False
                                break
                        if looks_like_root:
                            return directory

                parent = os.path.realpath(os.path.join(directory, os.path.pardir))
                if parent == directory:
                    # /.. == /
                    break
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

    def find_files(self, paths, file_pattern):
        self.files = []
        for path in paths:
            self.files.extend(rglob(path, file_pattern))

    def remove_from_list(self, current_file):
        # First check to see if the current file is in the list. For instance,
        # if the current file is under vendor/assets/javascripts and we did
        # not include that among the javascript locations that we list,
        # the current file will not in fact be there.
        if current_file in self.files:
            self.files.remove(current_file)
            pass

    def move_related_file_to_top(self, current_file):
        related_file = self.construct_related_file_name(current_file)

        if related_file:
            for file in self.files:
                if file == related_file:
                    i = self.files.index(file)
                    self.files.insert(0, self.files.pop(i))


class RailsCommandBase(sublime_plugin.WindowCommand, RailsMixin):
    MODEL_SEGMENT = os.path.join('app', 'models')
    CONTROLLER_SEGMENT = os.path.join('app', 'controllers')
    VIEW_SEGMENT = os.path.join('app', 'views')

    def construct_related_file_name(self, current_file):
        pass


class ListRailsModelsCommand(RailsCommandBase):
    def run(self):
        self.show_files([['app', 'models']])

    def construct_related_file_name(self, current_file):
        if self.CONTROLLER_SEGMENT in current_file:
            m = re.search(r'(\w+)_controller\.\w+$', current_file)
            singular = Inflector().singularize(m.group(1))

            related_file = re.sub(self.CONTROLLER_SEGMENT, self.MODEL_SEGMENT, current_file)
            related_file = re.sub(r'\w+_controller(\.\w+$)', '%s\g<1>' % singular, related_file)
            return related_file
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return 'app/models' in current_file


class ListRailsControllersCommand(RailsCommandBase):
    def run(self):
        self.show_files([['app', 'controllers']])

    def construct_related_file_name(self, current_file):
        if self.MODEL_SEGMENT in current_file:
            m = re.search(r'(\w+)\.\w+$', current_file)
            plural = Inflector().pluralize(m.group(1))

            related_file = re.sub(self.MODEL_SEGMENT, self.CONTROLLER_SEGMENT, current_file)
            related_file = re.sub(r'\w+(\.\w+)$', '%s_controller\g<1>' % plural, related_file)
            return related_file
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return 'app/controllers' in current_file


class ListRailsViewsCommand(RailsCommandBase):
    def run(self):
        self.show_files([['app', 'views']], '\.(?:erb|haml)$')

    def is_listing_current_file_group(self, current_file):
        return 'app/views' in current_file


class ListRailsJavascriptsCommand(RailsCommandBase):
    def run(self):
        dirs = self.get_setting('javascript_locations')
        self.show_files(dirs, '\.(?:js|coffee|erb)$')

    def is_listing_current_file_group(self, current_file):
        return 'javascripts' in current_file


class ListRailsStylesheetsCommand(RailsCommandBase):
    def run(self):
        dirs = self.get_setting('stylesheet_locations')
        self.show_files(dirs, '\.(?:s?css)$')

    def is_listing_current_file_group(self, current_file):
        return 'stylesheets' in current_file
