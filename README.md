# Sublime Text 2 plugin: Simple Rails Navigator

Simple plugin for navigating Ruby on Rails applications.

This plugin provides commands for listing models, controllers, views,
javascript files, or stylesheets in a quick panel for easy selection.

Related files are located at the top of the list so that they can be selected
simply by pressing Enter. For instance, if the active view is a Rails model
and you request a list of controllers, the controller corresponding to the
model will be listed at the top, provided that you follow normal Rails
resource conventions with the controller name containing the pluralized
version of the model name (e.g. post.rb and posts_controller.rb).

The plugin was inspired by Luqman Amjad's Rails Related Files plugin. These
plugins have complementary functionality and can be used together.

## Installation

### Package Control

The easiest way to install this is with [Package
Control](http://wbond.net/sublime\_packages/package\_control).

 * If you just went and installed Package Control, you probably need to restart Sublime Text 2 before doing this next bit.
 * Bring up the Command Palette (Command+Shift+p on OS X, Control+Shift+p on Linux/Windows).
 * Select "Package Control: Install Package" (it'll take a few seconds)
 * Select SublimeRailsNav when the list appears.

Package Control will automatically keep SublimeRailsNav up to date with the latest
version.

### Clone from GitHub

Alternatively, you can clone the repository directly from GitHub into your Packages directory:

    git clone http://github.com/noklesta/SublimeRailsNav

## Key bindings

The plugin does not install any key bindings automatically. You can set up
your own key bindings like this:

    { "keys": ["super+ctrl+m"], "command": "list_rails_models" },
    { "keys": ["super+ctrl+c"], "command": "list_rails_controllers" },
    { "keys": ["super+ctrl+v"], "command": "list_rails_views" },
    { "keys": ["super+ctrl+i"], "command": "list_rails_javascripts" },
    { "keys": ["super+ctrl+y"], "command": "list_rails_stylesheets" }

If you are using Vintage mode and want to use sequences of non-modifier keys,
you can restrict the key bindings to command mode like this:

    { "keys": [" ", "m"], "command": "list_rails_models", "context": [{"key": "setting.command_mode"}] },
    { "keys": [" ", "c"], "command": "list_rails_controllers", "context": [{"key": "setting.command_mode"}] },
    { "keys": [" ", "v"], "command": "list_rails_views", "context": [{"key": "setting.command_mode"}] },
    { "keys": [" ", "i"], "command": "list_rails_javascripts", "context": [{"key": "setting.command_mode"}] },
    { "keys": [" ", "y"], "command": "list_rails_stylesheets", "context": [{"key": "setting.command_mode"}] }

## Settings

The settings in SublimeRailsNav.sublime-settings may be overridden either in
Packages/User/SublimeRailsNav.sublime-settings or, for a particular project, in the
project file under a top-level "settings" key. An example of the latter:

    "settings":
    {
      "SublimeRailsNav":
      {
        "javascript_locations": [
          ["app", "assets", "javascripts"]
        ],
        "stylesheet_locations": [
          ["app", "assets", "stylesheets"],
          ["lib", "assets", "stylesheets"]
        ]
      }
    }

## Credits

- Inspiration from Luqman Amjad's Rails Related Files plugin for ST2.
- Python version of the Rails inflector: <https://bitbucket.org/ixmatus/inflector>
- Contains a modified version of a small code snippet from the Git package for ST2.

## Licence

All of SublimeRailsNav is licensed under the MIT licence.

  Copyright (c) 2012 Anders Nøklestad

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.