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
    # Zip base call.
    ZIP_CALL = ["wsl", "zip", "-rm"]

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

    def create_build(self, platform: str, platform_path: Path, exe_name: str = None) -> None:
        """
        Create the build for a platform.

        :param platform: The platform directory.
        :param platform_path: The path to the platform directory.
        :param exe_name: The name of the executable. If None, use the project name.
        """

        if exe_name is None:
            exe_name = self.project_name

        build_path = platform_path.joinpath(f"{exe_name}{Unity3DBuilder.PLATFORMS[platform]['extension']}")

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

    def chmod(self, platform: str) -> None:
        """
        Run wsl chmod +x
        Ignored if WSL 2 is not installed.

        :param platform: The name of the platform.
        """

        if platform == "Windows":
            return

        if platform == "OSX":
            p = self.dest_dir.joinpath(f"OSX/{self.project_name}.app/Contents/MacOS/{self.project_name}")
        elif platform == "Linux":
            p = self.dest_dir.joinpath(f"Linux/{self.project_name}.x86_64")
        else:
            raise Exception(f"Platform not supported: {platform}")

        assert p.exists(), f"File not found: {p.resolve()}"
        try:
            p = str(p.resolve())
            p = f"/mnt/c/{p[2:]}".replace("\\", "/")
            call(["wsl", "chmod", "+x", p])
        except FileNotFoundError:
            return

    def create(self) -> None:
        """
        Create each standalone build and zip it up.
        """

        platform_directories = self.create_platform_directories()

        zip_files: Dict[str, Path] = {}

        for platform_dir in platform_directories:
            # Create the build.
            self.create_build(platform_dir, platform_directories[platform_dir])
            # Run chmod +x
            self.chmod(platform=platform_dir)

            # Zip everything up.
            zip_file = self.zip(platform_dir)
            zip_files.update({platform_dir: zip_file})
        print("DONE!")


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--project", type=str, help="The path to the Unity project directory.")
    parser.add_argument("--dest", type=str, help="The path to the destination (output) directory.")
    args = parser.parse_args()

    ub = Unity3DBuilder(project_path=args.project, dest_dir=args.dest)
    ub.create()
