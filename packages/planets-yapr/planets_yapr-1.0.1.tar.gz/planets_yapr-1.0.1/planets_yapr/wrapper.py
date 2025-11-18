import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable
from contextlib import contextmanager

# Reused what YAMS used : https://github.com/randovania/YAMS/blob/2.8.0/am2r_yams/wrapper.py#L12-L20
yapr_path = os.fspath(Path(__file__).with_name(name="yapr"))
sys.path.append(yapr_path)
from pythonnet import load, unload

class YaprException(Exception):
    pass

class Wrapper:
    def __init__(self, lib):
        self.csharp_patcher = lib

    def get_csharp_version(self) -> str:
        return self.csharp_patcher.Version
    
    def patch_game(
        self,
        input_path: Path,
        output_path: Path,
        patch_data: dict,
        progress_update: Callable[[str, float], None],
    ):
        # Copy to input dir to temp dir first to do operations there
        progress_update("Copying to temporary path...", 0)
        tempdir = tempfile.TemporaryDirectory()
        tempdir_path = Path(tempdir.name)
        shutil.copytree(input_path, tempdir.name, dirs_exist_ok=True)

        # Get data.win path. Both of these *need* to be strings, as otherwise patcher won't accept them.
        output_data_win: str = os.fspath(
            _prepare_environment_and_get_data_win_path(tempdir.name)
        )
        input_data_win: str = shutil.move(output_data_win, output_data_win + "_orig")
        input_data_win_path = Path(input_data_win)

        # Temp write patch_data into json file for yapr later
        progress_update("Creating json file...", 0.3)
        json_file: str = os.fspath(
            input_data_win_path.parent.joinpath("yapr-data.json")
        )
        with open(json_file, "w+") as f:
            f.write(json.dumps(patch_data, indent=2).replace('\r\n', '\n'))

        # Patch data.win
        progress_update("Patching data file...", 0.6)
        self.csharp_patcher.Main(input_data_win, output_data_win, json_file)

        # Rename executable to corresponding planet
        result_exe_name = "ERROR???"
        match patch_data["level_data"]["room"]:
            case "rm_Zebeth":
                result_exe_name = "Planets_Zebeth.exe"
            case "rm_Novus":
                result_exe_name = "Planets_Novus.exe"
        os.replace(tempdir_path.joinpath("Metroid Planets v1.27g.exe"), tempdir_path.joinpath(result_exe_name))

        # Move temp dir to output dir and get rid of it. Also delete original data.win
        # Also delete the json if we're on a race seed.
        if not patch_data.get("configuration_identifier", {}).get("contains_spoiler", False):
            input_data_win_path.parent.joinpath("yapr-data.json").unlink()
        input_data_win_path.unlink()
        progress_update("Moving to output directory...", 0.8)
        shutil.copytree(tempdir.name, output_path, dirs_exist_ok=True)
        shutil.rmtree(tempdir.name)

        progress_update("Exporting finished!", 1)

def _load_cs_environment():
    # Load dotnet runtime
    load("coreclr")
    import clr

    clr.AddReference("YAPR-LIB")

@contextmanager
def load_wrapper() -> Wrapper:
    try:
        _load_cs_environment()
        from YAPR_LIB import Patcher as CSharp_Patcher
        yield Wrapper(CSharp_Patcher)
    except Exception as e:
        raise e
        
def _prepare_environment_and_get_data_win_path(folder: str) -> Path:
    return Path(folder).joinpath("data.win")