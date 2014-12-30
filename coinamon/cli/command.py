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
import sys

from coinamon import importer


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


class ImportContactsCommand(Command):
    name = "import_contacts"
    label = "Import addresses to your list of contacts"

    def __init__(self):
        super().__init__()
        self.importers = importers = {}
        base_class_name = "ContactsImporter"
        base_class = getattr(importer, base_class_name)
        for name in dir(importer):
            if name != base_class_name:
                candidate_class = getattr(importer, name)
                try:
                    if not issubclass(candidate_class, base_class):
                        continue
                except TypeError:
                    continue
                importers[candidate_class.name] = candidate_class()

    def run(self, prog, argv):
        try:
            importer_name = argv[0]
        except IndexError:
            print("You must specify an importer name")
            return 1

        importers = {}
        base_class_name = "ContactsImporter"
        base_class = getattr(importer, base_class_name)
        for name in dir(importer):
            if name != base_class_name:
                candidate = getattr(importer, name)
                try:
                    if not issubclass(candidate, base_class):
                        continue
                except TypeError:
                    continue

                if candidate.name == importer_name:
                    break
                importers[candidate.name] = candidate.label
        else:
            print("Unknown importer '{}'. Available importers are:\n".format(importer_name))
            for name in sorted(importers):
                print(" *  {} - {}".format(name, importers[name]))
            return 1

        print("Paste data and hit Ctrl-D\n")
        data = sys.stdin.read()
        print("")
        try:
            unique = candidate().import_contacts(data)
            if unique:
                print("Imported addresses:\n")
                for label, address in unique:
                    print("{}    {}".format(address, label or ""))
            return 0
        except (importer.PartialImportError, importer.CompleteImportError) as e:
            print("Import Failure")
            if e.unique:
                print("\nImported addresses:\n")
                for label, address in e.unique:
                    print("{}    {}".format(address, label or ""))
            if e.duplicate:
                print("\nDuplicate addresses (not imported):\n")
                for label, address in e.duplicate:
                    print("{}    {}".format(address, label or ""))
            if e.errors:
                print("\nParsing errors:\n")
                for label, address in e.errors:
                    print("{}    {}".format(address, label or ""))
            return 2 if isinstance(e, importer.PartialImportError) else 3
