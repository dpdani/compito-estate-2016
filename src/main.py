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
import re
import csv
import console
from collections import defaultdict


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
    host {} [
        hardware ethernet {};
        fixed-address {};
    ]""".format(self.name, self.mac, self.ip).replace('[', '{').replace(']', '}')

    def to_csv(self):
        """Prepares this host for csv serialization."""
        return {
            'n':self.n,
            'nome': self.name,
            'MV': self.vm,
            'MAC': self.mac,
            'IP': self.ip
        }

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.n == other.n and \
               self.name == other.name and \
               self.vm == other.vm and \
               self.mac == other.mac and \
               self.ip == other.ip:
                return True
        return False

    def __repr__(self):
        return "<Host n='{}' name='{}' vm='{}' mac='{}' ip='{}'>".format(self.n, self.name, self.vm, self.mac, self.ip)


class HostsHandler(object):
    def __init__(self):
        self.hosts = []

    def search(self, n='', name='', vm='', mac='', ip=''):
        re_n = re.compile(n, flags=re.IGNORECASE)
        re_name = re.compile(name, flags=re.IGNORECASE)
        re_vm = re.compile(vm, flags=re.IGNORECASE)
        re_mac = re.compile(mac, flags=re.IGNORECASE)
        re_ip = re.compile(ip, flags=re.IGNORECASE)
        found = []
        for host in self.hosts:
            if n != '':
                if re_n.search(host.n) is not None:
                    if host not in found:
                        found.append(host)
            if name != '':
                if re_name.search(host.name) is not None:
                    if host not in found:
                        found.append(host)
            if vm != '':
                if re_vm.search(host.vm) is not None:
                    if host not in found:
                        found.append(host)
            if mac != '':
                if re_mac.search(host.mac) is not None:
                    if host not in found:
                        found.append(host)
            if ip != '':
                if re_ip.search(host.ip) is not None:
                    if host not in found:
                        found.append(host)
        return found

    def remove(self, n='', name='', vm='', mac='', ip=''):
        hosts = []
        to_remove = self.search(n, name, vm, mac, ip)
        for host in self.hosts:
            if host not in to_remove:
                hosts.append(host)
        self.hosts = hosts


class MainConsole(console.Console):
    def __init__(self, hosts_handler, csv_path):
        super().__init__(input_str='$ ', greeting="Type 'help' for a list of commands.", goodbye='', pass_console=True)
        self.hosts_handler = hosts_handler
        self.csv_path = csv_path
        self.commands = [
            InsertCommand(),
            HelpCommand(),
            SearchCommand(),
            ListCommand(),
            SaveCommand(),
            ExportCommand(),
            RemoveCommand(),
            EditCommand(),
        ]

    def closing(self):
        print('\n\n\nDo you wish to save before closing?\n')
        SaveCommand().run(['closing'], None, self)


class HelpCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition="help $",
            help_str="You're in the shish of the world.",
            usage_str="Usage:      - help: Shows the main help page.\n"
                      "            - help [command]: Shows command-specific help.",
            short_name="help",
            short_help="Shows this page."
        )
        self.commands_shortnames = {}  # also contains the command instance for faster lookups
        self.commands_shorthelps = {}  # also contains the command name for faster lookups

    def run(self, args, usr, con=None):
        if not self.commands_shortnames:
            self.update_commands(con)
        if not args:
            coms_list = ""
            for com in self.commands_shortnames:
                coms_list += " - " + com + ": " + self.commands_shorthelps[com] + "\n"
            print("\nCommand Line Help.\n\n" + self.usage_str + """

Here's a quick list of commands:
{}
You can look at command-specific help by typing "help [command]". Have Fun!
""".format(coms_list))
        else:
            name = args[0]
            if name in self.commands_shortnames:
                print("{}: {}".format(name, self.commands_shorthelps[name]))
                print('')
                print(self.commands_shortnames[name].usage_str)
                print('')
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
        super().__init__(
            recognition="insert",
            help_str="Insert a new host in the list.",
            usage_str="Usage:      - insert: Insert a new host in the list.",
            short_name="insert",
            short_help="Insert a new host in the list."
        )

    def run(self, args, usr, con=None):
        fields = {}
        print("Press Ctrl-C to cancel at any moment.")
        for field in CSV_HEADER[1:]:  # excludes field 'n' which can be automatically generated
            try:
                fields[field] = input("Please insert data for the '{}' field: ".format(field))
            except KeyboardInterrupt:
                print('')
                return
        con.hosts_handler.hosts.append(
            Host(n=len(con.hosts_handler.hosts)+1, name=fields['nome'], vm=fields['MV'], mac=fields['MAC'],
                 ip=fields['IP'])
        )
        print("New host correctly added.")


class SearchCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition="search % $ $ $ $",
            usage_str="Usage:      - search [field1[field2[...]]]: search for hosts in registry.",
            short_name="search",
            help_str="Search for hosts using given arguments: each argument represents a field."
                     "\nEach field must be one of 'n', 'nome', 'MV', 'MAC' or 'IP'.",
            short_help="Search for hosts in registry."
        )

    def run(self, args, usr, con=None):
        field_names = []
        for field in CSV_HEADER:
            field_names.append(field.lower())
        fields = defaultdict(str)
        print("Press Ctrl-C to cancel at any moment.")
        for arg in args:
            if arg not in field_names:
                print("Argument '{}' is not a valid field name.".format(arg))
                continue
            if arg not in fields:
                try:
                    inp = input("Search for field '{}': ".format(arg))
                except KeyboardInterrupt:
                    print("\n")
                    return
                fields[arg] = inp
        found = con.hosts_handler.search(
            n=fields['n'], name=fields['nome'], vm=fields['mv'], mac=fields['mac'], ip=fields['ip']
        )
        if len(found) == 0:
            print("No hosts found.")
        else:
            for host in found:
                print(" - {}".format(host))
            print("Found {} host{}.".format(len(found), '' if len(found) == 1 else 's'))


class EditCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition='edit % $ $ $ $',
            usage_str="Usage:      - edit [field1[field2[...]]]: edit hosts in registry.",
            short_name="edit",
            help_str="Edit hosts that already exist in registry using given arguments: each argument "
                     "represents a field (similarly to what the `search` command does).\nEach field "
                     "must be one of 'n', 'nome', 'MV', 'MAC' or 'IP'.",
            short_help="Edit hosts that already exist in registry."
        )

    def run(self, args, usr, con=None):
        field_names = []
        for field in CSV_HEADER:
            field_names.append(field.lower())
        fields = defaultdict(str)
        print("Press Ctrl-C to cancel at any moment.")
        for arg in args:
            if arg not in field_names:
                print("Argument '{}' is not a valid field name.".format(arg))
                continue
            if arg not in fields:
                try:
                    inp = input("Select for field '{}': ".format(arg))
                except KeyboardInterrupt:
                    print("\nNo hosts changed.")
                    return
                fields[arg] = inp
        found = con.hosts_handler.search(
            n=fields['n'], name=fields['nome'], vm=fields['mv'], mac=fields['mac'], ip=fields['ip']
        )
        if len(found) == 0:
            print("No hosts found to be edited.")
        else:
            print("Found the following hosts to be edited:")
            for host in found:
                print(" - {}".format(host))
            for host in found:
                print("Editing {}.".format(host))
                changed = False
                for field in CSV_HEADER:
                    print("Edit {} ".format(field), end='')
                    if field == 'nome':
                        field = 'name'
                    elif field == 'MV':
                        field = 'vm'
                    elif field == 'MAC':
                        field = 'mac'
                    elif field == 'IP':
                        field = 'ip'
                    try:
                        inp = input("[{}]: ".format(getattr(host, field)))
                    except KeyboardInterrupt:
                        print('')
                        changed = False
                        break
                    if inp in ['', getattr(host, field)]:
                        continue
                    else:
                        changed = True
                        setattr(host, field, inp)
                if changed:
                    con.hosts_handler.hosts[con.hosts_handler.hosts.index(host)] = host
                    print("Successfully edited host.")
                else:
                    print("Host unchanged.")



class RemoveCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition='remove % $ $ $ $ $',
            usage_str="Usage:      - remove [field1[field2[...]]]: remove hosts in registry.\n"
                      "            - remove [field1[field2[...]]] dontask: remove hosts in registry. "
                      "Don't ask for confirmation.",
            short_name="remove",
            help_str="Remove hosts in registry using given arguments: each argument represents a field ("
                     "similarly to what the `search` command does).\nEach field must be one of 'n', 'nome',"
                     "'MV', 'MAC' or 'IP'.",
            short_help="Remove host from registry."
        )

    def run(self, args, usr, con=None):
        field_names = []
        for field in CSV_HEADER:
            field_names.append(field.lower())
        fields = defaultdict(str)
        print("Press Ctrl-C to cancel at any moment.")
        for arg in args:
            if arg == 'dontask':
                continue
            if arg not in field_names:
                print("Argument '{}' is not a valid field name.".format(arg))
                continue
            if arg not in fields:
                try:
                    inp = input("Select for field '{}': ".format(arg))
                except KeyboardInterrupt:
                    print("\nNo hosts removed.")
                    return
                fields[arg] = inp
        length_before = len(con.hosts_handler.hosts)
        found = con.hosts_handler.search(
            n=fields['n'], name=fields['nome'], vm=fields['mv'], mac=fields['mac'], ip=fields['ip']
        )
        if len(found) == 0:
            print("No hosts found to be removed.")
        else:
            print("These hosts are about to be removed:")
            for host in found:
                print(" - {}".format(host))
            if 'dontask' not in args:
                while True:
                    try:
                        yn = input("Are you sure you want to proceed? [y/N]  ").lower()
                    except KeyboardInterrupt:
                        print("\nNo hosts removed.")
                        return
                    if yn == 'y':
                        break
                    elif yn in ['n', '']:
                        print("No hosts removed.")
                        return
                    else:
                        print("Unrecognizable input.")
            con.hosts_handler.remove(
                n=fields['n'], name=fields['nome'], vm=fields['mv'], mac=fields['mac'], ip=fields['ip']
            )
        delta_length = length_before - len(con.hosts_handler.hosts)
        if delta_length != 0:
            print("Removed {} host{}.".format(delta_length, '' if delta_length == 1 else 's'))


class ListCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition="list",
            help_str="Shows the entire list of hosts on record.",
            usage_str="Usage:      - list: Shows every host.",
            short_name="list",
            short_help="Show every host."
        )

    def run(self, args, usr, con=None):
        for host in con.hosts_handler.search(name=r'\.*'):
            print(host)


class SaveCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition='save',
            help_str="Saves current session to csv file.",
            usage_str="Usage:      - save: saves current session to csv.",
            short_name="save",
            short_help="Saves current session."
        )

    def run(self, args, usr, con=None):
        print("Press Ctrl-C to {}.".format('cancel' if len(args) == 0 else 'not save'))
        try:
            path = input("Saving path [{}]: ".format(con.csv_path))
        except KeyboardInterrupt:
            print('\nNothing saved.')
            return
        if path == '':
            path = con.csv_path
        else:
            con.csv_path = path
        with open(path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
            writer.writeheader()
            for host in con.hosts_handler.hosts:
                writer.writerow(host.to_csv())
        print("Successfully saved.")


class ExportCommand(console.Command):
    def __init__(self):
        super().__init__(
            recognition='export $',
            help_str="Exports current session in dhcpd.conf-compatible format to file.",
            usage_str="Usage:      - export: export to path.\n"
                      "            - export simple: export to path, do not include headers and footers.",
            short_name="export",
            short_help="Exports current session."
        )

    def run(self, args, usr, con=None):
        print("Press Ctrl-C to cancel.")
        try:
            path = input("Exporting path: ")
        except KeyboardInterrupt:
            print('\nNothing exported.')
            return
        with open(path, 'w') as f:
            if 'simple' not in args:
                try:
                    with open('dhcpdconf-header.txt', 'r') as headerfile:
                        f.write(headerfile.read())
                except: pass
            for host in con.hosts_handler.hosts:
                f.write(host.to_dhcp())
            if 'simple' not in args:
                try:
                    with open('dhcpdconf-footer.txt', 'r') as footerfile:
                        f.write(footerfile.read())
                except: pass
        print("Successfully exported.")




def main(args):
    csv_path = ''
    if len(args) > 0:
        csv_path = args[0]
        print("{} file '{}'.".format('Using' if os.path.exists(csv_path) else 'Cannot use', csv_path))
    if not os.path.exists(csv_path):
        first = True
        while True:
            try:
                csv_path = input("Please, insert{} csv file path [new]: ".format('' if first else ' a valid'))
            except KeyboardInterrupt:
                return
            first = False
            if csv_path in ['new', '']:
                try:
                    csv_path = input("Please, insert new csv file path: ")
                except KeyboardInterrupt:
                    return
                try:
                    with open(csv_path, 'w') as f:
                        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
                        writer.writeheader()
                    break
                except:
                    print("Could not create file.")
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
        except Exception:
            print("Error while parsing csv file. Quitting.")
            sys.exit(1)
    print("Read {} hosts.".format(len(hosts_handler.hosts)))
    con = MainConsole(hosts_handler, csv_path)
    con.loop()



if __name__ == "__main__":
    main(sys.argv[1:])
    print("\nBye bye!")
