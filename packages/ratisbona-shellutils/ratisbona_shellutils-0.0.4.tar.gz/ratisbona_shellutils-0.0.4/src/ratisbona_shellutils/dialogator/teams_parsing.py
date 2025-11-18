# Wir verwenden eine HTML-zu-Markdown-Bibliothek für bessere Ergebnisse
import html2text

def generate_markdown_with_html2text(messages):
    markdown_lines = []
    last_date = None
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # keine automatische Zeilenumbrüche

    for dt, _, msg in messages:
        if not dt:
            continue

        date_str = dt.date().isoformat()
        time_str = dt.strftime("%H:%M")

        if last_date != date_str:
            markdown_lines.append(f"# {date_str}")
            markdown_lines.append("")
            last_date = date_str

        user = (msg.get("from") or {}).get("user", {})
        name = user.get("displayName", "UNKNOWN")

        markdown_lines.append(f"## {name}, {time_str}")
        markdown_lines.append("")

        body_html = (msg.get("body") or {}).get("content", "")
        body_md = h.handle(body_html).strip()
        markdown_lines.append(body_md)
        markdown_lines.append("")

    return "\n".join(markdown_lines)

# Neue Markdown-Version generieren
markdown_output2 = generate_markdown_with_html2text(sorted_messages)

# Neue Datei schreiben
output_file2 = Path("/mnt/data/teams_chat_export_fancy.md")
with open(output_file2, "w", encoding="utf-8") as f:
    f.write(markdown_output2)

output_file2.name
