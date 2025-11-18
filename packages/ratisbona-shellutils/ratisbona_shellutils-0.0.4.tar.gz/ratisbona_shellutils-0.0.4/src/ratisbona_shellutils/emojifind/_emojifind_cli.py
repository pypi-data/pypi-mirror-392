import sys

import click
import json
from pathlib import Path


from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint
from ratisbona_utils.click_extensions import DefaultGroup
from ._emojifind import search_emojis, get_additional_dbentries, get_user_dbentries, write_dbentries, merge_dbentries

@click.group(cls=DefaultGroup, default_cmd="search", invoke_without_command=True)
def emojifind_cli():
    errprint(blue_dosbox("Ratisbona Emojifind CLI"))


@emojifind_cli.command()
@click.argument("keyword")
@click.option("-m", "--max-results", default=10, help="Maximale Anzahl an Ergebnissen")
def search(keyword: str, max_results: int):
    matches = search_emojis(keyword, max_results=max_results)

    for number, (desc, beschreibung, emoji_char) in enumerate(matches):
        print(f"{number}: {emoji_char}  {desc} {beschreibung}")

    result_text = " ".join([emoji_char for _, __, emoji_char in matches])
    app = QApplication([])  # Muss existieren für Clipboard
    clipboard = QGuiApplication.clipboard()
    clipboard.setText(result_text)

@emojifind_cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(exists=False, path_type=Path),
    required=False, default=None,
    help="Pfad zur Ausgabedatei"
)
def export(output: Path | None):
    """
    Exportiert die Emojis in eine Datei.
    """

    additional_data = get_additional_dbentries()
    additional_data = merge_dbentries(additional_data, get_user_dbentries())
    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(additional_data, f, indent=2, ensure_ascii=False)
        print(f"{len(additional_data)} Emojis wurden in {output} exportiert.")
    else:
        for emoji, data in additional_data.items():
            print(f"{emoji}: {data}")

@emojifind_cli.command()
@click.argument("emoji", required=True, type=str)
@click.option("--lang", "-l", default="en", type=click.Choice(["en", "de"]), help="Language code of the emoji description (en or de)")
@click.argument("keywords", required=False, type=str, nargs=-1)
def register(emoji: str, lang: str, keywords: list[str]):
    """
    Registriert ein Emoji in der Datenbank.
    """
    additional_data = get_user_dbentries()

    if not emoji in additional_data:
        additional_data[emoji] = {"en": [], "de":[]}

    for keyword in keywords:
        print(f"Registriere Emoji: {emoji} in Sprache {lang} mit Keyword: {keyword}")
        additional_data[emoji][lang].append(keyword)

    write_dbentries(additional_data)
