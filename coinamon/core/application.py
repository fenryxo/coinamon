# coding: utf-8

# Copyright 2014 Jiří Janoušek <janousek.jiri@gmail.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from gi.repository import Gio
from gi.repository import Gtk


class Application(Gtk.Application):
    def __init__(self, components, db_session):
        Gtk.Application.__init__(
            self, application_id="eu.tiliado.Coinamon", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.components = components
        self.db_session = db_session
        self.window = None
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        if self.window:
            self.window.present()
            return

        from coinamon.core.gui import MainWindow
        from importlib import import_module

        self.window = window = MainWindow()
        app.add_window(window)

        modules = []
        for component in self.components:
            try:
                module = import_module("{}.gui".format(component))
                modules.append(module)
                if hasattr(module, "add_views"):
                    module.add_views(app, window)
            except ImportError as e:
                print(e)

        for module in modules:
            if hasattr(module, "add_actions"):
                module.add_actions(app, window)

        window.present()
