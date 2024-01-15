import re
import logging
from pprint import pprint

from maya_header_parser import parser_interface


class AsciiHeaderParser(parser_interface.ParserInterface):

    """
    Read/write header on ascii maya file

    Example:
        maya_file = BinaryHeaderParser('C:/filepath/filename.ma')

        maya_file.set_fileinfo("NewFileInfo", "Store string info")     # Set fileinfo
        print(maya_file.get_fileinfo("NewFileInfo"))                   # Get fileinfo
        print(maya_file.get_all_fileinfo())                            # Get a list of all fileinfo
        maya_file.remove_fileinfo("NewFileInfo", "Store string info")  # Remove fileinfo

        maya_file.set_plugin("fbxmaya", "required version")            # Set plugin requirements
        print(maya_file.get_plugin("fbxmaya"))                         # Get plugin
        print(maya_file.get_all_plugins())                             # Get a list of all plugins
        maya_file.remove_plugin("fbxmaya")                             # Remove plugin requirements

        maya_file.save()                                               # Save to current file
        maya_file.save_as('C:/filepath/newFilename.ma')                # Save to new file
    """

    COMMENT = "//"
    FILE = "file "
    REQUIRES = "requires "
    UNITS = "currentUnit "
    PLUG = "plugin"
    FINF = "fileInfo "
    UNKNOWN = "unknown"

    def __init__(self, filename, fileinfo_data=None, plugin_data=None):
        super().__init__(filename, fileinfo_data=fileinfo_data, plugin_data=plugin_data)

        self.log = logging.getLogger("maya_header_parser")

        self.filename = filename
        self._header_data = {self.COMMENT: [], self.FILE: [], self.REQUIRES: {}, self.PLUG: {}, self.UNITS: {}, self.FINF: {}, self.UNKNOWN:[]}
        self._header_size = 0

        self._unpack_header_data()

        if fileinfo_data is not None:
            self._header_data[self.FINF] = fileinfo_data

        if plugin_data is not None:
            self._header_data[self.PLUG] = plugin_data

    def _unpack_header_data(self):
        self._header_size = 0
        with open(self.filename, "r") as file_obj:
            while True:
                line_data = file_obj.readline()
                if line_data.startswith("createNode") or line_data.startswith("// End of"):
                    break

                self._header_size += 1

                line_data = line_data.strip()
                # Put all the comments in its own list
                if line_data.startswith(self.COMMENT):
                    self._header_data[self.COMMENT].append(line_data)

                elif line_data.startswith(self.FILE):
                    self._header_data[self.FILE].append(line_data)

                # Get all unit settings in a list ["-l centimeter", "-a degree", "-t ntsc"]
                # And the convert it to a dict to make it easier to search
                elif line_data.startswith(self.UNITS):
                    unit_list = re.findall("-[a-z]+ [a-z]+", line_data)
                    unit_dict = {}
                    for unit in unit_list:
                        split_unit = unit.split(" ")
                        unit_dict[split_unit[0]] = " ".join(split_unit[1:])
                    self._header_data[self.UNITS] = unit_dict

                # Get requirement (maya version/plugin)
                # We split them up (maya version/plugin) in the internal dict as it's easier to handle
                elif line_data.startswith(self.REQUIRES):
                    data_split = line_data[len(self.REQUIRES):-1].replace("\"", "").split(" ")
                    variable = data_split[0].strip("\"")
                    value = " ".join(data_split[1:]).strip("\"")
                    if variable == "maya":
                        self._header_data[self.REQUIRES][str(variable)] = value
                    else:
                        self._header_data[self.PLUG][str(variable)] = value

                elif line_data.startswith(self.FINF):
                    data_split = line_data[len(self.FINF):-1].split(" ")
                    variable = data_split[0].strip("\"")
                    value = " ".join(data_split[1:]).strip("\"")
                    self._header_data[self.FINF][str(variable)] = value

                else:
                    self._header_data[self.UNKNOWN].append(line_data)

    def _pack_header_data(self) -> list:
        header_list = []
        for header_type in self._header_data:
            if header_type == self.COMMENT:
                header_list += [f"{item}\n" for item in self._header_data[self.COMMENT]]

            if header_type == self.FILE:
                header_list += [f"{item}\n" for item in self._header_data[self.FILE]]

            elif header_type == self.UNITS:
                header_list.append(self.UNITS + " ".join([f"{key} {value}" for key, value in self._header_data[self.UNITS].items()]) + ";\n")

            elif header_type == self.REQUIRES:
                header_list += [f"{self.REQUIRES}{key} \"{value}\";\n" for key, value in self._header_data[self.REQUIRES].items()]

            elif header_type == self.PLUG:
                header_list += [f"{self.REQUIRES}\"{key}\" \"{value}\";\n" for key, value in self._header_data[self.PLUG].items()]

            elif header_type == self.FINF:
                header_list += [f"{self.FINF}\"{key}\" \"{value}\";\n" for key, value in self._header_data[self.FINF].items()]

            elif header_type == self.UNKNOWN:
                header_list += [f"{item}\n" for item in self._header_data[self.UNKNOWN]]

        return header_list

    def get_maya_version(self) -> int:
        for key in self._header_data[self.REQUIRES]:
            if key == "maya":
                return int(self._header_data[self.REQUIRES][key])

    def set_maya_version(self, version: int):
        for key in self._header_data[self.REQUIRES]:
            if key == "maya":
                self._header_data[self.REQUIRES][key] = str(version)
                break

    def save_as(self, filename):

        orig_file_data = []
        with open(self.filename, "r") as file_obj:
            orig_file_data = file_obj.readlines()

        header_end = 0
        for line in orig_file_data:
            if line.startswith("createNode"):
                break
            header_end += 1

        no_header_file_data = orig_file_data[header_end:]
        new_header_file_data = self._pack_header_data()
        new_file_data = new_header_file_data + no_header_file_data

        with open(filename, "w", encoding="utf-8") as file_obj:
            file_obj.writelines(new_file_data)

    def get_fileinfo(self, name) -> str:
        value = self._header_data[self.FINF].get(name)
        # Remove extra escape characters so we return same data that was sent in
        value = value.replace("\\\"", "\"")
        return value

    def set_fileinfo(self, name: str, value: str):
        # Add extra escape character (/) around " to make sure we
        # still can read current scene even if fileInfo contains "
        value = value.replace("\"", "\\\"")
        self._header_data[self.FINF][name] = value

if __name__ == "__main__":

    pass

    # Testing
    # maya_file = AsciiHeaderParser('C:/test/cube_new.ma')
    # maya_file.set_fileinfo("TestThis", "TestValue")
    # maya_file.remove_plugin("stereoCamera2")
    # print(maya_file.get_fileinfo("TestThis"))
    #
    # maya_file.save_as('C:/test/cube_new2.ma')


    # print("\n\n")
    # print("--------------------------------")
    # pprint(maya_file._serialize_header())
    # print("--------------------------------")
    #
    # maya_file.set_fileinfo("NewFileInfo", "Store string info")  # Set fileinfo
    # print(maya_file.get_fileinfo("NewFileInfo"))  # Get fileinfo
    # pprint(maya_file.get_all_fileinfo(), sort_dicts=False)  # Get a list of all fileinfo
    # pprint(maya_file.get_all_plugins(), sort_dicts=False)  # Get a list of all plugins
    # maya_file.remove_fileinfo("NewFileInfo", "Store string info")  # Remove fileinfo
    #
    # maya_file.set_plugin("fbxmaya", "required version")  # Set plugin requirements
    # print(maya_file.get_plugin("fbxmaya"))  # Get plugin
    # print(maya_file.get_all_plugins())  # Get a list of all plugins
    # maya_file.remove_plugin("fbxmaya")  # Remove plugin requirements
    #
    # maya_file.save()  # Save to current file
    # maya_file.save_as('C:/filepath/newFilename.mb')  # Save to new file