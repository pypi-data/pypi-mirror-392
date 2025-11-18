import configparser
import os
import subprocess
import sys
import zipfile
from datetime import datetime
from typing import Dict

import requests
import io

from more_itertools import last

from ratisbona_utils.functional import nth_element

PackageName = str
Version = str
PackageMetadata = dict
MetadataFile = str
WheelData = bytes


def get_metadata_from_wheel(package: PackageName, version: Version) -> PackageMetadata:
    # Lade JSON-Metadaten
    url = f"https://pypi.org/pypi/{package}/{version}/json"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ValueError(f"Version {version} of package {package} not found.")
    data = resp.json()
    return data

def get_versions(package_name: str):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Package {package_name} not found on PyPI.")

    data = response.json()

    filtered_data = []
    for version, version_files in data["releases"].items():
        first_date = min(datetime.fromisoformat(file["upload_time"]) for file in version_files)
        filtered_data.append((version, version_files, first_date))

    filtered_data.sort(key=nth_element(2))  # Sort by first upload date
    return filtered_data

def get_latest_version(package_name: str):
    versions = get_versions(package_name)
    return last(versions)[0]

def download_wheeldata_from_wheelinfo(data: PackageMetadata) -> WheelData:
    #print(json.dumps(data, indent=2))
    # Wähle ein .whl-File (idealerweise "py3-none-any")
    wheel_info = next((f for f in data["urls"] if f["filename"].endswith(".whl")), None)
    if not wheel_info:
        raise RuntimeError("No wheel file found for that version.")

    # Lade Wheel-Datei in den Speicher
    #print(f"Downloading: {wheel_info['filename']}")
    wheel_data = requests.get(wheel_info["url"]).content
    return wheel_data

def extract_metadata_from_wheeldata(wheel_data: WheelData) -> MetadataFile:

    # Entpacke die METADATA-Datei
    with zipfile.ZipFile(io.BytesIO(wheel_data)) as zf:
        metadata_path = next((name for name in zf.namelist() if name.endswith("METADATA")), None)
        if not metadata_path:
            raise RuntimeError("METADATA file not found in wheel.")

        with zf.open(metadata_path) as meta_file:
            metadata = meta_file.read().decode("utf-8")
            return metadata

def extract_entry_points_from_wheel(wheel_bytes: bytes) -> Dict[str, Dict[str, str]]:
    """
    Parsen der entry_points.txt aus einem Wheel.

    Rückgabe:
        { gruppe: { script_name: "modul:objekt" } }
    """
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as zf:
        # entry_points.txt liegt in <name>-<version>.dist-info/entry_points.txt
        ep_path = None
        for name in zf.namelist():
            if name.endswith("dist-info/entry_points.txt"):
                ep_path = name
                break

        if not ep_path:
            # Keine Entry Points im Wheel
            return {}

        with zf.open(ep_path) as f:
            data = f.read().decode("utf-8")

    parser = configparser.ConfigParser()
    parser.read_string(data)

    result: Dict[str, Dict[str, str]] = {}
    for section in parser.sections():
        entries: Dict[str, str] = {}
        for key, value in parser.items(section):
            entries[key] = value
        result[section] = entries

    return result

def extract_requires_dist_from_metadata(metadata: MetadataFile) -> list[str]:
    # Extrahiere "Requires-Dist"-Zeilen
    requires = [line for line in metadata.splitlines() if line.startswith("Requires-Dist:")]
    return requires


def extract_click_completions(script_name: str, completion_type: str = "zsh") -> list[str]:
    """
    Every click-based application can provide a completion script if you set
    the environment variable `SCRIPTNAME_COMPLETE` to `source_zsh` or `bash_source`.
    SCRIPTNAME therein is the name of the script without the extension.

    This command does the work for you, just provide the script name, like you would invoke it
    on the shell.

    Args:
        script_name: The name of the script.
        completion_type: Valid values are "zsh" and "bash".

    Returns:
        The completion script for the shell you chose.

    Raises:
        FileNotFoundError: If the script does not exist.
        RuntimeError: If the script does not provide completion.
    """
    env_values = {
        "zsh": "zsh_source",
        "bash": "bash_source",
    }

    if completion_type not in env_values:
        raise ValueError(f"Invalid completion type: {completion_type!r}")
    env_value = env_values[completion_type]
    env_var = f"_{script_name.replace('-', '_').upper()}_COMPLETE"

    env = os.environ.copy()
    env[env_var] = env_value
    proc = subprocess.run(
        [script_name],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    stdout_content = proc.stdout.strip()
    print(proc.stderr, file=sys.stderr)

    if proc.returncode != 0 or not stdout_content:
        msg = (
            f"[WARN] {script_name!r} hat keine gültige Completion ausgegeben "
            f"(rc={proc.returncode}). stderr:\n{proc.stderr}"
        )
        raise RuntimeError(msg)

    return stdout_content
