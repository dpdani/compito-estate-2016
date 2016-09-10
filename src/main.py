#!/usr/bin/python3
#
# Copyright (C) 2016  Daniele Parmeggiani
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""

See docs/compito_sistemi_4F.pdf for what this program does.

"""


import os
import sys
import csv
import console


CSV_HEADER = ['n', 'nome', 'MV', 'MAC', 'IP']


class Host(object):
    def __init__(self, n, name, vm, mac, ip):
        self.n = n
        self.name = name
        self.vm = vm
        self.mac = mac
        self.ip = ip

    def to_dhcp(self):
        """Prepares this host for dhcpd.conf file format serialization."""
        return """
    host {} {
        hardware ethernet {};
        fixed-address {};
    }""".format(self.name, self.mac, self.ip)

    def to_csv(self):
        """Prepares this host for csv serialization."""
        return [self.n, self.name, self.vm, self.mac, self.ip]

    def __repr__(self):
        return "<Host '{}'>".format(self.name)


class HostsHandler(object):
    def __init__(self):
        self.hosts = []

    def search(self, name=None, vm=None, mac=None, ip=None):
        found = []
        for host in self.hosts:
            if name is not None:
                if host.name == name or name == '*':
                    found.append(host)
            if vm is not None:
                if host.vm == vm or vm == '*':
                    found.append(host)
            if mac is not None:
                if host.mac == mac or mac == '*':
                    found.append(host)
            if ip is not None:
                if host.ip == ip or ip == '*':
                    found.append(host)
        return found


class MainConsole(console.Console):
    def __init__(self, hosts_handler):
        super().__init__(input_str='$ ', greeting="Type 'help' for a list of commands.", goodbye='', pass_console=True)
        self.hosts_handler = hosts_handler
        self.commands = [
            InsertCommand(),
            HelpCommand(),
        ]


class HelpCommand(console.Command):
    def __init__(self):
        usage = \
            """
Usage:      - help: Shows the main help page.
            - help [command]: Shows command-specific help.
"""
        console.Command.__init__(self, "help $", "You're in the shish of the world.", usage, "help", "Shows this page.")
        self.commands_shortnames = {}  # also contains the command instance for faster lookups
        self.commands_shorthelps = {}  # also contains the command name for faster lookups

    def run(self, args, usr, con=None):
        if not self.commands_shortnames:
            self.update_commands(con)
        if not args:
            coms_list = ""
            for com in self.commands_shortnames:
                coms_list += " - " + com + ": " + self.commands_shorthelps[com] + "\n"
            print("\nCommand Line Help.\n" + self.usage_str + """
Here's a quick list of commands:
{}
You can look at command-specific help by typing "help [command]". Have Fun!
""".format(coms_list))
        else:
            name = args[0]
            if name in self.commands_shortnames:
                print("Displaying help for the \"{}\" command.".format(name))
                print("{}: {}".format(name, self.commands_shorthelps[name]))
                print(self.commands_shortnames[name].usage_str)
                print(self.commands_shortnames[name].help_str)
            else:
                print("Cannot find command \"%s\"." % name)

    def update_commands(self, con):
        for com in con.commands:
            if com.short_name:
                # commands with no short name will not be recorded for help
                self.commands_shortnames.update({com.short_name: com})
                self.commands_shorthelps.update({com.short_name: com.short_help})


class InsertCommand(console.Command):
    def __init__(self):
        usage = """
Usage:      - insert: Insert a new host in the list."""
        super().__init__("insert", help_str="Insert a new host in the list.", usage_str=usage, short_name="insert",
                         short_help="Insert a new host in the list.")

    def run(self, args, usr, con=None):
        fields = {}
        print("Use Ctrl-C to cancel at any moment.")
        for field in CSV_HEADER:
            try:
                fields[field] = input("Please insert data for the '{}' field: ".format(field))
            except KeyboardInterrupt:
                print('\n')
                return
        con.hosts_handler.hosts.append(
            Host(n=fields['n'], name=fields['name'], vm=fields['MV'], mac=fields['MAC'], ip=fields['IP'])
        )
        print("New host correctly added.")


def main(args):
    first = True
    while True:
        try:
            csv_path = input("Please, insert{} csv file path: ".format('' if first else ' a valid'))
        except KeyboardInterrupt:
            return
        first = False
        if os.path.exists(csv_path):
            break
    hosts_handler = HostsHandler()
    with open(csv_path, 'r') as f:
        try:
            reader = csv.reader(f)
            for row in reader:
                if row == CSV_HEADER:
                    continue
                hosts_handler.hosts.append(
                    Host(n=row[0], name=row[1], vm=row[2], mac=row[3], ip=row[4])
                )
        except csv.Error:
            print("Error while parsing csv file. Quitting.")
            sys.exit(1)
    print("Read {} hosts.".format(len(hosts_handler.hosts)))
    con = MainConsole(hosts_handler)
    con.loop()



if __name__ == "__main__":
    main(sys.argv[1:])
    print("\nQuitting.")
