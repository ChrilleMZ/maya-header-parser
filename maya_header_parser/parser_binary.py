import struct
import math
import logging
from collections import namedtuple
import pprint

from maya_header_parser import parser_interface

def be_word4(buf):
    return struct.unpack('>L', buf)[0]


IffChunk = namedtuple("IffChunk", ["typeid", "data_offset", "data_length"])


class BinaryHeaderParser(parser_interface.ParserInterface):
    """
    Read/write header on binary maya file
    Inspired by https://github.com/mottosso/maya-scenefile-parser

    Example:
        maya_file = BinaryHeaderParser('C:/filepath/filename.mb')

        maya_file.set_fileinfo("NewFileInfo", "Store string info")     # Set fileinfo
        print(maya_file.get_fileinfo("NewFileInfo"))                   # Get fileinfo
        print(maya_file.get_all_fileinfo())                            # Get a list of all fileinfo
        maya_file.remove_fileinfo("NewFileInfo", "Store string info")  # Remove fileinfo

        maya_file.set_plugin("fbxmaya", "required version")            # Set plugin requirements
        print(maya_file.get_plugin("fbxmaya"))                         # Get plugin
        print(maya_file.get_all_plugins())                             # Get a list of all plugins
        maya_file.remove_plugin("fbxmaya")                             # Remove plugin requirements

        maya_file.save()                                               # Save to current file
        maya_file.save_as('C:/filepath/newFilename.mb')                # Save to new file
    """

    UTF8 = "utf-8"

    # 64 bits
    FOR8 = be_word4(b"FOR8")

    # General
    MAYA = be_word4(b"Maya")

    # Header fields
    HEAD = be_word4(b"HEAD")
    VERS = be_word4(b"VERS")
    UVER = be_word4(b"UVER")
    MADE = be_word4(b"MADE")
    CHNG = be_word4(b"CHNG")
    ICON = be_word4(b"ICON")
    INFO = be_word4(b"INFO")
    OBJN = be_word4(b"OBJN")
    INCL = be_word4(b"INCL")
    LUNI = be_word4(b"LUNI")
    TUNI = be_word4(b"TUNI")
    AUNI = be_word4(b"AUNI")
    FINF = be_word4(b"FINF")
    PLUG = be_word4(b"PLUG")

    def __init__(self, filename, fileinfo_data:dict=None, plugin_data:dict=None):
        super().__init__(filename, fileinfo_data=fileinfo_data, plugin_data=plugin_data)

        self.log = logging.getLogger("maya_header_parser")

        self.filename = filename
        self._header_struct = struct.Struct(">LxxxxQ")
        self._main_chunk: IffChunk = None
        self._head_chunk: IffChunk = None
        self._content_block: IffChunk = None  # Rest of the file, we only care about the header part right now
        self._head_data_byte = b""
        self._head_data_raw = b""
        self._content_data_byte = b""
        self._header_data = {}

        self._get_all_chunks()

        if fileinfo_data is not None:
            self._header_data[self.FINF] = self._convert_str_dict_to_byte_dict(fileinfo_data)

        if plugin_data is not None:
            self._header_data[self.PLUG] = self._convert_str_dict_to_byte_dict(plugin_data)

    def _get_all_chunks(self):
        """ Fetch all chunks to make it easier to jump to specific data """
        with open(self.filename, "rb") as file_obj:
            self._get_main_chunk(file_obj)
            self._get_head_chunk(file_obj)
            self._get_content_block(file_obj)
            self._header_data = self._unpack_header_data(file_obj)

            # pprint.pprint(self._header_data)

    def _get_main_chunk(self, file_obj):
        """ Gets the length of the entire file and offset to the first chunk (Head)"""
        buf = file_obj.read(self._header_struct.size)
        typeid, data_length = self._header_struct.unpack(buf)
        buf = file_obj.read(4)
        chunk_type = struct.unpack(">L", buf)[0]
        if not chunk_type == self.MAYA:
            self.log.warning(f"This dose not look like a maya file {self.filename}")
            return []

        data_offset = file_obj.tell()
        self._main_chunk = IffChunk(typeid=typeid, data_offset=data_offset, data_length=data_length)

    def _get_head_chunk(self, file_obj):
        """ Get the offset and length of the header data """
        file_obj.seek(self._main_chunk.data_offset)

        buf = file_obj.read(self._header_struct.size)
        typeid, data_length = self._header_struct.unpack(buf)
        buf = file_obj.read(4)
        chunk_type = struct.unpack(">L", buf)[0]
        if not chunk_type == self.HEAD:
            self.log.warning("Could not find maya info/header")
            return []

        data_offset = file_obj.tell()
        self._head_chunk = IffChunk(typeid=typeid, data_offset=data_offset, data_length=data_length)

    def _get_content_block(self, file_obj):
        """ Not real chunk but the rest of the file after head"""
        data_offset = self._head_chunk.data_length + self._head_chunk.data_offset - 4
        data_length = self._main_chunk.data_length - data_offset + 20
        self._content_block = IffChunk(typeid=self.FOR8, data_offset=data_offset, data_length=data_length)

    def _get_content_data(self, file_obj):
        """ Retrieve data for content based on """
        file_obj.seek(self._content_block.data_offset)
        return file_obj.read(self._content_block.data_length)

    def _unpack_header_data(self, file_obj) -> dict:
        data_end = self._head_chunk.data_length + self._head_chunk.data_offset
        current_offset = self._head_chunk.data_offset
        info_data = {}
        while True:
            file_obj.seek(current_offset)
            buf = file_obj.read(self._header_struct.size)
            typeid, data_length = self._header_struct.unpack(buf)

            if current_offset >= data_end or typeid == self.FOR8:
                break

            data_offset = file_obj.tell()
            data = file_obj.read(data_length)
            self._head_data_raw += data

            # Reformatting data to a dict format, so it's easier to handle
            if not info_data.get(typeid):
                info_data[typeid] = {}

            data_split = data.split(b"\x00")
            name = data_split[0]
            value = b"\x00".join(data_split[1:-1])

            info_data[typeid][name.decode(self.UTF8)] = value.decode(self.UTF8)

            # Head info chunks always is a full 8 bytes
            current_offset = math.ceil((data_offset + data_length) / 8) * 8

        return info_data

    def _generate_main_chunk_bytes(self):
        """ Generate a new main chunk based on the size of the new head chunk"""
        return self._header_struct.pack(self.FOR8, self._main_chunk.data_length + 4) + b"Maya"

    def _generate_head_chunk_bytes(self):
        """ Generate a new head chunk based on the size of the header data"""
        return self._header_struct.pack(self.FOR8, self._head_chunk.data_length + 4) + b"HEAD"

    def _pack_header_data(self):
        head_bytes = b""
        for typeid, type_data in self._header_data.items():
            first = True
            for name, value in type_data.items():
                # Check if we have a header with only value or variable and value
                name = name.encode(self.UTF8)
                value = value.encode(self.UTF8)

                full_item = name
                if len(value):
                    full_item = name + b"\x00" + value + b"\x00"

                full_item_size = len(full_item)

                item_chunk = self._header_struct.pack(typeid, full_item_size)

                # This might not be needed as it all works, but I notice that the first header var always had an F
                if first:
                    item_chunk = item_chunk[:4] + b"F" + item_chunk[5:]

                buffer = b"\x00" * ((math.ceil((full_item_size/8))*8) - full_item_size)
                head_bytes += item_chunk + full_item + buffer

                first = False

        return head_bytes

    def _print_byte_data(self, data):
        """ Prints byte data in 16 byte chunks (Only for debugging purposes) """
        for index in range(math.ceil(len(data) / 16)):
            current_pos = index * 16
            self.log.debug(data[current_pos:current_pos+16])

    def _convert_str_dict_to_byte_dict(self, data) -> dict:
        byte_dict = {}
        for key, value in data.items():
            byte_dict[key.decode(self.UTF8)] = (value.decode(self.UTF8), len(value))
        return byte_dict

    def get_header_data(self, raw_data=False):
        if not raw_data:
            readable_head = {}
            for key in self._header_data.keys():
                readable_head[struct.pack(">L", key)] = self._header_data[key]
        else:
            readable_head = self._header_data

        return readable_head

    def get_raw_head_data(self):
        with open(self.filename, "rb") as file_obj:
            file_obj.seek(self._head_chunk.data_offset)
            data = file_obj.read(self._head_chunk.data_length)
            self._print_byte_data(data)

    def get_maya_version(self) -> int:
        return int(next(iter(self._header_data[self.VERS])))

    def set_maya_version(self, version: int):
        self._header_data[self.VERS] = {str(version): ""}

    def save_as(self, filename):
        """ Save to new file """

        filename = filename or self.filename

        # self._update_head_data()

        # Only read in the full content if we need, most of the time we would only read the header data
        if not self._content_data_byte:
            with open(self.filename, "rb") as file_obj:
                self._content_data_byte = self._get_content_data(file_obj)

        head_data_bytes = self._pack_header_data()
        new_head_data_diff = len(head_data_bytes) - self._head_chunk.data_length
        self._head_chunk = IffChunk(typeid=self.FOR8, data_offset=self._head_chunk.data_offset, data_length=len(head_data_bytes))
        self._main_chunk = IffChunk(typeid=self.FOR8, data_offset=self._main_chunk.data_offset, data_length=(self._main_chunk.data_length + new_head_data_diff))

        file_data = (
                self._generate_main_chunk_bytes() +
                self._generate_head_chunk_bytes() +
                head_data_bytes +
                self._content_data_byte
        )

        with open(filename, "wb") as file_obj:
            file_obj.write(file_data)


if __name__ == "__main__":

    pass

    # Testing
    # maya_file = BinaryHeaderParser('C:/test/cube.mb')

    # maya_file.save_as('C:/test/cube_test2.mb')
    #
    # maya_file.set_fileinfo("NewFileInfo", "Store string info")  # Set fileinfo
    # print(maya_file.get_fileinfo("NewFileInfo"))  # Get fileinfo
    # pprint.pprint(maya_file.get_all_fileinfo(), sort_dicts=False)  # Get a list of all fileinfo
    # pprint.pprint(maya_file.get_all_plugins(), sort_dicts=False)  # Get a list of all plugins
    # maya_file.remove_fileinfo("NewFileInfo", "Store string info")  # Remove fileinfo
    #
    # maya_file.set_plugin("fbxmaya", "required version")  # Set plugin requirements
    # print(maya_file.get_plugin("fbxmaya"))  # Get plugin
    # print(maya_file.get_all_plugins())  # Get a list of all plugins
    # maya_file.remove_plugin("fbxmaya")  # Remove plugin requirements
    #
    # maya_file.save()  # Save to current file
    # maya_file.save_as('C:/filepath/newFilename.mb')  # Save to new file


