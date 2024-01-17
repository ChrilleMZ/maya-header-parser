import logging
from abc import ABC, abstractmethod


class ParserInterface(ABC):

    FINF = "FINF"
    PLUG = "PLUG"

    def __init__(self, filename, fileinfo_data=None, plugin_data=None):

        self.log = logging.getLogger("maya_header_parser")

        self.filename = filename
        self._header_data = {}
        self.header_parser = None

    def get_fileinfo(self, name: str, string_safe=True) -> str:
        """
        Get file info from given file
        :param name: Name of file info
        :param string_safe: Whether to replace "/\ with \"/\\ in the value to make it string safe
            (the string will always be encapsulated in " in ascii files)
        :return: File info value
        """
        value = self._header_data[self.FINF].get(name)
        # Remove extra escape characters so we return same data that was sent in
        if value and string_safe:
            value = value.replace("\\\\", "\\")
            value = value.replace("\\\"", "\"")

        return value

    def set_fileinfo(self, name: str, value: str, string_safe=True):
        """
        Add/update a file info, make sure to run the save function to store it
        :param name: Name of file info
        :param value: Value of the file info
        :param string_safe: Whether to replace " with \" in the value to make it string safe
            (the string will always be encapsulated in " in ascii files)
        :return:
        """
        # Add extra escape character (\) around " and \ to make sure we
        # still can read current scene even if fileInfo contains "
        # This is also to mimic mayas own fileInfo function that adds extra \ on write
        if not isinstance(value, str):
            raise TypeError(f"Type {type(value)} is not supported as value, please use a string (str) instead")

        if string_safe:
            value = value.replace("\\", "\\\\")
            value = value.replace("\"", "\\\"")

        self._header_data[self.FINF][name] = value

    def remove_fileinfo(self, name: str):
        if self._header_data[self.FINF].get(name):
            self._header_data[self.FINF].pop(name)

    def get_all_fileinfo(self) -> dict:
        return self._header_data[self.FINF]

    def get_plugin(self, name: str) -> str:
        return self._header_data[self.PLUG].get(name)

    def set_plugin(self, name: str, value: str):
        self._header_data[self.PLUG][name] = value

    def remove_plugin(self, name: str):
        if self._header_data[self.PLUG].get(name):
            self._header_data[self.PLUG].pop(name)

    def get_all_plugins(self) -> dict:
        return self._header_data[self.PLUG]

    @abstractmethod
    def get_maya_version(self) -> int:
        return 0

    @abstractmethod
    def set_maya_version(self, version: int):
        pass

    def save(self):
        self.save_as(self.filename)

    @abstractmethod
    def save_as(self, filename):
        pass
