# main.py
#
# Copyright 2025 James Jones
#
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import sys
import signal
import gi

# 1. Require versions FIRST
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

# 2. Import libraries SECOND
from gi.repository import Gtk, Gio, Adw
from window import FireFinanceWindow

class FireFinanceApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='me.velocitynet.FireFinance',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = FireFinanceWindow(application=self)
        win.present()

def main():
    # Handle Ctrl+C in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = FireFinanceApp()
    return app.run(sys.argv)
