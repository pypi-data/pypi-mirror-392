from asyncio import run
from fnmatch import fnmatch
from datetime import date, datetime
from functools import partial
from typing import Optional

import click
import json

from pathlib import Path

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.asyncio import run_command
from ratisbona_shellutils.dialogator.dialogator import (
    convert_to_latex,
    math_sanitze_markdown_text,
)
from ratisbona_shellutils.dialogator.chatgpt_parsing import (
    ChatGptFileContent,
    filter_conversations,
    ChatTitle,
    ChatGptConversation,
    translate_conversation,
)
from ratisbona_shellutils.dialogator.whatsapp_zip_parsing import (
    whatsapp_zip_to_dialog_md,
)
from ratisbona_utils.functional import first, nth_element, substitute_for_none
from ratisbona_utils.io import maybe_backup_file, UTF8, errprint
from ratisbona_utils.monads import Maybe


@click.group()
def dialogator_cli():
    errprint(blue_dosbox("    Dialogator Cli"))


async def stdout_callback(process, line):
    return
    print(f"STDOUT: {line}")


async def stderr_callback(process, line):
    print(f"STDERR: {line}")





@dialogator_cli.command("whats-parse")
@click.argument(
    "whatsapp_zip_txt_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
def whatsapp_zip_to_dialog_markdown_cli(whatsapp_zip_txt_file: Path):
    """
        First step in a whatsapp-dialogator-workflow. Parses a whatsapp-textfile from an whatsapp-export-zip
        into a dialog-markdown file (First headline-level = date, second headline-level = speaker).
        From that you can use the typeset subcomand to create a pdf.

        Args:
            whatsapp_zip_txt_file (Path): The path to the whatsapp-textfile from an whatsapp-export-zip.

        Side effects:
            Writes a markdown file to the same directory as the whatsapp_zip_txt_file.
    """
    maybe_backup_file(whatsapp_zip_txt_file)
    outfile = whatsapp_zip_txt_file.with_suffix(".md")
    with (
        whatsapp_zip_txt_file.open("r", **UTF8) as infile,
        outfile.open("w", **UTF8) as outfile,
    ):
        whatsapp_zip_to_dialog_md(infile, outfile)


@dialogator_cli.command("gpt-list")
@click.argument(
    "chatgpt_json",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
@click.option(
    "--date-filter-after",
    "-da",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="A date filter in isoformat. Only conversations with a first date after this date are listed.",
)
@click.option(
    "--date-filter-before",
    "-db",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="A date filter in isoformat. Only conversations with a first date before this date are listed.",
)
@click.option(
    "--title-filter",
    "-t",
    default=None,
    help="A title filter. Only conversations with a title containing this string are listed",
)
def list_chatgpt_dialog_names_cli(
    chatgpt_json: Path,
    date_filter_after: Optional[datetime],
    date_filter_before: Optional[datetime],
    title_filter: str,
):
    """
    First step in a gpt-dialogator-workflow. Allows you to identify, which conversations are in you conversations.json
    that you obtained from gpts data takeout.
    You can filter by date and title, by providing the respective options. Titles allow for wildcard matching.
    Lists the names of the chat gpt conversations, that would be selected by your filter criteria.

    Args:
        chatgpt_json (Path): The path to the chat gpt conversations.json file.
        date_filter_after (datetime): A date filter. Only conversations with a first date equal to or after this date are listed.
        date_filter_before (datetime): A date filter. Only conversations with a first date equal to or before this date are listed.
        title_filter (str): A title filter. Only conversations with a title containing this string are listed

    Side effects:
        Prints the names of the chat gpt conversations, that would be selected by your filter criteria
    """
    with chatgpt_json.open() as chatgpt_json_stream:
        chat_gpt_filecontent: ChatGptFileContent = json.load(chatgpt_json_stream)

    filtered_conversations: list[tuple[ChatTitle, date, ChatGptConversation]] = (
        filter_conversations(
            chat_gpt_filecontent,
            title_filter=title_filter,
            date_filter_after=date_filter_after,
            date_filter_before=date_filter_before,
        )
    )

    for title, the_date, _ in filtered_conversations:
        print(the_date, title)


@dialogator_cli.command()
@click.argument(
    "chatgpt_json",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
@click.option(
    "--date-filter-after",
    "-da",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="A date filter in isoformat. Only conversations with a first date after this date are listed.",
)
@click.option(
    "--date-filter-before",
    "-db",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=None,
    help="A date filter in isoformat. Only conversations with a first date before this date are listed.",
)
@click.option(
    "--title-filter",
    "-t",
    default=None,
    help="A title filter. Only conversations with a title containing this string are listed",
)
def gpt_filter_json(
    chatgpt_json: Path,
    date_filter_after: Optional[datetime],
    date_filter_before: Optional[datetime],
    title_filter: str,
):
    """
    Second step of a gpt-dialogator-workflow.
    Parses the chat gpt conversations, that would be selected by your filter criteria, creating an individual json file for each conversation.

    Args:
        chatgpt_json (Path): The path to the chat gpt conversations.json file.
        date_filter_after (datetime): A date filter. Only conversations with a first date equal to or after this date are listed.
        date_filter_before (datetime): A date filter. Only conversations with a first date equal to or before this date are listed.
        title_filter (str): A title filter. Only conversations with a title containing this string are listed


    Side effects:
        Writes a json file for each conversation that would be selected by your filter criteria.

    """
    print("Parsing", chatgpt_json)
    with chatgpt_json.open() as chatgpt_json_stream:
        chat_gpt_filecontent: ChatGptFileContent = json.load(chatgpt_json_stream)

    filtered_conversations: list[tuple[ChatTitle, date, ChatGptConversation]] = (
        filter_conversations(
            chat_gpt_filecontent,
            title_filter=title_filter,
            date_filter_after=date_filter_after,
            date_filter_before=date_filter_before,
        )
    )

    for title, the_date, result in filtered_conversations:
        filename = Path(
            the_date.isoformat()
            + "_-_"
            + title.lower().replace(" ", "_").replace("/", "_")
            + ".json"
        )
        print(f"Writing: {filename}")
        with filename.open("w", **UTF8) as outfile:
            json.dump(result, outfile, indent=2)


@dialogator_cli.command()
@click.argument(
    "filtered_json",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
def gpt_write_md(filtered_json: Path):
    with filtered_json.open() as infile:
        filtered_conversation = json.load(infile)
    title, result, first_date = translate_conversation(filtered_conversation)
    filename = filtered_json.with_suffix(".md")
    with filename.open("w", **UTF8) as outfile:
        outfile.write(result)



@dialogator_cli.command("typeset")
@click.argument(
    "dialog_markdown",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
)
def typeset_dialog_markdown_cli(dialog_markdown: Path):
    """
    Last step of any dialogator-workflow. This translates a dialoge-markdown (First headline-level = date, second headline-level = speaker) to a pdf.

    Args:
        dialog_markdown (Path): The path to the dialog markdown to translate.

    Side effects:
        Writes a tex file and a pdf file to the same directory as the dialog_markdown.
    """
    texfile = dialog_markdown.with_suffix(".tex")
    print("Converting", dialog_markdown, "to", texfile)
    markdown_text = dialog_markdown.read_text()

    markdown_text = math_sanitze_markdown_text(markdown_text)

    sanitized = dialog_markdown.with_suffix(".san.md")
    sanitized.write_text(markdown_text)

    latex_text = convert_to_latex(markdown_text, texfile.name.replace("_", " "))
    texfile.write_text(latex_text)
    workdir = texfile.parent
    # Run lualatex via subprocess write output to stdout
    print("Running lualatex in", workdir)
    retval = run(
        run_command(
            f'lualatex --shell-escape -interaction=nonstopmode "{texfile.name}"',
            stdout_callback,
            stderr_callback,
            cwd=workdir,
        )
    )
    if not retval == 0:
        print("ERROR: lualatex failed with return code", retval)


@dialogator_cli.command()
@click.argument(
    "json_files",
    type=click.Path(exists=True, dir_okay=False, file_okay=True, path_type=Path),
    nargs=-1,
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, file_okay=True, path_type=Path),
    help="The path to the output file. If not provided, the script will be printed to stdout."
)
def gpt_create_script(json_files, output: Path = None ):
    """
        Creates a script for steps 3-4 of a gpt-dialogator-workflow: gpt-write-md and typeset.
        After you took out your gpt data export and filtered it to single jsons using the gpt-filter-json command,
        you can use this to create a script that does the remaining translation steps.
        This will take into account, that maybe some of the files are already translated to md or pdf, in which case
        it will skip the translation steps for these files.
        
        Args:
            json_files (Path): The paths to the json files to translate.
            output (Path): The path to the output file. If not provided, the script will be printed to stdout.
        
        Side effects:
            Writes a script to the output file or prints it to stdout.
    """
    outstream = output.open("w", **UTF8) if output else click.get_text_stream("stdout")
    cprint = partial(print, file=outstream)

    try:
        for arg in json_files:
            md_file = arg.with_suffix(".md")
            pdf_file = arg.with_suffix(".pdf")

            if pdf_file.exists():
                cprint(f"# {arg} already translated to pdf. Ignoring.")
                continue

            if not md_file.exists():
                cprint(f"ratisbona_dialogator gpt-write-md {arg}")
            else:
                cprint(f"#Markdown file for {arg} already exists. Ignoring.")

            cprint(f"ratisbona_dialogator typeset {md_file}")
            cprint(f"open {pdf_file}")
            cprint("read a")
    finally:
        if output:
            outstream.close()
