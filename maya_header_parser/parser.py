from pprint import pprint
import logging
import pathlib

from maya_header_parser import ascii_parser
from maya_header_parser import binary_parser


class MayaHeaderParser:

    def __init__(self, filename, header_data=None, plugin_data=None):

        self.log = logging.getLogger("maya_header_parser")

        self.filename = filename
        self.header_parser = None

        if filename.endswith(".mb"):
            self.header_parser = binary_parser.BinaryHeaderParser(filename, fileinfo_data=header_data, plugin_data=plugin_data)
        elif filename.endswith(".ma"):
            self.header_parser = ascii_parser.AsciiHeaderParser(filename, fileinfo_data=header_data, plugin_data=plugin_data)

    def get_fileinfo(self, name) -> str:
        return self.header_parser.get_fileinfo(name)

    def set_fileinfo(self, name: str, value: str):
        self.header_parser.set_fileinfo(name, value)

    def remove_fileinfo(self, name: str):
        self.header_parser.remove_fileinfo(name)

    def get_all_fileinfo(self) -> dict:
        return self.header_parser.get_all_fileinfo()

    def get_plugin(self, name) -> str:
        return self.header_parser.get_plugin(name)

    def set_plugin(self, name: str, value: str):
        self.header_parser.set_plugin(name, value)

    def remove_plugin(self, name: str):
        self.header_parser.remove_plugin(name)

    def get_all_plugins(self) -> dict:
        return self.header_parser.get_all_plugins()

    def save(self):
        self.header_parser.save()

    def save_as(self, filename):
        if not filename.endswith(".ma") or not filename.endswith(".mb"):
            self.log.warning("MayaHeaderParser only supports files which ends with .ma or .mb")
            return

        current_extension = pathlib.Path(self.filename).suffix
        new_extension = pathlib.Path(filename).suffix

        if new_extension != current_extension:
            self.log.warning("MayaHeaderParser only support exporting to the same file type (mb -> mb or ma -> ma")

        self.header_parser.save_as(filename)


if __name__ == "__main__":

    maya_file = MayaHeaderParser('C:/test/cube_other.ma')
    pprint(maya_file.get_all_fileinfo(), sort_dicts=False)

    maya_file = MayaHeaderParser('C:/test/cube.mb')
    pprint(maya_file.get_all_fileinfo(), sort_dicts=False)
