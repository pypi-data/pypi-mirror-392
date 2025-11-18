import time
from pathlib import Path

import click

from ratisbona_shellutils.twister import wiggle_wiggle
from ratisbona_shellutils.twister._shouter import type_text_osascript
from ratisbona_shellutils.twister.triple_click import TripleClickDetector
from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint


@click.group()
def twist_and_shout_cli():
    errprint(blue_dosbox("Ratisbona Twister"))
    pass  # Placeholder for future implementation

@twist_and_shout_cli.command()
def twist():
    wiggle_wiggle()

@twist_and_shout_cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True))
@click.option("--typing-speed", "-s", "typing_speed_chars_per_min", type=int, default=600, help="Typing speed in characters per minute (default: 300)")
def shout(file: Path, typing_speed_chars_per_min: int):
    print("Reading file:", file)
    text = file.read_text(encoding="utf-8")
    print("Text length:", len(text), "characters")

    # --- Dreifachklick erkennen ---
    print("Bitte führe einen Dreifachklick aus...")
    with TripleClickDetector() as detector:
        while not detector.triple_click:
            # Warten, bis der Dreifachklick erkannt wird
            time.sleep(0.1)

    print("Dreifachklick erkannt!")
    print("Starte Eingabe in 3 Sekunden...")
    time.sleep(1)
    print("... 2")
    time.sleep(1)
    print("... 1")
    time.sleep(1)
    print("Let's rock and roll! 🎸")

    # --- Text tippen ---

    chunksize = 128
    chunks = [text[i: i + chunksize] for i in range(0, len(text), chunksize)]

    with TripleClickDetector() as detector:
        for chunknum, chunk in enumerate(chunks):
            print(f"Tippe Chunk {chunknum + 1}/{len(chunks)}: {chunk[:20]}... ({len(chunk)} characters). Tripple-click to stop.")
            type_text_osascript(chunk, delay= 60.0 / typing_speed_chars_per_min)
            if detector.triple_click:
                print("Dreifachklick erkannt! Stoppe Eingabe.")
                break
            else:
                print("Kein Tripple-Click. Nächster Chunk wird getippt.")
        else:
            print("Alle Chunks erfolgreich getippt!")
