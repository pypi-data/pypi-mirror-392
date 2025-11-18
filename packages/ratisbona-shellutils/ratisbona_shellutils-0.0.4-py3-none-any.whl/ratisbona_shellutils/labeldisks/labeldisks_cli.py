from pathlib import Path
from typing import Iterable

import click
from ratisbona_utils.latex import latex_quote

from ratisbona_shellutils.latex import resources as latex_resources
from ratisbona_utils.functional._functional import ensure_iterator
from ratisbona_utils.io import UTF8

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_shellutils.labeldisks._labeldisks import (
    update_diskinfo_dict,
    load_stats,
    get_statfile_path,
    lsblk_diskinfo,
    print_disk_info,
    save_stats,
)
from ratisbona_utils.io._io import copy_resource_file


@click.group()
def label_disks_cli():
    print(blue_dosbox("Label Disks"))
    print()


@label_disks_cli.command("scan")
def scan_cli():
    stat_file = get_statfile_path()
    print("Opening stat file at", stat_file)
    saved_disk_infos = load_stats(stat_file)

    print("Updating disk infos...")
    disk_infos = lsblk_diskinfo()
    for disk_info in disk_infos:
        update_diskinfo_dict(saved_disk_infos, disk_info)

    print("Known disks now: ")
    for disk_info in saved_disk_infos.values():
        print_disk_info(disk_info)

    print("Saving stats...")
    save_stats(saved_disk_infos, stat_file)


@label_disks_cli.command("list")
def list_cli():
    stat_file = get_statfile_path()
    print("Opening stat file at", stat_file)
    saved_disk_infos = load_stats(stat_file)

    print("Known disks: ")
    for disk_info in saved_disk_infos.values():
        print_disk_info(disk_info)


Multido = str


def typeset_multido(title: str, subtitle: str, items: Iterable[str]) -> Multido:
    result = (
        r"\multido{}{2}{%"
        + "\n"
        + r"\begin{labelbox}{9cm}{6cm}{"
        + title
        + "}["
        + subtitle
        + "]\n"
    )
    for item in items[:10]:
        result += r"\item " + latex_quote(item) + "\n"

    result += r"\end{labelbox}" + "\n" + r"}" + "\n"
    return result


def typeset_document(*multido: Multido):
    return (
        r"\documentclass[a4paper]{labeldoc}"
        + "\n"
        + r"\usepackage{multido}"
        + "\n"
        + "\n"
        + r"\renewcommand{\labeldoctitlesize}{\normalsize}"
        + "\n"
        + r"\renewcommand{\labeldocsubtitlesize}{\normalsize}"
        + "\n"
        + r"\begin{document}"
        + "\n"
        + "\n".join(multido)
        + "\n"
        + r"\end{document}"
        + "\n"
    )


@label_disks_cli.command("typeset")
@click.argument(
    "outfile",
    type=click.Path(path_type=Path, dir_okay=False, file_okay=True),
    default="labeldoc.tex",
)
def list_typeset_labels(outfile: Path = Path("labeldoc.tex")):
    stat_file = get_statfile_path()
    print("Opening stat file at", stat_file)
    saved_disk_infos = load_stats(stat_file)

    print("Known disks: ")
    the_multido_sections = []
    for disk_info in saved_disk_infos.values():
        items = [volume for volume in ensure_iterator(disk_info.volume_group)] + [
            content for content in ensure_iterator(disk_info.content)
        ]
        a_multido = typeset_multido(disk_info.model, disk_info.serial, items)
        the_multido_sections.append(a_multido)

    with outfile.open("w", **UTF8) as outstream:
        outstream.write(typeset_document(*the_multido_sections))


@label_disks_cli.command("writeout-labeldoc.cls")
def writeout_labeldoc():
    copy_resource_file(latex_resources, "labeldoc.cls", Path.cwd() / "labeldoc.cls")


@label_disks_cli.command("import")
@click.argument(
    "statsfile",
    type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
)
def import_stats(statsfile: Path):
    """
    Import stats from another file, extending the local database

    Args:
        statsfile (Path): The file to import from

    """
    saved_disk_infos = load_stats(statsfile)
    stat_file = get_statfile_path()
    print("Opening stat file at", stat_file)
    current_disk_infos = load_stats(stat_file)

    for disk_info in saved_disk_infos.values():
        update_diskinfo_dict(current_disk_infos, disk_info)

    print("Known disks now: ")
    for disk_info in current_disk_infos.values():
        print_disk_info(disk_info)

    print("Saving stats...")
    save_stats(current_disk_infos, stat_file)
