# Maya Head Parser
Parses maya (binary/ascii) info/head, so you read and write extra information to the maya files header data.


# Install
Using pip
```commandline
python -m pip install git+https://github.com/rBrenick/script-panel.git
```

# Usage (WIP)

1. Run this script in a python tab in maya

```python
from maya_head_parser import binary_head_parser
maya_file = binary_head_parser.BinaryHeadPaser("c:/filpath/filename.mb")
maya_file.set_fileinfo("NewFileInfo", "Store string info")     # Set fileinfo
print(maya_file.get_fileinfo("NewFileInfo"))                   # Get fileinfo
print(maya_file.get_all_fileinfos())                           # Get a list of all fileinfos
maya_file.remove_fileinfo("Embark_info", "Store string info")  # Remove fileinfo

maya_file.set_plugin("fbxmaya", "required version")            # Set plugin requirements
print(maya_file.get_plugin("fbxmaya"))                         # Get plugin
print(maya_file.get_all_plugins())                             # Get a list of all plugins
maya_file.remove_plugin("Embark_info", "Store string info")    # Remove plugin requirements

maya_file.save()                                               # Save to current file
maya_file.save_as('C:/test/testfile2.mb')                      # Save to new file
```




