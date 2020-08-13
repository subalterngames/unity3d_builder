# Unity3D Builder

Create Unity3D standalone builds of a project for Windows, OS X, and Linux. Then, create zip files for each platform.

## Requirements

- Python3
- Unity3D Editor
- Windows
- 7zip
- (Optional) WSL 2 (this will let Windows grant executable permissions to the OS X and Linux builds)

## Installation

1. Clone this repo.
2. `cd path/to/unity3d_builder` (Replace `path/to` with the actual path to the cloned repo.)
3. Install the pip module: `pip3 install -e .` (don't forget the `.`)

## Usage

```python
from unity3d_builder import Unity3DBuilder

ub = Unity3DBuilder(project_path="path/to/MyProject",
                    dest_dir="path/to/MyProject/bin")
ub.create()
```

| Parameter      | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `project_path` | The path to your Unity3D project. Can be relative. Use `~` for home directory. |
| `dest_dir`     | The path to where the standalone builds will be created. Can be relative. Use `~` for home directory. |

#### Result:

(Assuming a Unity3D project named "MyProject" and a destination directory "MyProject/bin"):

```
MyProject/
....bin/
........MyProject_Windows.zip
........MyProject_OSX.zip
........MyProject_Linux.zip
```