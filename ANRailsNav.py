import os
import glob
import sublime
import sublime_plugin


class RailsMixin:
    def show_files(self, segment):
        self.root = self.rails_root()
        path = self.construct_glob_path(segment)
        start_index = len(self.root) + 1

        self.files = glob.glob(path)
        relative_paths = map(lambda x: x[start_index:], self.files)
        self.view.window().show_quick_panel(relative_paths, self.file_selected)

    def rails_root(self):
        directory = self.view.window().folders()[0]
        while directory:
            if os.path.exists(os.path.join(directory, 'Gemfile')):
                return directory
            parent = os.path.realpath(os.path.join(directory, os.path.pardir))
            if parent == directory:
                # /.. == /
                return False
            directory = parent
        return False

    def construct_glob_path(self, segment):
        return os.path.join(self.root, 'app', segment, '*.rb')

    def file_selected(self, selected_index):
        self.view.window().open_file(self.files[selected_index])


class ListRailsModelsCommand(sublime_plugin.TextCommand, RailsMixin):
    def run(self, edit):
        self.show_files('models')


class ListRailsControllersCommand(sublime_plugin.TextCommand, RailsMixin):
    def run(self, edit):
        self.show_files('controllers')
