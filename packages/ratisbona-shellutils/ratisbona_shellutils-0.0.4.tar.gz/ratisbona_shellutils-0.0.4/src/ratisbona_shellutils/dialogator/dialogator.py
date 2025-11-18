from dataclasses import dataclass, field
from typing import Sequence, Callable
from uuid import UUID, uuid4

from markdown_it import MarkdownIt
from markdown_it.token import Token

from mdit_py_plugins.dollarmath import dollarmath_plugin

from ratisbona_utils.latex import (
    QuotesParser,
    latex_quote,
    replace_emojis,
    open_dialogue_document,
    close_dialogue_document,
)
from ratisbona_utils.strings import shorten, indent


@dataclass(frozen=True)
class Context:
    quotes_parser: QuotesParser = field(default_factory=QuotesParser)
    is_dialogue_open: bool = False
    is_a_verbatim_env_open: bool = False
    is_a_floating_env_open: bool = False
    is_em_open: bool = False
    is_strong_open: bool = False
    indent_level: int = 0
    buffer: str = ""
    buffer1: str = ""
    table_buffer: str = ""
    current_col_number: int = 0
    current_table_max_col_number: int = 0


def _with_changed(context: Context, **kwargs) -> Context:
    as_dict = context.__dict__
    as_dict.update(kwargs)
    return Context(**as_dict)


def _context_with_em_open(context: Context) -> Context:
    return _with_changed(context, is_em_open=True)


def _context_with_em_closed(context: Context) -> Context:
    return _with_changed(context, is_em_open=False)


def _context_with_strong_open(context: Context) -> Context:
    return _with_changed(context, is_strong_open=True)


def _context_with_strong_closed(context: Context) -> Context:
    return _with_changed(context, is_strong_open=False)


def _context_with_another_table(context: Context, document_so_far: str) -> Context:
    if len(context.table_buffer) > 0:
        print("WARNING! New Table started but Tablebuffer not empty!")
        print("Tablebuffer: \n" + indent(shorten(context.table_buffer, 1024), 2))

    return _with_changed(
        context,
        table_buffer=document_so_far,
        current_col_number=0,
        current_table_max_col_number=0,
    )


def _context_with_another_table_col(context: Context) -> Context:
    return _with_changed(context, current_col_number=context.current_col_number + 1)


def _context_with_another_table_row(context: Context) -> Context:
    max_col_num = max(context.current_col_number, context.current_table_max_col_number)
    return _with_changed(
        context, current_col_number=0, current_table_max_col_number=max_col_num
    )


def _context_with_buffer(context: Context, buffer: str) -> Context:
    return _with_changed(context, buffer=buffer)


def _context_with_buffer1(context: Context, buffer1: str) -> Context:
    return _with_changed(context, buffer1=buffer1)


def _context_with_open_floating(context: Context) -> Context:
    return _with_changed(context, is_a_floating_env_open=True)


def _context_with_close_floating(context: Context) -> Context:
    return _with_changed(context, is_a_floating_env_open=False)


def _context_with_open_dialogue(context: Context) -> Context:
    return _with_changed(context, is_dialogue_open=True)


def _context_with_close_dialogue(context: Context) -> Context:
    return _with_changed(context, is_dialogue_open=False)


def _context_with_open_verbatim(context: Context) -> Context:
    return _with_changed(context, is_a_verbatim_env_open=True)


def _context_with_closed_verbatim(context: Context) -> Context:
    return _with_changed(context, is_a_verbatim_env_open=False)


def _context_with_indent_incremented(context) -> Context:
    return _with_changed(context, indent_level=context.indent_level + 1)


def _context_with_indent_decremented(context) -> Context:
    return _with_changed(context, indent_level=context.indent_level - 1)


# ====== Document helper function =======


def _indent(context: Context) -> str:
    return "  " * context.indent_level


def _reset_quotes(context: Context) -> Context:
    context.quotes_parser.reset_quotes()  # Not that immutable after all, right?
    return context  # Hopefully nobody will notice...


def _debug_print_token(token: Token, indent=""):
    token_type = token.type
    token_content = token.content if token.content is not None else "[None]"
    print(
        f"{indent}Token: {token_type}, Content: {shorten(token_content, 40)}, Info: {token.info}"
    )
    for key, value in token.attrs.items():
        print(f"{indent}    Attr: {key} = {value}")
    if token.children is not None and len(token.children) > 0:
        for child in token.children:
            _debug_print_token(child, indent + "  ")


def _maybe_indent(document: str, context: Context) -> str:
    if document.endswith("\n"):
        return document + _indent(context)
    return document


def _ensure_newline(document: str, context: Context) -> str:
    if not document.endswith("\n"):
        return document + "\n"
    return document


def _maybe_supress_empty_paragraph_open(document: str, context: Context) -> str:
    if document.endswith("\n\n"):
        return document[:-1]
    return document


# ====== Token processing state handling =====

_headings = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]
_function_index = {}


def _register(function: Callable):
    _function_index[function.__name__.replace("process_", "")] = function


def _phony(function_name: str):
    _function_index[function_name.replace("process_", "")] = None


def _alias(alias_name: str, function_name: str):
    _function_index[alias_name.replace("process_", "")] = _function_index[
        function_name.replace("process_", "")
    ]


def _ensure_unstable_closed(document: str, context: Context) -> tuple[str, Context]:
    document, context = process_em_close(None, document, context, should_close=False)
    document, context = process_strong_close(
        None, document, context, should_close=False
    )
    return document, context


# ====== Token processing functions ======


_phony("process_inline")


def process_hardbreak(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    return document + "\\leavevmode\\\\", context


_register(process_hardbreak)


def process_html_inline(token: Token, document: str, context: Context):
    return process_code_inline(token, document, context)


_register(process_html_inline)


def process_code_block(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    print("CODE BLOCK?!??")
    _debug_print_token(token)

    _ensure_unstable_closed(document, context)
    return (
        document + f"\\begin{{minted}}{{text}}\n{token.content}\n\\end{{minted}}\n",
        context,
    )


_register(process_code_block)


def process_math_inline(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    return document + f"\\({token.content}\\)", context


_register(process_math_inline)


def process_math_block(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    context = _reset_quotes(context)

    return document + f"\\[\n{token.content.strip()}\n\\]\n", context


_register(process_math_block)


def process_em_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    if context.is_a_floating_env_open:
        return document, context  # do nothing!
    if context.is_em_open:
        print("WARN: Em open already.")
        return document, context  # already open, should not happen.

    context = _context_with_em_open(context)
    return document + "\\textit{", context


_register(process_em_open)


def process_em_close(
    token: Token, document: str, context: Context, should_close=True
) -> tuple[str, Context]:
    if context.is_a_floating_env_open:
        return document, context  # do nothing!
    if not context.is_em_open:
        return (
            document,
            context,
        )  # already closed. That can happen as mintinline uses it!
    if not should_close:
        print("WARNING: Em close due to latex stability issues!")

    context = _context_with_em_closed(context)
    return document + "}", context


_register(process_em_close)


def process_strong_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    if context.is_a_floating_env_open:
        return document, context  # do nothing!
    if context.is_strong_open:
        print("WARN: Strong open already.")
        return document, context
    context = _context_with_strong_open(context)
    return document + "\\textbf{", context


_register(process_strong_open)


def process_strong_close(
    token: Token, document: str, context: Context, should_close=True
) -> tuple[str, Context]:
    if context.is_a_floating_env_open:
        return document, context  # do nothing!
    if not context.is_strong_open:
        return document, context
    if not should_close:
        print("WARNING: Strong close due to latex stability issues!")

    context = _context_with_strong_closed(context)
    return document + "}", context


_register(process_strong_close)


def process_softbreak(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    return document + "\\\n", context


_register(process_softbreak)


def process_hr(token: Token, document: str, context: Context) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _ensure_newline(document, context)
    if context.is_dialogue_open:
        context = _context_with_close_dialogue(context)
        document += _indent(context) + "\\end{dialogue}\n"
    return document, context


_register(process_hr)


def process_ordered_list_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _maybe_indent(document, context)
    return document + "\\begin{enumerate}\n", _context_with_indent_incremented(context)


_register(process_ordered_list_open)


def process_ordered_list_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    context = _context_with_indent_decremented(context)
    document = _maybe_indent(document, context)
    return document + "\\end{enumerate}\n", context


_register(process_ordered_list_close)


def process_list_item_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _maybe_indent(document, context)
    return document + "\\begin{item}\n", _context_with_indent_incremented(context)


_register(process_list_item_open)


def process_list_item_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    context = _context_with_indent_decremented(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    return document + _indent(context) + "\\end{item}\n", context


_register(process_list_item_close)
_phony("process_paragraph_open")


def process_paragraph_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    return document + "\n\n", context


_register(process_paragraph_close)


def process_heading_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    level = int(token.tag[-1])
    document = _maybe_supress_empty_paragraph_open(document, context)

    if level == 2:
        # Speak opened!
        if not context.is_dialogue_open:
            context = _context_with_open_dialogue(context)
            document = _ensure_newline(document, context)
            document += _indent(context) + "\\begin{dialogue}\n"
        document = _ensure_newline(document, context)
        document += _indent(context) + "\\speak{"
        return document, context

    anylevel_closes = True  # Else only maior headings close the dialogue env!

    # Autoclose dialogue, it's a tag we created!
    if context.is_dialogue_open and (anylevel_closes or level == 1):
        context = _context_with_close_dialogue(context)
        document = _ensure_newline(document, context)
        document += "\\end{dialogue}\n"

    # Big gaps between maior headings
    if level == 1:
        document += "\n\n\n\n"  # I like having big gaps between sections

    # Heading level 1 is maior heading,
    # two is handled above as speak line
    # and the other levels are depicted to following tex headding levels.
    # So:
    # Heading level | Latex
    # 1             | \section
    # 2             | \speak
    # 3             | \subsection
    # 4             | \subsubsection
    if level > 2:
        level -= 1

    context = _context_with_open_floating(context)
    document = _ensure_newline(document, context)
    return document + _indent(context) + f"\\{_headings[level-1]}*{{", context


_register(process_heading_open)


def process_heading_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    level = int(token.tag[-1])

    document = _maybe_supress_empty_paragraph_open(document, context)

    if level == 2:
        return document + "} \\leavevmode\\\\\n", context

    context = _context_with_close_floating(context)
    return document + "}\n", context


_register(process_heading_close)


def process_fence(token: Token, document: str, context: Context) -> tuple[str, Context]:
    context = _reset_quotes(context)
    # print("Info: Sourcemap: ", token.map)
    language = token.info.strip()

    if "" == language:
        language = "text"

    if "assembl" in language.lower():
        language = "asm"

    short_out_languages = ["plaintext", "plantuml", "prompt", "udev", "config", "gitignore", ".gitignore"]
    for toxic in short_out_languages:
        if toxic in language.lower():
            language = "text"
            break

    if context.is_dialogue_open:
        document = _ensure_newline(document, context)
        document += _indent(context)
        document += "\\end{dialogue}\n"
        context = _context_with_close_dialogue(context)

    document = _ensure_newline(document, context)
    content = token.content
    while content.endswith("\n"):
        content = content[:-1]

    return (
        document + f"\\begin{{minted}}{{{language}}}\n{content}\n\\end{{minted}}\n",
        context,
    )


_register(process_fence)


def process_code_inline(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    if context.is_a_verbatim_env_open:
        print("INFO: Already verbatim! Just echoing content!")
        return document + token.content, context
    # print("Adding inline code (verbatimly): -->" + shorten(token.content, 40) + "<--")
    document = _maybe_indent(document, context)
    sanitized_token_content = token.content.replace("#", r"\#").replace("$", r"\$")
    return (
        document + f"\\mintinline{{text}}{{{sanitized_token_content}}}",
        context,
    )


_register(process_code_inline)
_alias("process_html_inline", "process_code_inline")


def bullet_list_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    document += _indent(context) + "\\begin{itemize}\n"
    context = _context_with_indent_incremented(context)
    return document, context


_register(bullet_list_open)


def bullet_list_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    context = _context_with_indent_decremented(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    document += _indent(context) + "\\end{itemize}\n"
    return document, context


_register(bullet_list_close)


def process_text(token: Token, document: str, context: Context) -> tuple[str, Context]:
    # mode = "verbatimly" if context.is_a_verbatim_env_open else "normally"
    # print(f"Adding Text [{mode}]: -->" + token.content + "<--")
    if context.is_a_verbatim_env_open:
        return document + token.content, context
    document = _maybe_indent(document, context)
    quotes_corrected = context.quotes_parser.parseline(token.content)
    sanitized_text = latex_quote(quotes_corrected)
    emoji_safe_text = replace_emojis(sanitized_text)
    indented = emoji_safe_text.replace("\n", "\n" + _indent(context))
    return document + indented, context


_register(process_text)


def process_image(token: Token, document: str, context: Context) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    return (
        document + f"\n\\includegraphics[width=\\textwidth]{{{token.attrs['src']}}}\n",
        context,
    )


_register(process_image)


def process_link_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    print("Processing Link Open")
    document, context = _ensure_unstable_closed(document, context)
    document = _maybe_indent(document, context)
    context = _context_with_buffer(context, document)
    context = _context_with_buffer1(context, token.attrs["href"])
    document = ""
    return document, context


_register(process_link_open)


def process_link_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    link_text = document
    old_document = context.buffer
    href = context.buffer1
    print(f"Processing Link Close, link_text: [{link_text}], href: [{href}]")
    cleaned_for_href = latex_quote(href)
    cleaned_for_nolink = cleaned_for_href
    if link_text == "" or href == link_text or cleaned_for_href == link_text:
        link_text = "(link)"

    document = (
        old_document
        + link_text
        + f"\\footnote{{\\href{{{cleaned_for_href}}}{{\\nolinkurl{{{cleaned_for_nolink}}}}}}}"
    )

    return document, context


_register(process_link_close)


# ========== Table processing =========

_phony("process_tbody_open")
_phony("process_tbody_close")


def process_table_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    context = _context_with_another_table(context, document)

    return "", context


_register(process_table_open)


def process_table_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    # Wrap the buffered context in a table now that we know
    # how wide it must be.
    max_col_num = context.current_table_max_col_number
    document_so_far = context.table_buffer
    document_so_far += r"\begin{table}[h]" + "\n"
    document_so_far += r"\centering" + "\n"
    document_so_far += r"\small" + "\n"
    document_so_far += (
        r"\begin{tabu} to \linewidth { " + "|X[m,c]" * max_col_num + "| }\n"
    )
    document_so_far += document
    document_so_far += r"\end{tabu}" + "\n"
    document_so_far += r"\end{table}" + "\n\n"
    context = _with_changed(context, table_buffer="", current_col_number=0)
    return document_so_far, context


_register(process_table_close)


def process_thead_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    document += r"\hline" + "\n"
    return document, context


_register(process_thead_open)
_alias("process_thead_close", "process_thead_open")


def process_tr_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    context = _context_with_another_table_row(context)
    document = _maybe_supress_empty_paragraph_open(document, context)
    document = _ensure_newline(document, context)
    return document, context


_register(process_tr_open)


def process_tr_close(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    return document + "\\\\\\hline \n", context


_register(process_tr_close)


def process_td_open(
    token: Token, document: str, context: Context
) -> tuple[str, Context]:
    context = _reset_quotes(context)
    if context.current_col_number > 0:
        document = document + " & "
    context = _context_with_another_table_col(context)
    return document, context


_register(process_td_open)
_phony("process_td_close")
_alias("process_th_open", "process_td_open")
_alias("process_th_close", "process_td_close")

# ======= MAIN FUNCTIONS ========


def process_ast_with_processors(
    ast: Sequence[Token], _document="", _context=Context(QuotesParser(), False, False)
) -> tuple[str, Context]:
    for token in ast:
        # print("PROCESSOR:  ", end="")
        # _debug_print_token(token)
        func_contained = token.type in _function_index
        if func_contained:
            func = _function_index[token.type]
            if func:
                _document, _context = func(
                    token, _document, _context
                )  # Invoke the processing function, if it's not NOP.
        if token.children:  # Recursively process child tokens
            _document, _context = process_ast_with_processors(
                token.children, _document, _context
            )
        if not func_contained and not token.children:
            print(f"Warning! Unhandled token:")
            _debug_print_token(token)
    return _document, _context


def convert_to_latex(markdown_text: str, title: str):
    md = MarkdownIt().use(dollarmath_plugin).enable("table")
    ast = md.parse(markdown_text)

    document, context = process_ast_with_processors(ast, "", Context())
    if context.is_dialogue_open:
        document = _maybe_supress_empty_paragraph_open(document, context)
        document = _ensure_newline(document, context)
        document += "\\end{dialogue}\n"

    document = open_dialogue_document(title) + document + close_dialogue_document()

    return document


def math_sanitze_markdown_text(markdown_text: str) -> str:
    return (
        markdown_text.replace(r"\[", "\n$$")
        .replace(r"\]", "\n$$")
        .replace(r"\(", r"$")
        .replace(r"\)", r"$")
    )
