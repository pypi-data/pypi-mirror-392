import difflib
from pathlib import Path
from unittest import TestCase

from ratisbona_shellutils.dialogator.dialogator import math_sanitze_markdown_text, convert_to_latex


class TestDialogator(TestCase):

    def dialogatortest(self, filename: str, overwrite_mode=False):
        infile = Path(__file__).parent / "dialogator_resources" / f"{filename}.md"
        outfile = Path(__file__).parent / "dialogator_resources" / f"{filename}.tex"

        markdown_text = infile.read_text()
        markdown_text = math_sanitze_markdown_text(markdown_text)

        latex_document = convert_to_latex(markdown_text, "test gpt")

        if overwrite_mode:
            outfile.write_text(latex_document)
            return

        expected_text = outfile.read_text()
        the_diff = '\n'.join(difflib.ndiff(expected_text.splitlines(), latex_document.splitlines()))
        self.assertEqual(expected_text, latex_document, the_diff)


    def test_dialogator_must_typeset_gpt_parser_question_containing_a_table(self):
       self.dialogatortest("gpt_regularity")


    def test_dialogator_must_typeset_gpt_dos_memory_question_containing_math(self):
        self.dialogatortest("2024-07-19_-_memory_addressing_in_dos")


    def test_dialogator_must_typeset_indiana_document_with_lots_of_tables(self):
        self.dialogatortest("2024-10-21_-_indiana_jones_filme_übersicht")
