import json
import logging
import os
import http.client as http_client

import msal
import requests
from requests import Response

from ratisbona_utils.io import get_config_dir


# Konfiguration
GRAPH_BASE = "https://graph.microsoft.com/v1.0"
CLIENT_ID = "da25865b-7574-4a38-9032-a2620322afb3"
TENANT_ID = "7a5da5e1-b2bf-41d5-b94a-c687cffa2b02"  # Alternativ "common" bei Multitenant
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = [
    "https://graph.microsoft.com/Chat.Read",
    "https://graph.microsoft.com/Mail.Read",
    "https://graph.microsoft.com/User.Read",
    "https://graph.microsoft.com/ChatMessage.Read",
    "https://graph.microsoft.com/Files.Read",
    "https://graph.microsoft.com/Files.Read.All"
]


AccessToken = str
CACHE_PATH = get_config_dir("ratisbona_messysoft") / "token.cache"

# Logging
def configure_logging():

    # Aktiviere HTTP-Logging
    http_client.HTTPConnection.debuglevel = 1

    # Konfiguriere Logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    # Nur das HTTP-Logging von requests/urllib3
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

#configure_logging()
ratisbona_logger = logging.getLogger("ratisbona.messysoft")
ratisbona_logger.info("Starting up!")


# User-Agent für Requests
USER_AGENT_HEADERS = {
    "User-Agent": "FCKUMS"
}

# Lade oder initialisiere Token-Cache
cache = msal.SerializableTokenCache()

if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        cache.deserialize(f.read())

def save_cache():
    if cache.has_state_changed:
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())

def get_session(custom_user_agent: str = "FCKUMS/1.0"):
    session = requests.Session()
    session.headers.update({"User-Agent": custom_user_agent})
    sessionstats = {"num_requests": 0}


    ratisbona_logger.log(logging.INFO, "Erstelle neue Session mit User-Agent: %s", custom_user_agent)

    def count_requests(response: Response, *args, **kwargs):
        nonlocal sessionstats

        sessionstats["num_requests"] += 1
        print(f"Anfrage #{sessionstats['num_requests']}")
        return response

    session.hooks["response"] = [count_requests]

    ratisbona_logger.log(logging.INFO, "Session erstellt: %s", session)
    ratisbona_logger.log(logging.INFO, "Sessionstats: %s", sessionstats)
    ratisbona_logger.log(logging.INFO, "Hooks: %s", session.hooks)
    return session, sessionstats

def try_extract_token(maybe_contains_token, rejoice: bool = True) -> bool:
    """
    Überprüft, ob ein gültiges Token vorhanden ist.
    Gibt True zurück, wenn ein Token vorhanden ist, sonst False.
    """
    if not maybe_contains_token or "access_token" not in maybe_contains_token:
        return None

    if rejoice:
        print("Zugriffstoken erhalten: " + maybe_contains_token["access_token"][:40] + "…")
        print("Enthaltene Scopes: " + maybe_contains_token.get("scope", ""))
        print("Enthaltene Claims:")
        print(json.dumps(maybe_contains_token.get("id_token_claims", {}), indent=2))

    save_cache()
    return maybe_contains_token["access_token"]

def authenticate(session: requests.Session) -> AccessToken:
    # Public-Client-App (für z. B. CLI)
    app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY, http_client=session, token_cache=cache)

    # Token holen (zuerst still versuchen)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        maybe_token = try_extract_token(result, rejoice=True)
        if maybe_token:
            return maybe_token


    # Interaktive Authentifizierung (öffnet Browser)
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise ValueError("Device flow konnte nicht gestartet werden")
    print("Bitte öffne den folgenden Link in deinem Browser und gib den Code ein:")
    print(flow["verification_uri"])
    print("Code:", flow["user_code"])
    result = app.acquire_token_by_device_flow(flow)
    maybe_token = try_extract_token(result, rejoice=True)
    if not maybe_token:
        raise ValueError("Fehler bei der Authentifizierung", result.get("error_description"))
    return maybe_token