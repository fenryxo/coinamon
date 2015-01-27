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

from gi.repository import Gtk


class DialogMixin:
    def add_button_with_class(self, label, response_id, style_class):
        button = self.add_button(label, response_id)
        if style_class:
            button.get_style_context().add_class(style_class)
        return button


class Dialog(DialogMixin, Gtk.Dialog):
    def __init__(self, parent_window=None, title="", **kwargs):
        try:
            use_header_bar = Gtk.Settings.get_default().get_property("gtk-dialogs-use-header")
            super().__init__(title=title, use_header_bar=use_header_bar, **kwargs)
            self.get_header_bar().set_title(title)
        except TypeError:
            super().__init__(title=title, **kwargs)  # GTK < 3.12

        if parent_window:
            self.set_transient_for(parent_window)


class FormDialog(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.infobar = Gtk.InfoBar(no_show_all=True)
        self.infobar_label = Gtk.Label(visible=True)
        self.infobar.get_content_area().add(self.infobar_label)
        self.get_content_area().add(self.infobar)

    def hide_infobar(self):
        self.infobar.hide()

    def show_infobar(self, text=None, type=None):
        if text is not None:
            self.infobar_label.set_label(text)
        if type is not None:
            self.infobar.set_message_type(type)
        self.infobar.show()

    def show_warning(self, text):
        self.show_infobar(text, Gtk.MessageType.WARNING)

    def show_error(self, text):
        self.show_infobar(text, Gtk.MessageType.ERROR)

    def show_info(self, text):
        self.show_infobar(text, Gtk.MessageType.INFO)
