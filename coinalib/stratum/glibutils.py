# coding: utf-8

# Copyright 2015 Jiří Janoušek <janousek.jiri@gmail.com>
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

import traceback

from gi.repository import GLib


class MainLoopWrapper:
    def __init__(self):
        self._loop = None

    def run(self):
        if self._loop:
            raise RuntimeError("Loop is already running.")

        self._loop = GLib.MainLoop()
        self._loop.run()

    def stop(self):
        if not self._loop:
            raise RuntimeError("Loop isn't running.")

        self._loop.quit()
        self._loop = None

    def call_soon_threadsafe(self, func, *args, **kwargs):
        return self.call_soon(func, *args, **kwargs)

    def call_soon(self, func, *args, **kwargs):
        def callback(func, *args2, **kwargs2):
            try:
                func(*args2, **kwargs2)
            except Exception:
                traceback.print_exc()
            return False

        GLib.idle_add(callback, func, *args, **kwargs)

    def call_later(self, delay, func, *args, **kwargs):
        def callback(func, *args2, **kwargs2):
            try:
                func(*args2, **kwargs2)
            except Exception:
                traceback.print_exc()
            return False

        GLib.timeout_add_seconds(delay, callback, func, *args, **kwargs)

    def create_child(self):
        return self.__class__()
