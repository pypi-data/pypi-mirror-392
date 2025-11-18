import json
from pathlib import Path
import click

from ratisbona_shellutils.messysoft._messysoft import authenticate, get_session
from ratisbona_shellutils.messysoft._messysoft_chats import get_personal_chats, sort_by_last_updated, export_all_chats, \
    create_failed_links_html
from ratisbona_shellutils.messysoft._messysoft_mail import list_mail_folders, sync_all_folders
from ratisbona_utils.boxdrawing import blue_dosbox


@click.group()
def messysoft_cli():
    blue_dosbox("Ratisbona Messysoft")

@messysoft_cli.command()
def list_folders():
    session = get_session()
    access_token = authenticate(session)
    for id, name in list_mail_folders(token=access_token):
        print(f"{name}: {id}")

@messysoft_cli.command()
@click.argument("maildir_root", type=click.Path(exists=True, path_type=Path, dir_okay=True, file_okay=False))
@click.option("--include", multiple=True)
def sync_folders(maildir_root: Path, include: list[str]):
    session = get_session()
    access_token = authenticate(session=session)
    sync_all_folders(maildir_root=maildir_root, token=access_token, folder_filter=include)

@messysoft_cli.command()
def list_chats():
    session = get_session()
    access_token = authenticate(session)
    chats = get_personal_chats(token=access_token, session=session)
    chats = sort_by_last_updated(chats)
    for chat in chats:
        print(chat.get("topic"), chat.get("last_updated"))
        print(json.dumps(chat, indent=2))

def printstats(stats: dict):
    print(f"Num requests issued: {stats['num_requests']}")

@messysoft_cli.command()
@click.argument("output_dir", type=click.Path(path_type=Path, dir_okay=True, file_okay=False) )
def export_chats(output_dir: Path):
    session, stats = get_session()
    try:
        access_token = authenticate(session)
        export_all_chats(token=access_token, out_dir=output_dir, session=session)
    finally:
        printstats(stats)


@messysoft_cli.command()
@click.argument("attachment_json", type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True))
@click.option("-o", "--output", type=click.Path(exists=False, path_type=Path, dir_okay=False, file_okay=True), default=None)
def html_failed_links(attachment_json: Path, output: Path = None):
    create_failed_links_html(attachment_json, output)

