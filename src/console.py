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

This module contains the base abstract classes for the command line interface.
This module comes from https://github.com/dpdani/csu/blob/master/src/core/console.py.
Has been slightly modified.

"""


class Console:
    """
    This is the base abstract class for command line
    interface in CSU.
    Call Console.loop() to start console.
    This class is intended to be highly customizable.
    """

    exit_strings = ["exit", "quit", "q"]  # input strings that can quit the console

    def __init__(self, input_str, greeting, goodbye, pass_console=False):
        """
        :type input_str: str
        :type greeting: str
        :type goodbye: str
        Argument input_str lets you choose which string will be
        shown for command input. Defaults to "$".
        Note: additional space not required.
        Argument greeting will be shown at console launch time.
        Argument goodbye will be shown at console close time.
        """
        self.usr = None  # the user must be implemented by a non-abstract console
        self.input_str = input_str
        self.greeting = greeting
        self.goodbye = goodbye
        self.commands = []
        self._closing = False
        self.pass_console = pass_console
        self.prepare()
        self.look_for_commands()

    def prepare(self):
        """
        This function will be called right after the __init__
        function and right before look_for_commands and is intended
        to prepare the Console before loop starts.
        By default this function does nothing.
        E.G.: setting up user, etc...
        """
        pass

    def loop(self):
        print(self.greeting)
        while True:
            if self._closing:
                break
            try:
                inp = input(self.input_str)
            except (KeyboardInterrupt, EOFError):
                break
            if inp == "":
                continue
            if inp in self.exit_strings:
                break
            self.call_command(inp)
        self.closing()
        print(self.goodbye)

    def close(self):
        """
        Prevents the console to make another iteration.
        Doesn't stop the current one.
        """
        self._closing = True

    def call_command(self, input):
        """
        This function uses the dafault command recognition
        mechanism as described in the Command class.
        :type input: str
        """
        input = input.lower().strip()
        input = input.split(" ")
        for com in self.commands:
            if com.recognition[0] == input[0]:
                if len(input) > len(com.recognition):
                    print(com.usage_str)
                    return
                n = 0
                for arg in com.recognition:
                    if arg == '%':
                        try:
                            input[n]
                        except IndexError:
                            if com.usage_str:
                                print(com.usage_str)
                            else:
                                print("Invalid usage of command.")
                            return
                    n += 1
                console = None
                if self.pass_console:
                    console = self
                return com.run(input[1:], self.usr, console)
        print("Unknown command.")

    def look_for_commands(self):
        """
        Looks for available commands and puts
        them in the self.commands list.
        The look mechanism must be implemented by
        a non abstract Console.
        """
        pass

    def closing(self):
        """
        This function will be called when the Console
        receives the closing command and is intended to
        prepare the Console to be closed.
        By default this function does nothing.
        """
        pass


class Command:
    def __init__(self, recognition, help_str="", usage_str="", short_name="", short_help=""):
        """
        :type recognition: str
        :type help_str: str
        :type usage_str: str
        :type short_name: str
        :type short_help: str
        Abstract base class for all commands.
        The recognition argument will be used by Console
        to understand which command has been prompted by
        the user and must follow this pattern:
            "command % $"
            % represents argument given to the command and might
              or might not be requested by a Command. If the
              command name is right, but the pattern hasn't
              been respected by the user, usage_str will be
              displayed if given.
            $ as above this character indicates an argument,
              but this is intended to be optional.
        The second argument, help_str, is the help string
        shown to the user when requested by the 'help'
        command.
        The third argument, usage_str, gets displayed
        when the user hasn't respected the pattern
        indicated in the 'recognition' argument. This
        string can be found in self.usage_str for
        avoiding redundancy within help strings.
        Arguments short_name and short_help will be
        used by the help command when listing commands.
        'short_name' should be the same name provided in
        the recognition argument and 'short_help' should
        be a one-line help explaining what the command
        basically does.
        """
        self.recognition = recognition.split(' ')
        self.help_str = help_str
        self.usage_str = usage_str
        self.short_name = short_name
        self.short_help = short_help

    def run(self, args, usr, console=None):
        """
        :type args: list
        This function is called when the Command has
        been recognized by the Console user prompt.
        The args argument is the list of arguments
        given to the Command according to the pattern
        defined in the initialization.
        If the console allows it, the console object itself
        may be passed through the argument 'console'.
        By default this method raises an exception.
        """
        raise NotImplementedError("run method not implemented by command.")
