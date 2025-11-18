import csv
import os
import re
from pathlib import Path
from typing import Optional, Sequence
from difflib import SequenceMatcher

import click

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint
from ratisbona_utils.strings import (
    cleaners,
    string_cleaner,
    quote_for_bash_double_quotes,
)


def print_mv(src: str, dst: str):
    if src == dst:
        errprint(f"# No change, skipping {src}")
        return
    move_command = "mv -i -v "
    padding = " " * len(move_command)
    print(
        f"{move_command}{quote_for_bash_double_quotes(src)} \\\n{padding}{quote_for_bash_double_quotes(dst)}"
    )


def print_ln(target: Path, links_path: Path):
    link_command = "ln -sr "
    padding = " " * len(link_command)

    bash_text = (
        f"{link_command}{quote_for_bash_double_quotes(str(target))}\\\n"
        f"{padding}{quote_for_bash_double_quotes(str(links_path))}"
    )
    print(bash_text)


def find_all_files(root_dir: Path):
    errprint("Scanning for files in", root_dir)
    """Erstelle ein Mapping von Dateinamen zu Pfaden"""
    file_index = []

    for path in root_dir.rglob("*"):
        errprint(f"Found file: {path}")
        if path.is_file() and not path.is_symlink():
            file_index.append(Path(path))
        else:
            errprint("Not a regular file!")
    return file_index


def filter_broken_symlinks(paths: Sequence[Path]):
    """Finde alle kaputten Symlinks"""
    broken_links = []
    for path in paths:
        if path.is_symlink() and not path.exists():
            broken_links.append(path)
    return broken_links


@click.group()
@click.pass_context
def fileorga_cli(ctx):
    errprint(blue_dosbox("    Ratisbona File Organisation CLI"))
    ctx.ensure_object(dict)


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_broken_symlinks(root_dir: Path):
    broken_links = []
    for path in root_dir.rglob("*"):
        if path.is_symlink() and not path.exists():
            broken_links.append(Path(path))
    return broken_links


@fileorga_cli.command("relink")
@click.argument("root_dir", type=click.Path(exists=True, dir_okay=True, path_type=Path))
@click.argument(
    "links_to_correct", type=click.Path(dir_okay=True, path_type=Path), nargs=-1
)
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=0.95,
    help="Minimum similarity score to consider a match (default: 0.95)",
)
def repair_symlinks(root_dir: Path, links_to_correct: list[Path], threshold=0.95):
    errprint("Entering Routine!")
    all_files = find_all_files(root_dir)
    broken_links = filter_broken_symlinks(links_to_correct)

    repaired = 0
    skipped = 0
    interactive = 0

    for link in broken_links:
        original_target = os.readlink(link)
        target_name = os.path.basename(original_target)
        mangled_target_name = target_name
        for name, (cleaner, docstring) in cleaners.items():
            mangled_target_name = cleaner(mangled_target_name)


        candidates = []
        for file_path in all_files:
            score = similarity(target_name, file_path.name)
            #errprint(f"Examinging: {file_path} {file_path.name} vs. {target_name} score: {score}")
            candidates.append((score, file_path))
            mangled_file_path_name = file_path.name
            for name, (cleaner, docstring) in cleaners.items():
                mangled_file_path_name = cleaner(mangled_file_path_name)
            score = similarity(mangled_target_name, mangled_file_path_name)
            errprint(f"Examinging: {mangled_target_name} vs. {mangled_file_path_name} -- Score: {score}")
            candidates.append((score, file_path))

        candidates.sort(reverse=True, key=lambda tup: tup[0])

        if not candidates:
            errprint(f" [!] Keine Kandidaten für {link}")
            skipped += 1
            continue

        errprint(f"Best Candidates for {link}:")
        for score, match in candidates[:10]:
            errprint(f"Score: {score:0.5f} {match}")

        best_score, best_match = candidates[0]
        if best_score >= threshold:
            try:
                rel_path = os.path.relpath(best_match, start=link.parent)
                new_link = link.with_name(link.stem + "_restored" + link.suffix)
                print_ln(rel_path, new_link)
                errprint(
                    f" [✓] Repariert: {link} → {rel_path} (Score: {best_score:.2f})"
                )
                repaired += 1
            except Exception as e:
                errprint(f" [!] Fehler beim Reparieren von {link}: {e}")
                skipped += 1
        else:
            errprint(
                f" [ ] Unsicher bei {link} → Ähnlichster Treffer: {best_match.name} (Score: {best_score:.2f})"
            )
            interactive += 1

    errprint("\nZusammenfassung:")
    errprint(f"  Repariert automatisch: {repaired}")
    errprint(f"  Übersprungen (Fehler oder keine Treffer): {skipped}")
    errprint(f"  Unsichere Fälle (Score < {threshold:.2f}): {interactive}")


@fileorga_cli.command()
@click.argument("regular_expression", type=str)
@click.argument("replacement", type=str)
@click.argument("args", nargs=-1)
def regexp(regular_expression: str, replacement: str, args: list[str]):
    """
    Rename files using a regular expression.

    The regular expression is applied to the filename. The replacement string is used to create the new filename.

    Args:
        regular_expression (str): The regular expression to match the filename
        replacement (str): The replacement string. You can use \\1, \\2, ... to refer to the matched groups.
        args (list[str]): The files to rename

    Returns:
        None

    Side Effects:
        Prints the rename command to stdout, so you can change it or maybe just pipe it through bash to run it.
    """
    for src in args:
        full_path = Path(src)
        file_name = full_path.name
        file_path = full_path.parent
        dst = re.sub(regular_expression, replacement, file_name)
        dst_path = file_path / dst
        print_mv(src, str(dst_path))


@fileorga_cli.command()
@click.argument("args", nargs=-1)
def cut_otr_postfix(args: list[str]):
    """
    Remove a postfix like "_XX_YYYYMMDD_HHMMSS_TVOON_DE.mpg" from the filename as the online tv-recorder
    uses to append it. This is useful for renaming files that have been downloaded from the online tv-recorder.

    Args:
        args (list[str]): The files to rename.

    Returns:
        None

    Side Effects:
        Prints the rename command to stdout, so you can change it or maybe just pipe it through bash to run it.
    """
    regexp(
        regular_expression=r"_([0-9]{2}[\._-])+[a-z0-9]+_[0-9]{1,3}_TVOON_DE(\.mpg)?(\.HQ)?",
        replacement="",
        args=args,
    )


@fileorga_cli.command("to-excel")
@click.argument(
    "in_csv",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.argument(
    "out_csv",
    type=click.Path(writable=True, path_type=Path),
    default=None,
    required=False,
)
def convert_ordinary_to_excel_csv(in_csv: Path, out_csv: Optional[Path]):
    """
    Convert a CSV file with comma as delimiter to a CSV file with semicolon as delimiter,
    which is the default for German Excel installations. This is done by reading the input file
    line by line and writing the output file line by line. The input file is expected to be in UTF-8 encoding.

    Args:
        in_csv (Path): Path to the input CSV file.
        out_csv (Path): Path to the output CSV file. If not provided, it will be created in the same directory
                        as the input file with "_excel" appended to the filename.
    """
    if not out_csv:
        out_csv = (in_csv.parent / (in_csv.stem + "_excel")).with_suffix(".csv")
    convert_csv(in_csv, out_csv)


def try_convert_decimal(value: str) -> str:
    """
    Convert only numeric values with a dot as a decimal separator.

    Args:
        value (str): The value to convert.

    Returns:
        str: The converted value with a comma as a decimal separator if it was numeric,
             otherwise the original value.
    """
    try:
        # Try converting to float, then format it properly
        float_value = float(value)
        return str(float_value).replace(".", ",")
    except ValueError:
        # If conversion fails, return the original value (it's likely text)
        return value


def convert_csv(input_file, output_file):
    """
    Convert a CSV file with comma as delimiter to a CSV file with semicolon as delimiter, which
    is the default for German Excel installations. This is done by reading the input file line by line
    and writing the output file line by line. The input file is expected to be in UTF-8 encoding.

    Args:
        input_file (Path): Path to the input CSV file.
        output_file (Path): Path to the output CSV file.

    Raises:
        IOError: If there is an error reading the input file or writing the output file.

    Returns:
        None

    Side Effects:
        Creates the output file with semicolon as delimiter.
        Prints the progress of the conversion to stderr.
    """
    with (
        open(input_file, newline="", encoding="utf-8") as infile,
        open(output_file, "w", newline="", encoding="utf-8") as outfile,
    ):
        reader = csv.reader(infile, delimiter=",", quotechar='"')
        writer = csv.writer(
            outfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        for idx, row in enumerate(reader):
            if idx % 1000 == 0:
                errprint(f"Processing row {idx + 1}")
            new_row = [try_convert_decimal(cell) for cell in row]
            writer.writerow(new_row)


@fileorga_cli.command()
@click.argument("args", nargs=-1)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show details on filename cleanup on stderr"
)
def rename(verbose: bool, args: list[str], **kwargs):
    apply_cleaners = []

    if kwargs.get("all"):
        apply_cleaners.extend(cleaners.keys())

    # print(kwargs)

    for cleaner in cleaners:
        gui_name = cleaner.replace("_", "-")
        if kwargs.get(gui_name) or kwargs.get(cleaner):
            if cleaner not in apply_cleaners:
                apply_cleaners.append(cleaner)
        if kwargs.get(f"no-{gui_name}") or kwargs.get(f"no_{cleaner}"):
            # print("Removing cleaner", cleaner)
            apply_cleaners.remove(cleaner)

    def change_callback(cleaner, original_string, new_string):
        newfilestart = "->"
        if verbose:
            errprint(f"# {cleaner:20s}: {original_string}")
            errprint(f"# {newfilestart:20s}: {new_string}")
            errprint()

    for src in args:
        full_path = Path(src)
        file_name = full_path.name
        file_path = full_path.parent
        dst = string_cleaner(file_name, apply_cleaners, change_callback=change_callback)
        dst_path = file_path / dst
        print_mv(src, str(dst_path))


# Dynamically add cleaners to rename-function
for option, (the_function, the_help) in cleaners.items():
    option = option.replace("_", "-")
    rename = click.option(
        f"--{option}", is_flag=True, help=f"Enable {option}: " + the_help
    )(rename)
    rename = click.option(
        f"--no-{option}", is_flag=True, help=f"Disable {option}: " + the_help
    )(rename)
rename = click.option("--all", is_flag=True, help="Enable all cleaners")(rename)


def find_offset(data: bytes, max_line_length: int = 1000, max_nonascii: int = 5):
    """
    Finds the offset in a GOG installer file where the binary data begins.
    This is done by searching for the last line of ASCII data in the file.
    The function returns the offset of the first byte of binary data.

    Args:
        data (bytes): The binary data of the GOG installer file.
        max_line_length (int): The maximum length of a line in bytes.
        max_nonascii (int): The maximum number of non-ASCII characters allowed in a line.

    Returns:
        int: The offset of the first byte of binary data. Will return 0 if no offset is found.
    """
    last_newline = -1
    nonascii_count = 0
    line_start = 0

    for i, byte in enumerate(data):
        if byte == 0x0A:  # Zeilenende '\n'
            if nonascii_count > max_nonascii:
                return last_newline + 1
            last_newline = i
            nonascii_count = 0
            line_start = i + 1
        else:
            if not (32 <= byte <= 126 or byte in (9, 13)):  # ASCII plus Tab und CR
                nonascii_count += 1

        if i - line_start > max_line_length:
            return last_newline + 1

    # Falls Datei sauber durchläuft (sehr unwahrscheinlich), Offset ans Ende setzen
    return last_newline + 1


@fileorga_cli.command("extract-gog", short_help="Depack a GOG installer")
@click.argument(
    "installer_path",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.argument(
    "output_dir",
    type=click.Path(exists=False, dir_okay=True, writable=True, path_type=Path),
    default=None,
    required=False,
)
def extract_gog(installer_path: Path, output_dir: Path):
    """
    Depacks a GOG installer file. Gog installers are usually self-extracting archives
    based on sh and gzip. A executable header is prepended to the gzip data.
    This searches for the last line of ascii data and extracts the gzip data from there.

    Args:
        installer_path (Path): Path to the GOG installer file.
        output_dir (Path): Directory to save the extracted payload to.
    """
    if not output_dir:
        output_dir = installer_path.parent / (installer_path.stem + "_extracted")
    extract_gog_installer(installer_path, output_dir)


def extract_gog_installer(installer_path: Path, output_dir: Path):
    """
    Depacks a GOG installer file. Gog installers are usually self-extracting archives
    based on sh and gzip. A executable header is prepended to the gzip data.
    This searches for the last line of ascii data and extracts the gzip data from there.

    Args:
        installer_path (Path): Path to the GOG installer file.
        output_dir (Path): Directory to save the extracted payload to.

    Raises:
        ValueError: If the offset cannot be found in the installer file.
        IOError: If there is an error reading the installer file or writing the output file.

    Returns:
        None

    Side Effects:
        Creates output_dir if it does not exist already.
        Writes the extracted payload to a file named "payload.bin" in output_dir.
        Prints the offset detected in the installer file as well as the output file path.
    """
    with open(installer_path, "rb") as f:
        data = f.read()

    offset = find_offset(data)
    if offset is None:
        raise ValueError(
            "Cannot find the offset at which binary data begin. Maybe it's not in the gog-installer format?"
        )

    print(f"Offset detected: {offset} bytes")

    binary_data = data[offset:]

    output_dir.mkdir(exist_ok=True, parents=True)

    output_file = output_dir / "payload.bin"
    with output_file.open("wb") as f:
        f.write(binary_data)

    print(f"Depacked binary content to {output_file}")


@fileorga_cli.command("extract-gog-installer")
@click.argument(
    "installer_file",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
def extract_gog_sh_installer(installer_file: Path):
    """
    Depacks a GOG installer file. Gog installers are usually self-extracting archives
    based on sh and gzip. A executable header is prepended to the gzip data.
    This searches for the last line of ascii data and extracts the gzip data from there.

    Args:
        installer_file (Path): Path to the GOG installer file.
    """
    output_dir = installer_file.parent / (installer_file.stem + "_extracted")
    extract_gog_installer(installer_file, output_dir)
