import json
import os
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict

from ratisbona_utils.io import UTF8, get_config_dir

from ratisbona_utils.monads import Just, Nothing


def maybe_lsblk_full_info():
    return (
        Just(
            ["lsblk", "-o", "NAME,MODEL,FSTYPE,TYPE,LABEL,UUID,MOUNTPOINT,SERIAL,SIZE", "-J"]
        )
        .bind(subprocess.run, capture_output=True, text=True, check=True)
        .bind(lambda result: result.stdout)
        .bind(json.loads)
        .maybe_warn("Error running lsblk:")
    )


def search_for_vgs(blockdevice):
    maybe_device = Just(blockdevice)
    results = []
    if maybe_device["type"].default_or_throw("").startswith("lvm"):
        maybe_name = maybe_device["name"]
        if maybe_name:
            results.append(maybe_name.unwrap_value())

    for maybe_child in maybe_device["children"]:
        maybe_vgs = maybe_child.bind(search_for_vgs)
        for maybe_vg in maybe_vgs:
            if maybe_vg:
                results.append(maybe_vg.unwrap_value())
    return results


def list_mountpoints(blockdevice):
    maybe_device = Just(blockdevice)
    maybe_mountpoint = maybe_device["mountpoint"]
    mountpoints = []
    if maybe_mountpoint:
        mountpoints.append(maybe_mountpoint.unwrap_value())

    for maybe_child in maybe_device["children"]:
        maybe_mountpoints = maybe_child.bind(list_mountpoints)
        for a_mountpoint in maybe_mountpoints:
            if a_mountpoint:
                mountpoints.append(a_mountpoint.unwrap_value())
    return mountpoints


def maybe_list_mountpoint_contents(mountpoint):
    print(mountpoint)
    return (
        Just(["ls", mountpoint])
        .bind(subprocess.run, capture_output=True, text=True, check=True)
        .maybe_warn("Error running ls:")
        .bind(lambda result: result.stdout)
        .bind(str.splitlines)
        .maybe_recover(lambda _: Nothing)
    )


def get_statfile_path():
    return get_config_dir("ratisbona_diskinfo") / "stats.json"

def load_stats(stats_file: Path):

    if not stats_file.exists():
        return {}

    try:
        with stats_file.open("r", **UTF8) as f:
            data = json.load(f)
        disk_info_dict = {}
        for key, value in data.items():
            disk_info_dict[key] = DiskInfo(**value)
        return disk_info_dict

    except (json.JSONDecodeError, IOError) as e:
        print("Error loading stats file:", e)
        return {}


def save_stats(stats: Dict, stats_file: Path):
    try:
        with open(stats_file, "w") as f:
            json_dict = {}
            for key, value in stats.items():
                json_dict[key] = asdict(value)
            return json.dump(json_dict, f, indent=2)

    except IOError as e:
        print("Error saving stats file:", e)


@dataclass
class DiskInfo:
    model: str
    serial: str
    size: str
    volume_group: str | list[str]
    content: list[str]


def diskinfo_from_maybes(
    maybe_lsblk_result, maybe_vg_results, contents
) -> DiskInfo:
    return DiskInfo(
        model=maybe_lsblk_result["model"].default_or_throw(""),
        serial=maybe_lsblk_result["serial"].default_or_throw(""),
        size=maybe_lsblk_result["size"].default_or_throw(""),
        volume_group=maybe_vg_results.default_or_throw([]),
        content=contents,
    )


def lsblk_diskinfo() -> list[DiskInfo]:
    results = maybe_lsblk_full_info()

    disk_infos = []
    for maybe_result in results["blockdevices"]:
        if not maybe_result["model"]:
            continue
        maybe_vg_results = maybe_result.bind(search_for_vgs)
        maybe_mountpoints = maybe_result.bind(list_mountpoints)
        maybe_content = []
        for maybe_mountpoint in maybe_mountpoints:
            maybe_content_items = maybe_mountpoint.bind(maybe_list_mountpoint_contents)
            maybe_content.extend(maybe_content_items.default_or_throw([]))

        disk_infos.append(
            diskinfo_from_maybes(maybe_result, maybe_vg_results, maybe_content)
        )
    return disk_infos


def print_disk_info(disk_info: DiskInfo):
    print("Model: ", disk_info.model)
    print("Serial:", disk_info.serial)
    print("Size:  ", disk_info.size)
    print("VG:    ", disk_info.volume_group)
    print("Cont.: ", disk_info.content)
    print()
    print()


def update_diskinfo_dict(disk_info_dict, disk_info):
    key = f"{disk_info.model}-{disk_info.serial}"
    if key not in disk_info_dict:
        disk_info_dict[key] = disk_info
        return

    if disk_info.size != "":
        disk_info_dict[key].size = disk_info.size

    if disk_info.volume_group != "":
        disk_info_dict[key].volume_group = disk_info.volume_group

    if len(disk_info.content) > 0:
        disk_info_dict[key].content = disk_info.content
