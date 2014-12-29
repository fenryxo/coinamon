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

from coinamon.cli import Command
from coinamon.models import Group


class ListGroupsCommand(Command):
    name = "list_groups"
    label = "List groups of your list of contacts"

    def run(self, prog, args):
        parser = argparse.ArgumentParser(prog, description=self.label)
        parser.add_argument(
            '-i', '--show-id', action='store_true', default=False,
            help='Print also id of groups')
        parser.add_argument(
            '-g', '--group', metavar="GROUP_ID", type=int,
            help='Start from given group instead of a root')
        args = parser.parse_args(args)

        with self.db_session() as dbs:
            for level, group in Group.walk_tree(dbs, args.group):
                if args.show_id:
                    print("{}{: 2d} {}".format("    " * level, group.id, group.name))
                else:
                    print("{}+ {}".format("    " * level, group.name))


class ListContactsCommand(Command):
    name = "list_contacts"
    label = "List your contacts"

    def run(self, prog, args):
        parser = argparse.ArgumentParser(prog, description=self.label)
        parser.add_argument(
            '-i', '--show-id', action='store_true', default=False,
            help='Print also id of groups')
        args = parser.parse_args(args)

        with self.db_session() as dbs:
            for level, group, addr in Group.walk_tree(dbs, addresses=True):
                if group:
                    if args.show_id:
                        print("{}+ {} #{}".format("  " * level, group.name, group.id))
                    else:
                        print("{}+ {}".format("  " * level, group.name))
                elif addr:
                    print("{}- {} {}".format("  " * level, addr.id, addr.label))
