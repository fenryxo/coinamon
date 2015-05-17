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

import datetime

from gi.repository import GLib
from gi.repository import Gtk

import coinagtk
from coinalib import bitcoin
import coinamon.core.gui.view


def add_views(app, window):
    view = BlockHeadersView(app.block_explorer)
    window.add_view(view, False)

    def on_response(response, error, view, *args, **kwargs):
        view.add_block_header(bitcoin.BlockHeader(**response.response))

    def on_notification(notification, view, *args, **kwargs):
        view.add_block_header(bitcoin.BlockHeader(**notification.params[0]))

    def on_new_transport(client, transport, view):
        app.electrum.send_request_async(method, params, on_response, view)

    method = "blockchain.headers.subscribe"
    params = []
    app.electrum.notifications[method].connect(on_notification, view)
    app.electrum.connection_established.connect(on_new_transport, view)
    if app.electrum.is_connection_established:
        app.electrum.send_request_async(method, params, on_response, view)


def add_actions(app, window):
    pass


class BlockHeadersView(coinamon.core.gui.view.View):

    def __init__(self, block_explorer):
        widget = grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, row_spacing=10, margin=10)
        super().__init__("blockheaders", "New Blocks", widget)
        self.block_explorer = block_explorer
        self.list_box = list_box = Gtk.ListBox()
        scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
        scroll.add(list_box)
        grid.add(scroll)
        grid.show_all()

    def add_block_header(self, block_header):
        label_grid = Gtk.Grid(
            column_spacing=10, orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.START, hexpand=True)
        label_grid.add(Gtk.Label("<b>Height</b>", use_markup=True))
        label_grid.add(Gtk.Label(str(block_header.block_height)))
        label_grid.add(Gtk.Label("<b>Time</b>", use_markup=True))
        local_datetime = block_header.datetime.replace(tzinfo=datetime.timezone.utc).astimezone()
        label_grid.add(Gtk.Label(str(local_datetime)))
        label_grid.add(Gtk.LinkButton(
            self.block_explorer.block_info(block_header.hash_hex),
            "Explore"))
        label_grid.show_all()

        hash_label = Gtk.Label(
            "<b>Hash</b> {}".format(GLib.markup_escape_text(block_header.hash_hex)),
            use_markup=True)
        hash_label.show()

        expander = coinagtk.Expander.new()
        expander = coinagtk.Expander(label_widget=label_grid)
        expander.add(hash_label)
        expander.show()
        self.list_box.prepend(expander)
