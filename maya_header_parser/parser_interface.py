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

    def get_fileinfo(self, name: str) -> str:
        return self._header_data[self.FINF].get(name)

    def set_fileinfo(self, name: str, value: str):
        self._header_data[self.FINF][name] = value

    def remove_fileinfo(self, name: str):
        if self._header_data[self.FINF].get(name):
            self._header_data[self.FINF].pop(name)

    def get_all_fileinfo(self) -> dict:
        return self._header_data[self.FINF]

    def get_plugin(self, name) -> str:
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
