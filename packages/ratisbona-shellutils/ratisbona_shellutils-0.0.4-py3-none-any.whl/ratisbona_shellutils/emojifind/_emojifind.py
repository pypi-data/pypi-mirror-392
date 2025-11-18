import emoji
emoji.config.load_language('de')

import json
from ratisbona_utils.io import get_config_dir, get_resource
from ratisbona_utils.functional import ensure_collection


def get_user_emoji_file():
    return get_config_dir("emojifind") / "users.json"

def get_user_dbentries():
    """
    Load the user emoji database entries from the user emoji file.

    :return: A dictionary containing the user emoji database entries.
    """
    user_db = get_user_emoji_file()
    if not user_db.exists():
        return {}

    with user_db.open("r") as f:
        data = json.load(f)

    return data

def get_additional_dbentries():
    with get_resource("ratisbona_shellutils.emojifind.resources", "additional_emojis.json").open("r") as f:
        additional_data = json.load(f)
    return additional_data

def merge_collections(collection1, collection2):
    """
    Merge two collections, ensuring that both are treated as lists.

    :param collection1: The first collection to merge.
    :param collection2: The second collection to merge.

    :return: A merged list containing elements from both collections.
    """
    result = []
    for collection in (collection1, collection2):
        for item in collection:
            if not item in result:
                result.append(item)
    return result


def merge_dbentries(db1, db2):
    """
    Merge two emoji database entries.

    :param db1: The first emoji database entries.
    :param db2: The second emoji database entries.

    :return: A merged dictionary of emoji database entries.
    """
    merged = db1.copy()
    for key, values in db2.items():
        if key in merged:
            # If the key already exists, merge the descriptions
            for lang in ("de", "en"):
                merged[key][lang] = merge_collections(
                    merged[key].get(lang, []),
                    values.get(lang, [])
                )
        else:
            # If the key does not exist, add it
            merged[key] = values
    return merged

def write_dbentries(data):
    """
    Write the given data to the user emoji database file.

    :param data: The data to write to the user emoji database.
    """
    user_db = get_user_emoji_file()
    with user_db.open("w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def search_emojis(keyword, max_results=10):
    """
    Search for emojis based on a keyword in English or German.

    :param keyword: The keyword to search for.
    :param max_results: The maximum number of results to return.

    :return: A list of tuples containing the emoji character, its description in English and German.
    """
    keyword = keyword.lower()
    results = []



    collections = {
        "emoji.EMOJI_DATA": emoji.EMOJI_DATA,
        "additional_data": get_additional_dbentries(),
        "userdb_entries": get_user_dbentries()
    }


    for collection_name, collection in collections.items():
        collection_results = 0
        print(f"Searching in collection {collection_name} with {len(collection)} emojis...", end=" ")
        for name, char in collection.items():
            description = ensure_collection(char.get("en", ""))
            beschreibung = ensure_collection(char.get("de", ""))
            description = list(map(str.lower, description))
            beschreibung = list(map(str.lower, beschreibung))
            search_strings = description + beschreibung + [name.lower()]
            for search_string in search_strings:
                if not keyword in search_string:
                    continue
                results.append((char["en"],char["de"], name))
                collection_results += 1
                if len(results) >= max_results:
                    break
        print(f"Found {collection_results} results...")

    return results
