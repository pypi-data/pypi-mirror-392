#!/usr/bin/env python3
"""GUI to upload tests."""
import argparse
import json
import sys
from pathlib import Path

try:
    import itkdb_gtk

except ImportError:
    cwd = Path(__file__).parent.parent
    sys.path.append(cwd.as_posix())

from itkdb_gtk import dbGtkUtils, ITkDBlogin, ITkDButils, QRScanner, findVTRx

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

class FindComponent(dbGtkUtils.ITkDBWindow):
    """Read QR of bar code and retrieve information about component."""

    def __init__(self, session, help_link=None):
        """Initialization.

        Args:
            session: ITkDB session
            help_link: link to help page.

        """
        super().__init__(session=session, title="Find Component", help_link=help_link)
        self.scanner = QRScanner.QRScanner(self.get_qrcode)
        self.ofd = None  # Output file descriptor
        self.init_window()

    def __del__(self):
        """Destructor."""
        if self.ofd is not None:
            self.ofd.close()

    def init_window(self):
        """Create the Gtk window."""
        # Initial tweaks
        self.set_border_width(10)

        # Prepare HeaderBar
        self.hb.props.title = "Find Component"


        # File name
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.mainBox.pack_start(box, False, False, 0)
        self.open_btn = Gtk.Button(label="Output File")
        self.open_btn.set_tooltip_text("Select output file to save scanned component information in CSV format.")
        self.open_btn.connect("clicked", self.on_file_set)
        box.pack_start(self.open_btn, False, False, 0)

        self.close_btn = Gtk.Button(label="Close File")
        self.close_btn.set_sensitive(False)
        self.close_btn.set_tooltip_text("Close the output file.")
        self.close_btn.connect("clicked", self.on_file_close)
        box.pack_start(self.close_btn, False, False, 0)


        self.file_name = Gtk.Label(label="No output file selected")
        self.mainBox.pack_start(self.file_name, False, False, 5)

        self.scanner_dev = Gtk.Label(label="No scanner found")
        self.mainBox.pack_start(self.scanner_dev, False, False, 5)

        # Object Data
        lbl = Gtk.Label(label="Scan your QR or bar code. Information will appear below.")
        self.mainBox.pack_start(lbl, False, False, 10)

        
        #btn = Gtk.Button(label="Test Button")
        #btn.connect("clicked", self.test_qrcode)
        #self.mainBox.pack_start(btn, True, True, 0)

        # The text view
        self.mainBox.pack_start(self.message_panel.frame, True, True, 0)

        self.timer_id = GLib.timeout_add(500, self.find_scanner)

        self.show_all()

    def find_scanner(self, *args):
        """Figure out if there is a scanner connected."""
        if self.scanner.reader is None:
            self.scanner_dev.set_text("No scanner found")
        else:
            self.scanner_dev.set_text("Found scanner in {}".format(self.scanner.reader.name))

        return True
    
    def on_file_set(self, *args):
        """File selected.

            Opens the file for writing the information aobut the components
            scanned.
        """
        fc = Gtk.FileChooserDialog(title="Save data file", action=Gtk.FileChooserAction.SAVE)
        fc.set_current_name("scanned_components.csv")
        fc.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )
        response = fc.run()
        if response != Gtk.ResponseType.OK:
            fc.destroy()
            return

        filename = fc.get_filename()

        if Path(filename).exists():
            overwrite = dbGtkUtils.ask_for_confirmation("File already exists. Overwrite?", "{}".format(filename))
            if not overwrite:
                fc.destroy()
                return

        fc.destroy()
        self.close_btn.set_sensitive(True)
        self.open_btn.set_sensitive(False)
        self.file_name.set_text("Output File: {}".format(filename))
        self.ofd = open(filename, "w", encoding="utf-8")
        self.ofd.write("SN,AltID,Type,Location,StageCode\n")
        self.ofd.flush()

    def on_file_close(self, *args):
        """File closed."""
        if self.ofd is not None:
            self.ofd.close()
            self.ofd = None
            self.close_btn.set_sensitive(False)
            self.open_btn.set_sensitive(True)
            self.file_name.set_text("No output file selected")

    def get_qrcode(self, txt):
        """Gets data from QR scanner."""
        is_vtrx = False
        if findVTRx.is_vtrx(txt):
            try:
                SN = findVTRx.find_vtrx(self.session, txt)
                is_vtrx = True
            except ValueError as e:
                self.write_message("Error: {}\n".format(e))
                return
        else:
            SN = txt

        obj = ITkDButils.get_DB_component(self.session, SN)
        if obj is None:
            self.write_message("Object {} not found in DB\n\n".format(SN))
            return

        if is_vtrx and obj["alternativeIdentifier"] is None:
            obj["alternativeIdentifier"] = txt

        msg = "\n{}\nObject SN: {}\nObject Alt. ID: {}\nObject Type: {}\nObject Loc. {}\nObject stage: {} - {}\n\n".format(
            txt,
            obj["serialNumber"],
            obj["alternativeIdentifier"],
            obj["componentType"]["name"],
            obj["currentLocation"]["name"],
            obj["currentStage"]["code"],
            obj["currentStage"]["name"])
        self.write_message(msg)

        msg = "{}, {}, {}, {}, {}\n".format(
            obj["serialNumber"],
            obj["alternativeIdentifier"],
            obj["componentType"]["name"],
            obj["currentLocation"]["code"],
            obj["currentStage"]["code"])

        if self.ofd is not None:
            self.ofd.write(msg)
            self.ofd.flush()

    def test_qrcode(self, *args):
        """Gets data from QR scanner."""
        txt = "a3c671bf38d3957dc053c6e5471aa27e"
        self.write_message("{}\n".format(txt))

        if findVTRx.is_vtrx(txt):
            try:
                SN = findVTRx.find_vtrx(self.session, txt)
            except ValueError as e:
                self.write_message("Error: {}\n".format(e))
                return
        else:
            SN = txt

        obj = ITkDButils.get_DB_component(self.session, SN)
        if obj is None:
            self.write_message("Object {} not found in DB\n\n".format(SN))
            return


        msg = "\n\nObject SN: {}\nObject Alt. ID: {}\nObject Type: {}\nObject Loc.: {}\nObject stage: {} - {}\n".format(
            obj["serialNumber"],
            obj["alternativeIdentifier"],
            obj["componentType"]["name"],
            obj["currentLocation"]["name"],
            obj["currentStage"]["code"],
            obj["currentStage"]["name"])

        self.write_message(msg)
        self.write_message("")

def main():
    """Main entry."""
    HELP_LINK="https://itkdb-gtk.docs.cern.ch/uploadSingleTest.html"

    # DB login
    dlg = ITkDBlogin.ITkDBlogin()
    client = dlg.get_client()
    if client is None:
        print("Could not connect to DB with provided credentials.")
        dlg.die()
        sys.exit()

    client.user_gui = dlg

    window = FindComponent(client, help_link=HELP_LINK)
    window.set_accept_focus(True)
    window.present()
    window.connect("destroy", Gtk.main_quit)

    try:
        Gtk.main()

    except KeyboardInterrupt:
        print("Arrrgggg!!!")

    dlg.die()

if __name__ == "__main__":
    main()
