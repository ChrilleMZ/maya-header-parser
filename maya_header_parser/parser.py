from pprint import pprint

from maya_header_parser import parser_interface


def maya_header_parser(filename, fileinfo_data=None, plugin_data=None) -> parser_interface.ParserInterface:
    if filename.endswith(".mb"):
        from maya_header_parser import parser_binary
        return parser_binary.BinaryHeaderParser(filename, fileinfo_data=fileinfo_data, plugin_data=plugin_data)
    elif filename.endswith(".ma"):
        from maya_header_parser import parser_ascii
        return parser_ascii.AsciiHeaderParser(filename, fileinfo_data=fileinfo_data, plugin_data=plugin_data)


if __name__ == "__main__":
    pass

    # maya_file = maya_header_parser('C:/test/cube_other.ma')
    # maya_file.set_maya_version(2022)

    # maya_file.save_as('C:/test/cube_other_2.ma')
    # print(maya_file.get_maya_version())
    # pprint(maya_file.get_all_fileinfo(), sort_dicts=False)
    # print(maya_file.get_fileinfo("Embark_info"))
    # maya_file.set_fileinfo("NewValue", "this new value")


    # maya_file = maya_header_parser('C:/test/cube.mb')
    # pprint(maya_file.get_all_fileinfo(), sort_dicts=False)
    # print(maya_file.get_maya_version())
    # maya_file.set_maya_version(2022)

    # print(maya_file.get_fileinfo("Embark_info"))
    # maya_file.set_fileinfo("NewValue", "this new value")
    # maya_file.save_as('C:/test/cube_2.mb')

