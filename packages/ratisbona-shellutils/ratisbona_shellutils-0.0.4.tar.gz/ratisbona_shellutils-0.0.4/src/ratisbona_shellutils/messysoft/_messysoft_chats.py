import datetime
import json
import uuid
from typing import Any

import requests
from pathlib import Path

from ratisbona_shellutils.messysoft._messysoft import GRAPH_BASE, AccessToken, USER_AGENT_HEADERS
from ratisbona_utils.io import UTF8
from ratisbona_utils.monads import Maybe

Chat = dict
Message = dict
Url = str
LocalFilename = str
AttachmentMap = dict[Url, tuple[LocalFilename, bool]]  # URL -> (Dateiname, Erfolgreich)



def get_personal_chats(*, token: AccessToken, session: requests.Session) -> list[Chat]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/me/chats?$top=50"
    chats = []

    while url:
        res = session.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        chats.extend(data.get("value", []))
        url = data.get("@odata.nextLink")

    return chats

def sort_by_last_updated(chats: list[Chat]) -> list[Chat]:

    def get_last_updated(chat: Chat) -> Any:
        field = chat.get("lastUpdatedDateTime")
        if not field:
            return datetime.datetime.min
        return datetime.datetime.fromisoformat(field)

    return sorted(chats, key=get_last_updated, reverse=True)


def get_chat_messages(chat_id: str,*, token: AccessToken, session: requests.Session) -> list[Message]:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages?$top=50"
    messages = []

    while url:
        try:
            res = session.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
            messages.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
        except Exception as e:
            print(f"⚠️ Fehler beim Abrufen der Nachrichten für Chat {chat_id}: {e}")
            break

    return messages

def already_exported_msg_ids(msg_dir: Path) -> set[str]:
    return {
        f.stem for f in msg_dir.glob("*.json")
    }

def download_attachments(
        msg: Message, attach_dir: Path, *, token: AccessToken, session: requests.Session
) -> AttachmentMap:
    headers = {"Authorization": f"Bearer {token}"}

    attachments = {}
    for att in msg.get("attachments", []):
        url = att.get("contentUrl")
        if not url:
            continue
        name = att.get("name") or f"{uuid.uuid4().hex}.bin"
        filename = f"{msg['id']}_{name}"
        try:
            r = session.get(url, headers=headers)
            r.raise_for_status()
            with open(attach_dir / filename, "wb") as f:
                f.write(r.content)
            attachments[url] = (filename, True)  # True bedeutet erfolgreicher Download
        except Exception as e:
            print(f"⚠️ Fehler beim Herunterladen {name}: {e}")
            attachments[url] = (filename, False)  # Fehler beim Download
    return attachments




def export_chat(chat: Chat, base_path: Path,*, token: AccessToken, session: requests.Session):
    chat_id = chat["id"]
    topic = chat.get("topic", "")
    messages = get_chat_messages(chat_id, token=token, session=session)

    # Neue Namenslogik
    participants = get_chat_participants_from_messages(messages)
    name_part = "_".join(n.replace(" ", "_") for n in participants) or "Unbekannt"
    dirname_parts = ["chat"]
    if topic:
        dirname_parts.append(topic.replace(" ", "_"))
    dirname_parts.append(name_part)
    dirname_parts.append(chat_id)
    dirname = '_'.join(dirname_parts)

    chat_dir = base_path / dirname
    msg_dir = chat_dir / "messages"
    att_dir = chat_dir / "attachments"
    msg_dir.mkdir(parents=True, exist_ok=True)
    att_dir.mkdir(exist_ok=True)

    # Metadaten speichern
    with open(chat_dir / "metadata.json", "w", **UTF8) as f:
        json.dump(chat, f, indent=2)

    exported_ids = already_exported_msg_ids(msg_dir)

    attachment_map = {}
    try:
        for msg in messages:
            if msg["id"] in exported_ids:
                continue
            fname = msg_dir / f"{msg['id']}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(msg, f, indent=2)
            attachment_map_delta = download_attachments(msg, att_dir, token=token, session=session)
            attachment_map.update(attachment_map_delta)
            print(f"💬 Exportiert: {fname.name}")
    finally:
        # Speichere die Zuordnung der Anhänge
        with open(chat_dir / "attachments.json", "w", encoding="utf-8") as f:
            json.dump(attachment_map, f, indent=2)

def export_all_chats(*, session: requests.Session, token: str, out_dir: Path):
    chats = get_personal_chats(token=token, session=session)
    for chat in chats:
        export_chat(chat, out_dir, token=token, session=session)

def get_chat_participants_from_messages(messages: list[dict], max_names: int = 3) -> list[str]:
    participants = set()
    for msg in messages:
        maybe_name = Maybe(msg)["from"]["user"]["displayName"].bind(str.strip)
        if maybe_name:
            participants.add(maybe_name.unwrap_value())
        if len(participants) >= max_names:
            break
    return sorted(participants)[:max_names]


def create_failed_links_html(json_path: Path, output_path: Path = None):
    output_path = output_path or json_path.with_suffix(".html")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = ["<html><head><meta charset='utf-8'><title>Fehlgeschlagene Downloads</title></head><body>"]
    html.append("<h1>Fehlgeschlagene Downloads</h1><ul>")
    for url, (filename, success) in data.items():
        if not success:
            escaped_url = url.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html.append(f'<li><a href="{escaped_url}" download="{filename}">{filename}</a></li>')
    html.append("</ul></body></html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    print(f"HTML-Datei erstellt: {output_path}")
