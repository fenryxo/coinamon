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
        if not self.window:
            self._init_core()
            self._init_ui()
            self._load_components()

        self.window.present()

    def _init_core(self):
        from coinalib import blockexplorers
        from coinalib.stratum import client
        from coinalib.stratum import glibutils
        from coinalib.stratum import peers
        from coinalib.stratum import transports

        self.block_explorer = blockexplorers.Blocktrail()
        loop = glibutils.MainLoopWrapper()
        peer_list = peers.PeerList(peers.PeerList.parse(peers.DEFAULT_PEERS))
        self.transport_pool = transports.TransportPool(peer_list)
        self.electrum = client.StratumClient(self.transport_pool, loop)
        self.electrum.start()

    def _init_ui(self):
        from coinamon.core.gui import MainWindow

        self.window = MainWindow()
        self.add_window(self.window)

    def _load_components(self):
        from importlib import import_module

        modules = []
        for component in self.components:
            try:
                module = import_module("{}.gui".format(component))
                modules.append(module)
                if hasattr(module, "add_views"):
                    module.add_views(self, self.window)
            except ImportError as e:
                print(e)

        for module in modules:
            if hasattr(module, "add_actions"):
                module.add_actions(self, self.window)
