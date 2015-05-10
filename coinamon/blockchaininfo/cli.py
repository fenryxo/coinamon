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
from datetime import datetime
import sys

from coinamon.blockchaininfo.importer import BlockchaininfoImporter  # noqa
from coinamon.core.cli import Command  # noqa
from coinamon.core.cli import IntValidator  # noqa
from coinamon.core.importer import BadDataError  # noqa
from coinamon.core.models import Group  # noqa


class ImportBlockchainWalletCommand(Command):
    name = "import_blockchain_wallet"
    label = "Import your contacts from Blockchain.info Wallet. Reads data from standard input."

    def run(self, prog, args):
        parser = argparse.ArgumentParser(prog, description=self.label)
        parser.add_argument(
            '-g ', '--group', type=IntValidator(1),
            help='Id of a group to add new contacts to. If omitted, a new group will be created.')
        args = parser.parse_args(args)

        importer = BlockchaininfoImporter(self.db_session)

        if args.group:
            with self.db_session() as dbs:
                group = dbs.query(Group).filter_by(id=args.group).first()
                if not group:
                    print("Error: Group with id {} does not exist.".format(args.group))
                    return 2
        else:
            group = "Blockchain.info Wallet Import ({0:%c})".format(datetime.today())

        print("Paste data and hit Ctrl-D\n")
        data = sys.stdin.read()
        print("")

        errors = []

        try:
            unique, duplicate = importer.analyse_contacts(importer.import_contacts(data, errors))
        except BadDataError as e:
            print("Error: Data processing failed. {}".format(e))
            return 2

        code = 0
        if unique:
            importer.save_contacts(group, unique)

            print("Imported addresses:\n")
            for label, address in unique:
                print("{}    {}".format(address, label or ""))

        if duplicate:
            code = 3
            print("\nDuplicate addresses (not imported):\n")
            for label, address in duplicate:
                print("{}    {}".format(address, label or ""))

        if errors:
            code = 4
            print("\nThere were errors:\n")
            for error in errors:
                print(error)

        return code
