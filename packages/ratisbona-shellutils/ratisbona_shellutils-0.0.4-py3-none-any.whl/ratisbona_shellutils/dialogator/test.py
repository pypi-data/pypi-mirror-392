from markdown_it import MarkdownIt

md = MarkdownIt().enable('table')  # Tabelle aktivieren

markdown_text = """
| Spalte 1 | Spalte 2 | Spalte 3 |
|----------|----------|----------|
| Wert 1   | Wert 2   | Wert 3   |
| A        | B        | C        |
"""

# Parsen und Ausgabe der Token
ast = md.parse(markdown_text)
for token in ast:
    print(token)

# HTML-Ausgabe
html_output = md.render(markdown_text)
print(html_output)
