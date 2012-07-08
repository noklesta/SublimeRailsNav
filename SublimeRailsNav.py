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

    def show_files(self, dirs, file_pattern='\.rb$'):
        paths = self.construct_glob_paths(dirs)
        self.find_files(paths, file_pattern)

        view = self.window.active_view()
        if view:
            current_file = view.file_name()
            if self.is_listing_current_file_group(current_file):
                self.remove_from_list(current_file)
            else:
                self.move_related_files_to_top(current_file)

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

    def construct_glob_paths(self, dirs):
        paths = []
        for dir in dirs:
            paths.append(os.path.join(self.root, *dir))
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

    def move_related_files_to_top(self, current_file):
        related_file_name_pattern = self.construct_related_file_name_pattern(current_file)

        if related_file_name_pattern:
            for file in self.files:
                if re.search(related_file_name_pattern, file):
                    i = self.files.index(file)
                    self.files.insert(0, self.files.pop(i))


class RailsCommandBase(sublime_plugin.WindowCommand, RailsMixin):
    MODEL_DIR = os.path.join('app', 'models')
    CONTROLLER_DIR = os.path.join('app', 'controllers')
    VIEW_DIR = os.path.join('app', 'views')
    HELPER_DIR = os.path.join('app', 'helpers')
    FIXTURE_DIR = os.path.join('test', 'fixtures')

    def setup(self):
        self.root = self.rails_root()
        if not self.root:
            sublime.error_message('No Rails root directory found. Not a Rails application?')
            return False

        if os.path.isdir(os.path.join(self.root, 'spec')):
            # RSpec seems to be installed, so ignore the 'test' dir and search for specs
            self.test_type = 'spec'
            self.model_test_dir = os.path.join('spec', 'models')
            self.controller_test_dir = os.path.join('spec', 'controllers')
            self.view_test_dir = os.path.join('spec', 'views')
            self.helper_test_dir = os.path.join('spec', 'helpers')
        else:
            # No RSpec, so use the standard 'test' dir
            self.test_type = 'test'
            self.model_test_dir = os.path.join('test', 'unit')
            self.controller_test_dir = os.path.join('test', 'functional')
            self.helper_test_dir = os.path.join('test', 'unit', 'helpers')
        return True

    def construct_related_file_name_pattern(self, current_file):
        pass


class ListRailsModelsCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        self.show_files([['app', 'models']])

    def construct_related_file_name_pattern(self, current_file):
        if self.CONTROLLER_DIR in current_file:
            m = re.search(r'(\w+)_controller\.\w+$', current_file)
            singular = Inflector().singularize(m.group(1))

            pattern = re.sub(self.CONTROLLER_DIR, self.MODEL_DIR, current_file)
            pattern = re.sub(r'\w+_controller(\.\w+$)', '%s\g<1>' % singular, pattern)
            return pattern
        elif self.FIXTURE_DIR in current_file:
            m = re.search(r'(\w+)\.yml$', current_file)
            singular = Inflector().singularize(m.group(1))

            pattern = re.sub(self.FIXTURE_DIR, self.MODEL_DIR, current_file)
            pattern = re.sub(r'\w+.yml$', '%s.rb' % singular, pattern)
            return pattern
        elif self.model_test_dir in current_file:
            pattern = re.sub(self.model_test_dir, self.MODEL_DIR, current_file)
            pattern = re.sub(r'(_%s)(.\w+)$' % self.test_type, '\g<2>', pattern)
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join('app', 'models') in current_file


class ListRailsControllersCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        self.show_files([['app', 'controllers']])

    def construct_related_file_name_pattern(self, current_file):
        if self.MODEL_DIR in current_file:
            m = re.search(r'(\w+)\.\w+$', current_file)
            plural = Inflector().pluralize(m.group(1))

            pattern = re.sub(self.MODEL_DIR, self.CONTROLLER_DIR, current_file)
            pattern = re.sub(r'\w+(\.\w+)$', '%s_controller\g<1>' % plural, pattern)
            return pattern
        elif self.VIEW_DIR in current_file:
            pattern = re.sub(self.VIEW_DIR, self.CONTROLLER_DIR, current_file)
            pattern = re.sub(os.path.join('', r'(\w+)', r'[\w\.]+$'), '\g<1>_controller', pattern)
            return pattern
        if self.HELPER_DIR in current_file:
            pattern = re.sub(self.HELPER_DIR, self.CONTROLLER_DIR, current_file)
            pattern = re.sub(r'_helper\.rb$', '_controller\.rb', pattern)
            return pattern
        elif self.controller_test_dir in current_file:
            pattern = re.sub(self.controller_test_dir, self.CONTROLLER_DIR, current_file)
            pattern = re.sub(r'(_%s)(.\w+)$' % self.test_type, '\g<2>', pattern)
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join('app', 'controllers') in current_file


class ListRailsViewsCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        self.show_files([['app', 'views']], '\.(?:erb|haml|slim)$')

    def construct_related_file_name_pattern(self, current_file):
        if self.CONTROLLER_DIR in current_file:
            pattern = re.sub(self.CONTROLLER_DIR, self.VIEW_DIR, current_file)
            pattern = re.sub(r'(\w+)_controller\.\w+$', '\g<1>' + os.sep, pattern)
            return pattern
        elif self.test_type == 'test' and self.controller_test_dir in current_file:
            # With Test::Unit, view tests are found in the controller test
            # file, so the best we can do is to show all views for the
            # controller associated with the currently active controller test
            # at the top of the list.
            pattern = re.sub(self.controller_test_dir, self.VIEW_DIR, current_file)
            pattern = re.sub(r'(\w+)_controller_test\.rb$', '\g<1>' + os.sep, pattern)
            return pattern
        elif self.test_type == 'spec' and self.view_test_dir in current_file:
            # RSpec uses separate view specs, so here we can show the
            # particular view associated with the currently active spec at the
            # top of the list.
            pattern = re.sub(self.view_test_dir, self.VIEW_DIR, current_file)
            pattern = re.sub(r'(\w+)\.[\w\.]+$', '\g<1>\.', pattern)
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join('app', 'views') in current_file


class ListRailsHelpersCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        self.show_files([['app', 'helpers']])

    def construct_related_file_name_pattern(self, current_file):
        if self.CONTROLLER_DIR in current_file:
            pattern = re.sub(self.CONTROLLER_DIR, self.HELPER_DIR, current_file)
            pattern = re.sub(r'_controller\.rb$', '_helper\.rb', pattern)
            return pattern
        elif self.helper_test_dir in current_file:
            pattern = re.sub(self.helper_test_dir, self.HELPER_DIR, current_file)
            pattern = re.sub(r'(_%s)(.\w+)$' % self.test_type, '\g<2>', pattern)
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join('app', 'helpers') in current_file


class ListRailsFixturesCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        self.show_files([['test', 'fixtures']], '\.yml$')

    def construct_related_file_name_pattern(self, current_file):
        if self.MODEL_DIR in current_file:
            m = re.search(r'(\w+)\.rb$', current_file)
            plural = Inflector().pluralize(m.group(1))

            pattern = re.sub(self.MODEL_DIR, self.FIXTURE_DIR, current_file)
            pattern = re.sub(r'\w+\.rb$', r'%s\.yml' % plural, pattern)
            return pattern
        elif self.model_test_dir in current_file:
            m = re.search(r'(\w+)_%s\.rb$' % self.test_type, current_file)
            plural = Inflector().pluralize(m.group(1))

            pattern = re.sub(self.model_test_dir, self.FIXTURE_DIR, current_file)
            pattern = re.sub(r'(\w+)_%s\.rb$' % self.test_type, r'%s\.yml' % plural, pattern)
            return pattern
        elif self.controller_test_dir in current_file:
            m = re.search(r'(\w+)_controller_%s\.rb$' % self.test_type, current_file)
            plural = Inflector().pluralize(m.group(1))

            pattern = re.sub(self.controller_test_dir, self.FIXTURE_DIR, current_file)
            pattern = re.sub(r'(\w+)_controller_%s\.rb$' % self.test_type, r'%s\.yml' % plural, pattern)
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join('test', 'fixtures') in current_file


class ListRailsTestsCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return

        self.show_files([[self.test_type]])

    def construct_related_file_name_pattern(self, current_file):
        if self.MODEL_DIR in current_file:
            pattern = re.sub(self.MODEL_DIR, self.model_test_dir, current_file)
            pattern = re.sub(r'(\.\w+)$', '_%s\g<1>' % self.test_type, pattern)
            return pattern
        elif self.CONTROLLER_DIR in current_file:
            pattern = re.sub(self.CONTROLLER_DIR, self.controller_test_dir, current_file)
            pattern = re.sub(r'(\.\w+)$', '_%s\g<1>' % self.test_type, pattern)
            return pattern
        elif self.VIEW_DIR in current_file:
            if self.test_type == 'spec':
                # RSpec uses separate view specs
                pattern = re.sub(self.VIEW_DIR, self.view_test_dir, current_file)
                pattern = re.sub(r'(\w+)\.[\w\.]+$', r'\g<1>[\w\.]*_spec\.rb', pattern)
            else:
                # Test::Unit puts view tests in the controller test file
                pattern = re.sub(self.VIEW_DIR, self.controller_test_dir, current_file)
                pattern = re.sub(r'(\w+)%s[\w\.]+$' % os.sep, '\g<1>_controller_test.rb', pattern)
            return pattern
        elif self.HELPER_DIR in current_file:
            pattern = re.sub(self.HELPER_DIR, self.helper_test_dir, current_file)
            pattern = re.sub(r'\.rb$', r'_%s\.rb' % self.test_type, pattern)
            return pattern
        elif self.FIXTURE_DIR in current_file:
            m = re.search(r'(\w+)\.yml$', current_file)
            singular = Inflector().singularize(m.group(1))

            pattern = re.sub(self.FIXTURE_DIR, r'(?:%s|%s)' % (self.model_test_dir, self.controller_test_dir), current_file)
            pattern = re.sub(r'(\w+)\.yml$', r'(?:\g<1>_controller|%s)_%s\.rb' % (singular, self.test_type), pattern)
            return pattern
        elif 'config/routes.rb' in current_file and self.test_type == 'spec':
            pattern = os.path.join(self.root, 'spec', 'routing', '.+_routing_spec.rb')
            return pattern
        else:
            return None

    def is_listing_current_file_group(self, current_file):
        return os.path.join(self.root, self.test_type) in current_file and not self.FIXTURE_DIR in current_file


class ListRailsJavascriptsCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        dirs = self.get_setting('javascript_locations')
        self.show_files(dirs, '\.(?:js|coffee|erb)$')

    def is_listing_current_file_group(self, current_file):
        return 'javascripts' in current_file


class ListRailsStylesheetsCommand(RailsCommandBase):
    def run(self):
        if not self.setup():
            return
        dirs = self.get_setting('stylesheet_locations')
        self.show_files(dirs, '\.(?:s?css)$')

    def is_listing_current_file_group(self, current_file):
        return 'stylesheets' in current_file
