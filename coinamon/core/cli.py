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

import argparse
from importlib import import_module


def lookup_command(components, command_name, commands_found=None):
    for component in components:
        try:
            module = import_module("{}.cli".format(component))
            for name in dir(module):
                candidate = getattr(module, name)
                try:
                    if candidate is Command or not issubclass(candidate, Command):
                        continue
                except TypeError:
                    continue

                if candidate.name == command_name:
                    return candidate
                    break
                if commands_found is not None:
                    commands_found[candidate.name] = candidate.label
        except ImportError:
            pass


def run_command(args, components, db_session):
    name = args[1]
    commands_found = {}
    command = lookup_command(components, name, commands_found)
    if command:
        return command(db_session).run(" ".join(args[:2]), args[2:])

    print("Unknown command '{}'. Available commands are:\n".format(name))
    for name in sorted(commands_found):
        print(" *  {} - {}".format(name, commands_found[name]))
    return 1


class Command:
    name = None
    description = None

    def __init__(self, db_session):
        self.db_session = db_session

    def run(self, prog, argv):
        raise NotImplementedError("{}.run not implemented.".format(self.__class__.__name__))


class IntValidator:
    def __init__(self, min_value=None, max_value=None):
        self.min_value, self.max_value = min_value, max_value

    def __call__(self, value):
        try:
            value = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError("'{}' is not a valid integer.".format(value))
        if self.min_value is not None and value < self.min_value:
            raise argparse.ArgumentTypeError(
                "Value must be equal to {} or greater, but {} is not.".format(
                    self.min_value, value))
        if self.max_value is not None and value > self.max_value:
            raise argparse.ArgumentTypeError(
                "Value must be equal to {} or lesser, but {} is not.".format(
                    self.max_value, value))
        return value


def str_not_empty(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("Empty string not allowed.")
    return value
