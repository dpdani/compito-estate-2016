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


class Host(object):
    def __init__(self, name, vm, mac, ip):
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
        }
        """.format(self.name, self.mac, self.ip).strip()

    def to_csv(self):
        """Prepares this host for csv serialization."""
        return [self.name, self.vm, self.mac, self.ip]


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


def main(args):
    pass




if __name__ == "__main__":
    main(sys.argv)
