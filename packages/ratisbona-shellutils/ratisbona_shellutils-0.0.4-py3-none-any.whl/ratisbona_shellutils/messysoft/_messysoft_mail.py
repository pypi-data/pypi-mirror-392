import json
import uuid
from pathlib import Path

import requests

from ratisbona_shellutils.messysoft._messysoft import AccessToken, GRAPH_BASE, USER_AGENT_HEADERS

def ensure_maildir_structure(base_path: Path, folder_name: str):
    path = base_path / folder_name
    for sub in ["cur", "new", "tmp"]:
        (path / sub).mkdir(parents=True, exist_ok=True)
    return path / "new"

def download_mail_as_eml(message_id: str, token: str) -> str:
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{GRAPH_BASE}/me/messages/{message_id}/$value"
    response = requests.get(url, headers={**headers, **USER_AGENT_HEADERS})
    if not response.ok:
        raise Exception(f"Fehler beim Abrufen von {message_id}: {response.text}")
    return response.text  # raw .eml

def export_folder_to_maildir(maildir_root: Path, folder_id: str, folder_name: str, *, token: AccessToken, limit: int = 50):
    headers = {"Authorization": f"Bearer {token}"}
    messages_url = f"{GRAPH_BASE}/me/mailFolders/{folder_id}/messages?$top={limit}"
    response = requests.get(messages_url, headers={**headers, **USER_AGENT_HEADERS})
    if not response.ok:
        raise Exception(f"Fehler beim Abrufen der Nachrichten: {response.text}")

    messages = response.json().get("value", [])
    target_dir = ensure_maildir_structure(maildir_root, folder_name)

    for msg in messages:
        eml_text = download_mail_as_eml(msg["id"], token)
        fname = f"{uuid.uuid4().hex}.eml"
        with open(target_dir / fname, "w", encoding="utf-8") as f:
            f.write(eml_text)
        print(f"Gespeichert: {folder_name}/{fname}")


def list_mail_folders(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    result = []

    def walk_folder(folder_id: str, path_prefix: str = ""):
        url = f"{GRAPH_BASE}/me/mailFolders/{folder_id}/childFolders?$top=100"
        while url:
            response = requests.get(url, headers={**headers, **USER_AGENT_HEADERS})
            if not response.ok:
                raise Exception(f"Fehler beim Abrufen von childFolders: {response.text}")
            data = response.json()
            for folder in data.get("value", []):
                full_name = f"{path_prefix}/{folder['displayName']}".strip("/")
                result.append((folder["id"], full_name))
                # Rekursion: weitere Unterordner
                walk_folder(folder["id"], full_name)
            url = data.get("@odata.nextLink")

    # Top-Level-Folder holen
    url = f"{GRAPH_BASE}/me/mailFolders?$top=100"
    response = requests.get(url, headers={**headers, **USER_AGENT_HEADERS})
    if not response.ok:
        raise Exception(f"Fehler beim Abrufen der Mailordner: {response.text}")
    for folder in response.json().get("value", []):
        result.append((folder["id"], folder["displayName"]))
        walk_folder(folder["id"], folder["displayName"])

    return result



def fetch_all_messages(folder_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    messages = []
    url = f"{GRAPH_BASE}/me/mailFolders/{folder_id}/messages?$top=50"

    while url:
        response = requests.get(url, headers={**headers, **USER_AGENT_HEADERS})
        if not response.ok:
            raise Exception(f"Fehler beim Paging: {response.text}")
        data = response.json()
        messages.extend(data.get("value", []))
        url = data.get("@odata.nextLink")  # für nächste Seite

    return messages


def get_existing_ids(target_dir: Path) -> set:
    return {
        json.loads(f.read_text()).get("id")
        for f in target_dir.glob("*.json")
    }

def save_mail_with_metadata(target_dir: Path, message_id: str, eml_text: str, metadata: dict):
    fname = f"{message_id}.eml"
    meta_name = f"{message_id}.json"

    with open(target_dir / fname, "w", encoding="utf-8") as f:
        f.write(eml_text)

    with open(target_dir / meta_name, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)



def sync_folder_to_maildir(maildir_root: Path, folder_id: str, folder_name: str, token: str):
    target_dir = ensure_maildir_structure(maildir_root, folder_name)
    existing_ids = get_existing_ids(target_dir)

    print(f"📂 Synchronisiere Ordner: {folder_name}")
    messages = fetch_all_messages(folder_id, token)

    count_new = 0
    for msg in messages:
        msg_id = msg["id"]
        if msg_id in existing_ids:
            continue  # schon da

        try:
            eml_text = download_mail_as_eml(msg_id, token)
            save_mail_with_metadata(target_dir, msg_id, eml_text, msg)
            print(f"✅ Gespeichert: {msg.get('subject', 'kein Betreff')}")
            count_new += 1
        except Exception as e:
            print(f"⚠️ Fehler bei {msg_id}: {e}")

    print(f"🧾 {count_new} neue Mails in '{folder_name}' gespeichert.")



def sync_all_folders(maildir_root: Path, token: str, folder_filter: list[str] = None):
    folders = list_mail_folders(token)
    for folder_id, folder_name in folders:
        if folder_filter and (folder_name not in folder_filter):
            continue
        sync_folder_to_maildir(maildir_root, folder_id, folder_name, token)


def mail(*, access_token: AccessToken):

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Abruf der ersten 10 Mails aus dem Posteingang
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=10",
        headers=headers
    )

    if response.ok:
        messages = response.json().get("value", [])
        for i, msg in enumerate(messages, 1):
            print(f"\n--- Nachricht {i} ---")
            print("Von:", msg.get("from", {}).get("emailAddress", {}).get("address"))
            print("Betreff:", msg.get("subject"))
            print("Erhalten am:", msg.get("receivedDateTime"))
            print("ID:", msg.get("id"))
    else:
        print("Fehler beim Abrufen der Mails:", response.text)
