# Maya Head Parser
Parses maya (binary/ascii) info/head, so you read and write extra information to the maya files header data.

Binary reader inspired by https://github.com/mottosso/maya-scenefile-parser

# Install
Using pip
```commandline
python -m pip install git+https://github.com/ChrilleMZ/maya-header-parser.git
```

# Usage

Run this in a python script

```python
from maya_header_parser import parser as mh_parser

maya_file = mh_parser.maya_header_parser("c:/filpath/filename.mb")
maya_file.set_fileinfo("NewFileInfo", "Store string info")          # Set fileinfo
print(maya_file.get_fileinfo("NewFileInfo"))                        # Get fileinfo
print(maya_file.get_all_fileinfo())                                 # Get a list of all fileinfos
maya_file.remove_fileinfo("NewFileInfo")                            # Remove fileinfo

maya_file.set_plugin("fbxmaya", "required version")                 # Set plugin requirements
print(maya_file.get_plugin("fbxmaya"))                              # Get plugin
print(maya_file.get_all_plugins())                                  # Get a list of all plugins
maya_file.remove_plugin("fbxmaya")                                  # Remove plugin requirements

maya_file.save()                                                    # Save to current file
maya_file.save_as('C:/test/testfile2.mb')                           # Save to new file
```






