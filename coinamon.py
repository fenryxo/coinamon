#!/usr/bin/python3
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

import os.path
import sys

from coinamon.db import bind_engine
from coinamon.db import db_session

bind_engine('sqlite:///' + os.path.join(os.path.abspath("."), "db.sqlite"), echo=False)

if len(sys.argv) > 1:
    command_name = sys.argv[1]
    from coinamon import cli as module
    commands = {}
    base_class_name = "Command"
    base_class = getattr(module, base_class_name)
    for name in dir(module):
        if name != base_class_name:
            candidate = getattr(module, name)
            try:
                if not issubclass(candidate, base_class):
                    continue
            except TypeError:
                continue

            if candidate.name == command_name:
                sys.exit(candidate().run(sys.argv[2:]))
                break
            commands[candidate.name] = candidate.label

    print("Unknown command '{}'. Available commands are:\n".format(command_name))
    for name in sorted(commands):
        print(" *  {} - {}".format(name, commands[name]))

else:
    from coinamon.application import Application
    app = Application(db_session)
    sys.exit(app.run(sys.argv))
