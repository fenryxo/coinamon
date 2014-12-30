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
import json

from sqlalchemy.exc import IntegrityError

from coinamon.cli import Command
from coinamon.cli.command import IntValidator
from coinamon.cli.command import str_not_empty
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


class DumpContactsCommand(Command):
    name = "dump_contacts"
    label = "Dump contacts as JSON"

    def run(self, prog, args):
        parser = argparse.ArgumentParser(prog, description=self.label)
        parser.add_argument(
            '-c', '--compact', action='store_true', default=False,
            help='Use compact format with less white space.')
        args = parser.parse_args(args)

        groups = []
        contacts = []
        with self.db_session() as dbs:
            for level, group, addr in Group.walk_tree(dbs, addresses=True):
                if group:
                    groups.append(
                        {
                            "id": group.id,
                            "name": group.name
                        })
                elif addr:
                    contacts.append(
                        {
                            "address": addr.id,
                            "label": addr.label,
                            "group_id": addr.group_id
                        })
        data = {"groups": groups, "contacts": contacts}
        if args.compact:
            print(json.dumps(data, separators=(',', ':')))
        else:
            print(json.dumps(data, sort_keys=True, indent=2))


class CreateGroupCommand(Command):
    name = "create_group"
    label = "Crate a new group in your list of contacts"

    def run(self, prog, args):
        parser = argparse.ArgumentParser(prog, description=self.label)
        parser.add_argument(
            '-p', '--parent', type=IntValidator(1),
            help='Id of a parent group. Use `list_groups -i` to get list of groups with id.')
        parser.add_argument("name", metavar="NAME", type=str_not_empty, help="Group name")
        args = parser.parse_args(args)

        try:
            with self.db_session() as dbs:
                group = Group(parent_id=args.parent, name=args.name)
                dbs.add(group)
                dbs.commit()
                print("Added group '{}' with id {}.".format(args.name, group.id))
        except IntegrityError:
            print("Error: Parent group with id {} does not exist.".format(args.parent))
            return 2
