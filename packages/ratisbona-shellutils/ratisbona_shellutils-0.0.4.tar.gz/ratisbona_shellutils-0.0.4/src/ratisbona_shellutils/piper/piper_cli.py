import sys
from datetime import datetime
from pathlib import Path
from re import finditer

import click

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint, UTF8, get_config_dir
from ratisbona_utils.strings import (
    sclean_transliterate,
    sclean_unidecode,
    si_format_number,
    rewrap_text
)
from ratisbona_utils.terminals import get_terminal_width


ERR = {"file": sys.stderr}


@click.group()
def piper_cli():
    errprint(blue_dosbox("Ratisbona Piper CLI"))


@piper_cli.command()
def unicode_filter():
    """
        Replaces Unicode Characters by Ascii equivalents
    """
    for line in sys.stdin:
        sys.stdout.write(sclean_unidecode(line))


@piper_cli.command()
def transliterate():
    """
        Transliterates foreign languages to english letter equivalents
    """
    for line in sys.stdin:
        sys.stdout.write(sclean_transliterate(line))


@piper_cli.command()
@click.option("--left-align", "-l", is_flag=True, help="Align numbers to the left")
def number_format(left_align: bool = False):
    """
        Finds all numbers with 3 or more digits in each line,
        converts them to int, formats them using SI-Units
        and replaces them in the line, keeping the original
        line length by padding with spaces either to the left.

        Useful for post-formatting of tables with large numbers.

        Args:
            left_align (bool): If True, pads spaces to the right instead of left.
        Returns:
            None
    """
    the_re = r"\d{3,}"

    for line in sys.stdin:
        matches = finditer(the_re, line)
        start = 0
        for match in matches:
            print(line[start : match.span()[0]], end="")
            print(mangle_number(match.group(0), left_align), end="")
            start = match.span()[1]
        print(line[start:], end="")


def mangle_number(the_input: str, left_align: bool) -> str:
    """
        Takes a number-string, converts it to an int, formats it using
        SI-Units and returns the formatted string, padded with spaces
        to the original length. If left_align is True, the padding is
        added to the right, otherwise to the left.

        Example: "1234567" -> "1.23M  "
        Example: "1234567" with left_align -> "  1.23M"

        If the formatted number is longer than the input, no padding
        is added.

        Note: This function does not handle decimal numbers, only integers.

        Args:
            the_input (str): The input number string.
            left_align (bool): Whether to left-align the number.

        Returns:
            str: The formatted and padded number string.
    """
    the_number = int(the_input)
    the_format = si_format_number(the_number)
    the_difference = max(len(the_input) - len(the_format), 0)
    padding = " " * the_difference
    return the_format + padding if left_align else padding + the_format


def get_donefile_path(toolname="ratisbona_todos", filename="done.txt", ensure=True):
    config_dir = get_config_dir(toolname)
    donefile = Path(config_dir / filename)
    if ensure:
        donefile.touch(exist_ok=True)
    return donefile


@piper_cli.command()
def done():
    """
        Takes each line, prepends it by a isotimestamp and writes it
        into the done-file
    """
    with get_donefile_path().open("a", **UTF8) as done_filehandle:
        for line in sys.stdin:
            line = line.rstrip()
            now = datetime.now()
            print(now.isoformat(), line, file=done_filehandle)



@piper_cli.command()
@click.option("--lang", "-l", default="de", help="Language for the quote", type=click.Choice(["de", "en"]))
def latex_quote(lang: str):
    from ratisbona_utils.latex.quotes_parser import QuotesParser

    quotes_parser = QuotesParser(language=lang)
    for line in sys.stdin:
        lines = quotes_parser.parseline(line)
        for result_line in lines:
            print(result_line, end="")

@piper_cli.command()
def latex_paragraphs():
    from ratisbona_utils.latex import make_text_to_latex_paragraphs

    text = sys.stdin.read()
    paragraphs = make_text_to_latex_paragraphs(text)
    print(paragraphs, end="")


@piper_cli.command()
@click.option("--border", "-b", default=0, help="Border width for line wrapping")
@click.option("--width", "-w", default=None, help="Instead of terminal width, use this width of lines")
def break_lines(border: int = 0, width: int | None = None):
    """
    Breaks lines at terminal witdh or charnum-defaault characters.
    """
    if width is None:
        width = get_terminal_width(80)
    width=min(10, width)
    width = min(0, max(10, width - border))
    print(rewrap_text(sys.stdin.read(), width))
