from subprocess import call
from pathlib import Path
from typing import List, Dict


class Unity3DBuilder:
    """
    Create Unity3D standalone applications of a project for Windows, OS X, and Linux.

    See README for documentation.
    """

    # Each platform, its extension, and the command line argument.
    PLATFORMS = {"Windows": {"extension": ".exe", "call": "-buildWindows64Player"},
                 "OSX": {"extension": ".app", "call": "-buildOSXUniversalPlayer"},
                 "Linux": {"extension": ".x86_64", "call": "-buildLinux64Player"}}
    # Use this argument when calling Unity.
    PROJECT_PATH_ARG = "-projectPath"
    # 7z base call.
    ZIP_CALL = ["C:/Program Files/7-Zip/7z.exe", "a", "-r"]

    def __init__(self, project_path: str, dest_dir: str):
        """
        :param project_path: The path to the Unity project.
        :param dest_dir: Output the standalone builds to this directory.
        """

        home = str(Path.home().resolve())
        if "~" in project_path:
            project_path = project_path.replace("~", home)
        if "~" in dest_dir:
            dest_dir = dest_dir.replace("~", home)

        self.project_path = Path(project_path)
        assert self.project_path.exists(), f"Directory not found: {self.project_path.resolve()}"

        self.project_name = self.project_path.stem

        self.dest_dir = Path(dest_dir)
        # Create the output directory.
        if not self.dest_dir.exists():
            self.dest_dir.mkdir(parents=True)

    def get_unity_version(self) -> str:
        """
        Returns the Unity version of the TDWBase project.
        """

        p = self.project_path.joinpath("ProjectSettings/ProjectVersion.txt")
        return p.read_text().split(": ")[1].split("\n")[0].strip()

    def get_editor_path(self) -> str:
        """
        Returns the path to Unity Editor.
        """

        return f"C:/Program Files/Unity/Hub/Editor/{self.get_unity_version()}/Editor/Unity.exe"

    def get_unity_call(self) -> List[str]:
        """
        Returns the beginning of a Unity Editor call.
        """

        return [self.get_editor_path(), "-quit", "-batchmode"]

    def create_platform_directories(self) -> Dict[str, Path]:
        """
        Create directories for each platform.

        :return: The path to each destination directory. Key = platform.
        """

        platforms: Dict[str, Path] = {}
        for platform in Unity3DBuilder.PLATFORMS:
            platform_root_directory = self.dest_dir.joinpath(platform)
            if not platform_root_directory.exists():
                platform_root_directory.mkdir()
            platforms.update({platform: platform_root_directory})
        print(f"Created platform directories.")
        return platforms

    def create_build(self, platform: str, platform_path: Path) -> None:
        """
        Create the build for a platform.

        :param platform: The platform directory.
        :param platform_path: The path to the platform directory.
        """

        build_path = platform_path.joinpath(f"{self.project_name}{Unity3DBuilder.PLATFORMS[platform]['extension']}")

        build_call = self.get_unity_call()[:]
        build_call.extend([Unity3DBuilder.PROJECT_PATH_ARG,
                           str(self.project_path.resolve()),
                           Unity3DBuilder.PLATFORMS[platform]["call"],
                           str(build_path.resolve())])
        print(f"Creating build for {platform}...")
        call(build_call)

        print("...Done!")
        assert build_path.exists(), "Failed to create build."

    def zip(self, platform: str) -> Path:
        """
        Zip up the build.

        :param platform: The name of the platform.
        """

        # Get the current destination directory, e.g. Windows
        p = self.dest_dir.joinpath(platform)
        # Change the name of the directory to the project name, e.g. MyProject
        p.replace(self.dest_dir.joinpath(self.project_name))
        p = self.dest_dir.joinpath(self.project_name)
        # Get the zip file name, e.g. MyProject_Windows.zip
        dest = self.dest_dir.joinpath(f"{self.project_name}_{platform}.zip")

        # Create the zip file.
        zip_call = Unity3DBuilder.ZIP_CALL[:]
        zip_call.extend([str(dest.resolve()),
                         str(p.resolve()),
                         "-sdel"])
        call(zip_call)

        return dest


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--project", type=str, help="The path to the Unity project directory.")
    parser.add_argument("--dest", type=str, help="The path to the destination (output) directory.")
    args = parser.parse_args()

    rc = Unity3DBuilder(project_path=args.project, dest_dir=args.dest)
    release_directory, platform_directories = rc.create_platform_directories()

    zip_files: Dict[str, Path] = {}

    for platform_dir in platform_directories:
        # Create the build.
        rc.create_build(platform_dir, platform_directories[platform_dir])

        # Zip everything up.
        zip_file = rc.zip(platform_dir)
        zip_files.update({platform_dir: zip_file})

    # Upload the zip files.
    print("DONE!")
