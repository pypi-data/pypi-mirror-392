import sys
from datetime import datetime
from typing import Sequence

import click
import requests

from ratisbona_shellutils.pypi_research._pipy_research import (
    get_metadata_from_wheel, extract_requires_dist_from_metadata,
    download_wheeldata_from_wheelinfo, extract_metadata_from_wheeldata,
    extract_entry_points_from_wheel, extract_click_completions,
    get_versions, get_latest_version
)
from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.functional import nth_element
from ratisbona_utils.strings import si_format_number


@click.group
def pypi_research_cli():
    blue_dosbox("Ratisbona PyPi Research CLI")

@pypi_research_cli.command("get-versions")
@click.argument("package_name")
@click.option("--show-files", is_flag=True, help="Show files for each version", default=False)
def cli_get_versions(package_name: str, show_files: bool):
    # version, version_files, first_date\
    filtered_data = get_versions(package_name)

    for version, version_files, first_date in filtered_data:
        print(f"Version: {version}, {first_date.date().isoformat()}")
        if show_files:
            for file in version_files:
                print(f"  - {file['filename']}, {file['upload_time']} ({si_format_number(file['size'])}B)")


@pypi_research_cli.command()
@click.argument("package_name")
@click.argument("version")
def requires(package_name: str, version: str):
    wheelinfo = get_metadata_from_wheel(package_name, version)
    wheeldata = download_wheeldata_from_wheelinfo(wheelinfo)
    metadatafile = extract_metadata_from_wheeldata(wheeldata)
    metadatas = extract_requires_dist_from_metadata(metadatafile)
    for metadata in metadatas:
        print(metadata)

@pypi_research_cli.command()
@click.argument("package_name")
@click.argument("version")
def list_entrypoints(package_name: str, version: str):
    wheelinfo = get_metadata_from_wheel(package_name, version)
    wheeldata = download_wheeldata_from_wheelinfo(wheelinfo)
    entrypoints = extract_entry_points_from_wheel(wheeldata)
    for point, poitinfo in entrypoints.items():
        print(f"{point}: ")
        for key, value in entrypoints[point].items():
            print(f"  - {key}: {value}")

@pypi_research_cli.command()
@click.argument("script_names", type=str, required=True, nargs=-1)
@click.option(
    "--completion-type", "-t",
    type=click.Choice(["bash", "zsh"]),
    default="zsh",
    help="Type of completion to generate"
)
def print_completion(script_names: list[str], completion_type: str = "zsh"):
    do_print_completion(script_names, completion_type)

def do_print_completion(script_names: Sequence[str], completion_type: str = "zsh"):
    for script_name in script_names:
        print(f"Completion for: {script_name}...", file=sys.stderr)
        try:
            print(extract_click_completions(script_name, completion_type))
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
    print(f"Für sofortige Aktivierung:\n   source <(...)", file=sys.stderr)

@pypi_research_cli.command()
@click.argument("package_names", type=str, required=True, nargs=-1)
def download_completion(package_names: list[str]):
    for package_name in package_names:
        wheelinfo = get_metadata_from_wheel(package_name, get_latest_version(package_name))
        wheeldata = download_wheeldata_from_wheelinfo(wheelinfo)
        entrypoints = extract_entry_points_from_wheel(wheeldata)
        do_print_completion(entrypoints['console_scripts'])

