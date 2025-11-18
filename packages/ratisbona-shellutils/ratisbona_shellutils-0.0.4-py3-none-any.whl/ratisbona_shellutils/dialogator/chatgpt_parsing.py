import json
import re
from datetime import datetime, date
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Iterable, Any

from ratisbona_utils.functional import nth_element, first
from ratisbona_utils.monads import has_keyvalue, Just, Maybe, Nothing
from ratisbona_utils.strings import shorten

ChatTitle = str
ChatGptConversation = dict
ChatGptFileContent = Iterable[ChatGptConversation]
ChatGptMessage = Any


def find_root_messages(message_dict: Dict) -> List[Dict]:
    result = [
        message
        for message in message_dict.values()
        if not has_keyvalue(message, "parent")
    ]
    return result


def get_message_sequence(root_message, message_dict, indent=""):
    maybe_root_message = Just(root_message)
    print(indent + "INFO: Get Message Sequence for: id=", maybe_root_message["id"])
    all_childs = []
    for maybe_child_id in Just(root_message)["children"]:
        maybe_child = Just(message_dict)[maybe_child_id]
        if not maybe_child:
            print(indent + f"Warning! Message {maybe_child_id} could not be found!")
            continue
        print(indent + "INFO: Child found: id=", maybe_child_id)
        all_childs.append(maybe_child)

    sequence = [root_message]
    all_childs.sort(key=message_key_function)

    for idx, child in enumerate(all_childs):
        if idx > 0:
            print(indent + "WARNING: More than one child is unexpected!")
        maybe_child_childs = child.bind(
            get_message_sequence, message_dict, indent + " "
        )
        if maybe_child_childs:
            sequence.extend(maybe_child_childs.unwrap_value())
    return sequence


def detect_date(message) -> Maybe[datetime]:
    maybe_message = Just(message)
    return maybe_message["message"]["create_time"].bind(datetime.fromtimestamp)


def extract_create_time_from_conversation(
    conversation: ChatGptConversation,
) -> Maybe[datetime]:
    return Just(conversation)["create_time"].bind(datetime.fromtimestamp)


def maybe_parse_json(a_string: str) -> Maybe[Dict]:
    try:
        return Just(json.loads(a_string))
    except json.JSONDecodeError as jde:
        print(
            f"Cannot parse {a_string} as JSON: {jde}. Line: {jde.lineno}, Column: {jde.colno} Pos {jde.pos} Text there: ->{a_string[jde.pos-10:jde.pos+10]}<-"
        )
        print(jde.__dict__)
    return Nothing


def try_hard_parsing_json(a_string: str) -> Maybe[Dict]:
    stripped_start = a_string.lstrip()[:10]

    if (
        len(stripped_start) == 0 or stripped_start[0] not in "{["
    ):  # Ok, I don't see how it could be a JSON-String...
        print("INFO: Not a JSON-String: ", shorten(a_string, 80))
        return Nothing

    a_string = a_string.replace(r"\-", r"\\-")

    maybe_parseresult = maybe_parse_json(a_string)
    if maybe_parseresult:
        return maybe_parseresult

    manipulated_string = a_string.replace("\\\\", "\\")
    maybe_parseresult = maybe_parse_json(manipulated_string)
    if maybe_parseresult:
        return maybe_parseresult

    print("WARNING: Looks like json but it seems it isnt: ", shorten(a_string, 80))

    return Nothing


def handle_string_message(part: str):
    """
        Extracts the text from a string message part of a message, makes sure
        sensible, markdown/latex-conforming paragraph-ends are generated.

        Args:
            part: The string content of the message part.
        Returns:
            str: The markdown rendered text, or empty string, if the content is empty.
    """
    content = part.replace("\\n", "\n")
    if len(content.strip()) > 0:
        if not content.endswith("\n"):
            content += "\n"
        return content
    return ""


def maybe_code_message(json_partcontent: Dict) -> Maybe[str]:
    maybe_partcontent = Just(json_partcontent)
    maybe_language = (
        maybe_partcontent["type"].bind(str.split, "/", 1).bind(nth_element(1))
    )
    maybe_content = maybe_partcontent["content"].bind(str.replace, "```", "''")
    return maybe_language.bind(
        lambda language, content: Just(f"```{language}\n{content}\n```\n"),
        maybe_content,
    )


def maybe_update_message(json_partcontent: Dict) -> Maybe[str]:
    maybe_partcontent = Just(json_partcontent)
    maybe_updates = maybe_partcontent["updates"]

    result = ""
    for maybe_update in maybe_updates:
        maybe_pattern = maybe_update["pattern"]
        maybe_replacement = maybe_update["replacement"]
        if not maybe_pattern or not maybe_replacement:
            print("WARNING! Incomprehensible Update: ", maybe_update)
            result += f"#Warning incomprehensible update!\n```\n{maybe_update}\n```"
        result += maybe_pattern.bind(
            lambda p, r: f"**Update**\nPattern: `{p}`\n```{r}\n```\n", ""
        ).default_or_throw("")
    return Just(result)


def maybe_textid_message(json_partcontent: Dict) -> Maybe[str]:
    maybe_partcontent = Just(json_partcontent)

    if not maybe_partcontent["textdoc_id"]:
        return Nothing

    return "***Textdoc_ID***:\n\n" + maybe_partcontent["result"]


def handle_json_str_message(json_partcontent: Maybe[Dict]):
    """
    Handles a JSON string message part in a message.

    Currently three types of messages are supported:
    - Code messages: {"type": "code/xyz", "content": "..."}
    - Text-ID messages: {"textdoc_id": "...", "result": "..."}
    - Update messages: {"updates": [{"pattern": "...", "replacement": "..."}]}

    Args:
        json_partcontent: The JSON content of the message part or Nothing.
    Returns:
        str: The markdown rendered content, or empty string, if the content type is not recognized.
    """

    maybe_result = (
        json_partcontent.bind(maybe_code_message)
        or json_partcontent.bind(maybe_textid_message)
        or json_partcontent.bind(maybe_update_message)
    )

    if not maybe_result:
        print("ERROR! Unhandled JSON-Content: ", json_partcontent)

    return maybe_result


def handle_text_message_parts(maybe_parts: Maybe[List[str]]) -> str:
    """
    Handles text message parts in a message.

    Args:
        maybe_parts: The parts of the message or Nothing.

    Returns:
        str: The markdown rendered text, or empty string, if no parts are present.
    """
    result = ""
    for maybe_part in maybe_parts:
        maybe_understood = maybe_part.bind(try_hard_parsing_json).bind(
            handle_json_str_message
        ) or maybe_part.bind(handle_string_message)
        if not maybe_understood:
            print(f"WARNING! Unhandled text message part: {maybe_part}")
        else:
            result += maybe_understood.unwrap_value()
    return result


def search_dir(dir: Path, pointer: str) -> Maybe[Path]:
    """
    Search for a file in a directory fitting an (sanitized, remove protocol and file- prefix) assess-pointer.
    Prefers everything over webp.

    Args:
        dir: The directory to search in.
        pointer: The pointer to search for.
    Returns:
        Maybe[Path]: The found file or Nothing.
    """
    if not dir.exists():
        return Nothing

    found_file = Nothing
    for file in dir.iterdir():
        # print(f"Searching for {pointer} in {file}")
        if pointer in file.name:
            if file.suffix.lower() in [".webp", ".dat"]:
                found_file = Just(file)
            else:
                # print(f"Found file {file} that is not a webp or dat file.")
                return Just(file)
    # print(f"Found file {found_file} that is a webp or dat file.")
    return found_file


def find_file_from_pointer(pointer: str) -> Maybe[Path]:
    """
    Finds a file from a given pointer by searching in predefined directories.
    The pointer format seems to have changed several times, because of which we
    try to sanitize it a bit before searching by removing prefixes like:
    "file-service:", "file-", "file_", "sediment://"

    The search is done in the "dalle-generations" as well as in the current directory.

    Args:
        pointer: The pointer to search for.
    Returns:
        Maybe[Path]: The found file or Nothing.
    """
    # search in dalle-generations
    dalle_generations = Path("dalle-generations")

    # Remove prefixes from pointer
    remove_words = ["file-service", ":", "/", "file-", "file_", "sediment"]
    while True:
        did_something = False
        for word in remove_words:
            if pointer.startswith(word):
                pointer = pointer.removeprefix(word)
                did_something = True
        if not did_something:
            break

    # Try tp find it...
    result = search_dir(dalle_generations, pointer) or search_dir(Path("."), pointer)

    # Ok, maby in a directory that is called something like "user?"
    possible_paths = [x for x in Path(".").glob("user*") if x.is_dir()]
    for path in possible_paths:
        result = result or search_dir(path, pointer)

    print(f"Searching for file-pointer {pointer} resulted in {result}")
    return result


def handle_multimodal_message_parts(maybe_parts: Maybe[List[str]]) -> str:
    """
    Handles multimodal message parts in a message.

    For example:

    ```
        "29562c5b-7bb3-47ac-8629-a668964d4f25": {
      "id": "29562c5b-7bb3-47ac-8629-a668964d4f25",
      "message": {
        "id": "29562c5b-7bb3-47ac-8629-a668964d4f25",
        "author": {
          "role": "tool",
          "name": "t2uay3k.sj1i4kz",
          "metadata": {}
        },
        "create_time": 1755522325.3033564,
        "update_time": null,
        "content": {
          "content_type": "multimodal_text",
          "parts": [
            {
              "content_type": "image_asset_pointer",
              "asset_pointer": "sediment://file_000000006b486246972d7e560640829e",
              "size_bytes": 3651278,
              "width": 1536,
              "height": 1024,
              "fovea": null,
              "metadata": {
                "dalle": {
                  "gen_id": "bc05c8d8-a8d3-4ba0-b097-58c1b86d4e93",
                  "prompt": "",
                  "seed": null,
                  "parent_gen_id": null,
                  "edit_op": null,
                  "serialization_title": "DALL-E generation metadata"
                },
                "gizmo": null,
                "generation": {
                  "gen_id": "bc05c8d8-a8d3-4ba0-b097-58c1b86d4e93",
                  "gen_size": "xlimage",
                  "seed": null,
                  "parent_gen_id": null,
                  "height": 1024,
                  "width": 1536,
                  "transparent_background": false,
                  "serialization_title": "Image Generation metadata"
                },
                "container_pixel_height": 1024,
                "container_pixel_width": 1536,
                "emu_omit_glimpse_image": null,
                "emu_patches_override": null,
                "lpe_keep_patch_ijhw": null,
                "sanitized": false,
                "asset_pointer_link": null,
                "watermarked_asset_pointer": null
              }
            }
          ]
        },
    ```

    """
    result = ""
    for maybe_part in maybe_parts:

        # Handle asset-pointers.
        if maybe_part["content_type"] == "image_asset_pointer":
            maybe_file = (
                maybe_part["asset_pointer"]
                .bind(find_file_from_pointer)
                .maybe_warn("Could not find file!")
            )
            if maybe_file:
                file = maybe_file.unwrap_value()
                result += f"![{file.name}]({file})\n"
            continue

        print(f"WARNING! Unhandled multimodal_message_part: {maybe_part}")

    return result


def handle_thoughts(maybe_thoughts: Maybe) -> str:
    """
    Handles thoughts in a message.

    For example the metadata might contain:
    ```
    "3fbd1f9e-8833-48e0-984d-9ea868d167f7": {
      "id": "3fbd1f9e-8833-48e0-984d-9ea868d167f7",
      "message": {
        "id": "3fbd1f9e-8833-48e0-984d-9ea868d167f7",
        "author": {
          "role": "assistant",
          "name": null,
          "metadata": {}
        },
        "create_time": 1757860085.952565,
        "update_time": null,
        "content": {
          "content_type": "thoughts",
          "thoughts": [
            {
              "summary": "\u00dcberlegungen zur Code-Struktur",
              "content": "Wir m\u00fcssen ein komplettes Repo-Skelett bereitstellen: Dockerfile, run.sh, README und eventuell .dockerignore sowie Anweisungen. Da es sich um Setup-Code handelt, ist kein Web-Browsen notwendig. Der Benutzer ist Deutschsprachig, also werden wir Code-Bl\u00f6cke verwenden. Eine Canvas f\u00fcr die Dateien vom Projekt ist eine gute L\u00f6sung.",
              "chunks": [],
              "finished": true
            }
          ],
          "source_analysis_msg_id": "462d52bb-8cca-48d4-a633-69f0e538672a"
        },
        "status": "finished_successfully",
        "end_turn": false,
        "weight": 1.0,
        "metadata": {
    ```
    Args:
        maybe_thoughts: The thoughts in the content of a message or Nothing.
    Returns:
        str: The markdown rendered thoughts, or empty string, if no thoughts are present.
    """
    result = ""
    for maybe_thought in maybe_thoughts:
        maybe_summary: Maybe[str] = maybe_thought["summary"]
        if maybe_summary:
            result += f"***Thought***: {maybe_summary.unwrap_value()}\n\n"

        maybe_content: Maybe[str] = maybe_thought["content"]
        if maybe_content:
            result += f"{maybe_content.unwrap_value()}\n\n"
    return result


def render_url(linktext: str, url: str) -> str:
    """
    Renders a URL in markdown format.
    Args:
        linktext: The text to display for the link.
        url: The URL to link to.
    Returns:
        str: The rendered URL in markdown format: `[linktext](url)`.
    """
    return f"[{linktext}]({url})"


def handle_search_results(maybe_metadata) -> str:
    """
    Handles search results in the metadata of a message.

    For example the metadata might contain:
    ```
        "search_result_groups": [
            {
              "type": "search_result_group",
              "domain": "amazon.com",
              "entries": [
                {
                  "type": "search_result",
                  "url": "https://www.amazon.com/Myth-2-Soulblighter-Linux-PC/dp/B00003OPE7?utm_source=chatgpt.com",
                  "title": "Myth 2: Soulblighter (Linux) : Video Games",
                  "snippet": "Bungie's thrilling strategy adventure, Myth 2: Soulblighter, brings back the scourge of the West and challenges you with all-new scenarios and improved ...",
                  "ref_id": {
                    "turn_index": 0,
                    "ref_type": "search",
                    "ref_index": 1
                  },
                  "pub_date": null,
                  "attribution": "amazon.com"
                }
              ]
            },
            {
              "type": "search_result_group",
              "domain": "projectmagma.net",
              "entries": [
                {
                  "type": "search_result",
                  "url": "https://projectmagma.net/downloads/myth2_183/?utm_source=chatgpt.com",
                  "title": "Project Magma :: Myth II v1.8.3 Update",
                  "snippet": "This release is an incremental update, bringing new OS compatibility, additional polishing and bugfixing, plus a few great new features.",
                  "ref_id": {
                    "turn_index": 0,
                    "ref_type": "search",
                    "ref_index": 4
                  },
                  "pub_date": null,
                  "attribution": "projectmagma.net"
                },
        ```

    Args:
        maybe_metadata: The metadata of a message or Nothing.

    Returns:
        str: The rendered search results, or empty string, if no search results are present.
    """
    result = ""

    for maybe_group in maybe_metadata["search_result_groups"]:
        for maybe_entry in maybe_group["entries"]:
            maybe_type = maybe_entry["type"]
            maybe_url = maybe_entry["url"]
            maybe_title = maybe_entry["title"]
            maybe_snippet = maybe_entry["snippet"]
            if maybe_type:
                result += f'***{maybe_type.unwrap_value().replace("_", " ")}:***'
            if maybe_url:
                url = maybe_url.unwrap_value()
                linktext = maybe_title.default_or_throw("(link)")
                result += render_url(linktext, url) + "\n\n"
            if maybe_snippet:
                result += f"{maybe_snippet.unwrap_value()}\n\n"

    return result


def handle_content_references(
    maybe_content_references: Maybe, result_so_far: str
) -> str:
    """
    Extracts the content-references from the metadata of a message and reviews the Text based on that.


    For example the metadata might contain:
    ```
            "metadata": {
          "content_references": [
            {
              "matched_text": "\ue200cite\ue202turn2view0\ue202turn4view3\ue201",
              "start_idx": 397,
              "end_idx": 425,
              "safe_urls": [
                "https://projectmagma.net/downloads/myth2_updates/",
                "https://projectmagma.net/downloads/myth2_updates/1.8.5%20Final%20%28Build%20471b%29/Readme_1.8.5.pdf"
              ],
              "refs": [],
              "alt": "([projectmagma.net](https://projectmagma.net/downloads/myth2_updates/))",
              "prompt_text": null,
              "type": "grouped_webpages",
              "items": [
                {
                  "title": "Project Magma :: Downloads :: Myth II Updates",
                  "url": "https://projectmagma.net/downloads/myth2_updates/",
                  "pub_date": null,
                  "snippet": null,
                  "attribution_segments": null,
                  "supporting_websites": [
                    {
                      "title": "Myth II Readme",
                      "url": "https://projectmagma.net/downloads/myth2_updates/1.8.5%20Final%20%28Build%20471b%29/Readme_1.8.5.pdf",
                      "pub_date": null,
                      "snippet": null,
                      "attribution": "projectmagma.net"
                    }
                  ],
                  "refs": [
                    {
                      "turn_index": 2,
                      "ref_type": "view",
                      "ref_index": 0
                    },
                    {
                      "turn_index": 4,
                      "ref_type": "view",
                      "ref_index": 3
                    }
                  ],
                  "hue": null,
                  "attributions": null,
                  "attribution": "projectmagma.net"
                }
              ],
              "fallback_items": null,
              "status": "done",
              "error": null,
              "style": null
            },

    ```
     Args:
        maybe_content_references: The content references in the metadata of a message or Nothing.
        result_so_far: The result so far, to which the content references will be appended.
    Returns:
        str: The markdown rendered content references, or the original result if no content references are present.

    """
    for content_reference in maybe_content_references:
        maybe_matched_text = content_reference["matched_text"]
        if not maybe_matched_text:
            continue
        matched_text = maybe_matched_text.unwrap_value()
        if len(matched_text.strip()) == 0:
            continue

        replacement = ""
        for item in content_reference["items"]:
            maybe_url = item["url"]
            maybe_title = item["title"]
            if maybe_matched_text and maybe_url:
                url = maybe_url.unwrap_value()
                linktext = maybe_title.default_or_throw("(link)")
                rendered_url = render_url(linktext, url)
                replacement += f"(vgl. {rendered_url})"
        print(
            f"INFO: Replacing matched_text {shorten(matched_text,80)} with {replacement}"
        )
        result_so_far = result_so_far.replace(matched_text, replacement)
    return result_so_far

CodeMessageJsonContent = Dict[str, Any]

def handle_code_message_content_type(code_message_json_content: CodeMessageJsonContent, context: dict) -> Maybe[str]:
    maybe_code_message_json_content = Just(code_message_json_content)

    print("Searching for code content...")
    result = ""
    maybe_document_name = maybe_code_message_json_content["name"]
    if maybe_document_name:
        print("Found name!")
        document_name = maybe_document_name.unwrap_value()
        result += f"### File: {document_name}\n\n"

    maybe_document_content = maybe_code_message_json_content["content"]
    if not maybe_document_content:
        print("WARNING! No content in code message content: ", shorten(json.dumps(code_message_json_content), 80))
        return Nothing

    print("Found code message json type!: ", shorten(json.dumps(code_message_json_content), 80))
    result += maybe_document_content.unwrap_value()
    context["pending_document"] = result
    print("Writing result to the document: ", shorten(result, 80))
    return Just(result)

def handle_code_message_content_update(code_message_json_content: CodeMessageJsonContent, context: dict) -> Maybe[str]:
    """
    ```
        "cf21dfdc-66f9-42e7-9f33-97da65e349f3": {
      "id": "cf21dfdc-66f9-42e7-9f33-97da65e349f3",
      "message": {
        "id": "cf21dfdc-66f9-42e7-9f33-97da65e349f3",
        "author": {
          "role": "assistant",
          "name": null,
          "metadata": {}
        },
        "create_time": 1757873017.882611,
        "update_time": null,
        "content": {
          "content_type": "code",
          "language": "json",
          "response_format_name": null,
          "text": "{\"updates\":[{\"pattern\":\"## Dockerfile[\\\\s\\\\S]*?```\",\"multiple\":false,\"replacement\":\"## Dockerfile\\n\\n```d
    ```
    """
    if "pending_document" not in context:
        print("WARNING! No pending document to apply update to: ", shorten(json.dumps(code_message_json_content), 80))
        return Nothing

    result = ""
    for maybe_update in Just(code_message_json_content)["updates"]:
        maybe_pattern = maybe_update["pattern"]
        maybe_replacement = maybe_update["replacement"]
        if not maybe_pattern or not maybe_replacement:
            print("WARNING! Incomprehensible Update: ", maybe_update)
            continue

        pattern = maybe_pattern.unwrap_value()
        replacement = maybe_replacement.unwrap_value()
        pending_document = context["pending_document"]
        pending_document = re.compile(pattern).sub(replacement, pending_document)
        context["pending_document"] = pending_document
        result += f"**Update applied**  Pattern: `{shorten(pattern, 60)}`\n\n"
    result += context["pending_document"]
    return Just(result)


def handle_code_message(content_text: str, context: dict ) -> Maybe[str]:
    maybe_code_content = try_hard_parsing_json(content_text)
    if not maybe_code_content:
        print("WARNING! Could not parse code message content: ", shorten(content_text, 80))
        return Nothing

    maybe_result = (
        maybe_code_content.bind(handle_code_message_content_type, context)
        or maybe_code_content.bind(handle_code_message_content_update, context)
    )

    return maybe_result


def translate_message(message: ChatGptMessage, context: dict) -> str:
    maybe_message = Just(message)
    print("INFO: Translate Message:" + maybe_message["id"])
    maybe_inner = maybe_message["message"]
    author = maybe_inner["author"]["role"].default_or_throw("?")
    maybe_content_type = maybe_inner["content"]["content_type"]
    print("INFO: Content-Type: " + maybe_content_type)
    maybe_parts = maybe_inner["content"]["parts"]

    if maybe_content_type == "text":
        result = handle_text_message_parts(maybe_parts)
    elif maybe_content_type == "thoughts":
        result = handle_thoughts(maybe_inner["content"]["thoughts"])
    elif maybe_content_type == "multimodal_text":
        result = handle_multimodal_message_parts(maybe_parts)
    elif maybe_content_type == "code":
        maybe_code_content = maybe_inner["content"]["text"].bind(handle_code_message, context)
        result = maybe_code_content.default_or_throw("")
    else:
        print("WARNING: Unknown Content-Type: " + maybe_content_type)
        result = ""

    maybe_metadata = maybe_inner["metadata"]
    result = handle_content_references(maybe_metadata["content_references"], result)
    result += handle_search_results(maybe_metadata)

    if result:
        result = f"## {author}\n\n" + result
    return result


def message_key_function(message):
    maybe_date = detect_date(message)
    if not maybe_date:
        print(
            f"WARNING: Message-Key-Function: Could not extract date from message:"
            + shorten(str(message), 80)
        )
    return maybe_date.default_or_throw(datetime.min)


def debug_print_message(message):
    the_id_or_replacement = Just(message)["id"].default_or_throw("No ID")
    message_date = (
        Just(message)
        .bind(detect_date)
        .bind(datetime.isoformat)
        .default_or_throw("No Date")
    )
    message_content = (
        Just(message)["message"]["content"]
        .bind(str)
        .bind(shorten, 80)
        .default_or_throw("No Content")
    )
    children = (
        "children"
        if Just(message)["children"].bind(len).default_or_throw(0) > 0
        else "no children"
    )
    print(
        f"Root-Message id: {the_id_or_replacement} Date: {message_date} {children} "
        f"Content: ->{message_content}<-"
    )


def maybe_extract_title(conversation: ChatGptConversation) -> Maybe[str]:
    return Just(conversation)["title"]


def filter_conversations(
    conversations: ChatGptFileContent,
    title_filter: str = "*",
    date_filter_after: datetime = None,
    date_filter_before: datetime = None,
) -> list[tuple[ChatTitle, date, ChatGptConversation]]:

    output_conversations = []

    for conversation in conversations:
        title = maybe_extract_title(conversation).default_or_throw("No Title found")

        the_date = (
            extract_create_time_from_conversation(conversation)
            .bind(datetime.date)
            .default_or_throw(date.min)
        )

        if (
            (title_filter is None or fnmatch(title.lower(), title_filter.lower()))
            and (date_filter_after is None or the_date >= date_filter_after.date())
            and (date_filter_before is None or the_date <= date_filter_before.date())
        ):
            output_conversations.append((title, the_date, conversation))

    output_conversations.sort(key=nth_element(1))
    return output_conversations


def translate_conversation(conversation) -> tuple[str, str, Maybe[date]]:
    maybe_conversation = Just(conversation)

    title = maybe_conversation["title"].default_or_throw("No Title found")
    maybe_messages = maybe_conversation["mapping"]
    maybe_root_msgs = maybe_messages.bind(find_root_messages)
    maybe_root_msgs = maybe_root_msgs.bind(sorted, key=message_key_function)

    num_root_msgs = maybe_root_msgs.bind(len).default_or_throw(0)

    if num_root_msgs == 0:
        print("WARNING: No Root-message found")
    if num_root_msgs > 1:
        print("WARNING: More than one Root-message found")
        for maybe_root_msg in maybe_root_msgs:
            maybe_root_msg.bind(debug_print_message)
        print()

    result = ""
    last_date = Nothing
    first_date = Nothing
    context = {}
    for maybe_root_msg in maybe_root_msgs:
        print(
            "INFO: Translate Conversation: Tackling first rootmessage: id="
            + maybe_root_msg["id"]
            + " keys:"
            + maybe_root_msg.bind(dict.keys)
        )

        maybe_message_sequence = maybe_root_msg.bind(
            get_message_sequence, maybe_messages
        )

        for maybe_message in maybe_message_sequence:
            new_date = maybe_message.bind(detect_date).bind(datetime.date)
            first_date = first_date or new_date

            if new_date and new_date != last_date:
                result += (
                    f"# {new_date.bind(date.isoformat).default_or_throw('??')}\n\n"
                )
                last_date = new_date
            partresult = translate_message(maybe_message, context)
            result += partresult

    return title, result, first_date
