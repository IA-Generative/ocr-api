from odf.opendocument import load
from odf.text import P
from odf import teletype
import re


class TemplatingFieldExtraction:
    def __init__(
        self,
        placeholder_pattern: str = r"{{(.*?)}}",
        accepted_placeholder_pattern: str = r"^[a-zA-Z0-9_]+$",
    ):
        self.placeholder_pattern = placeholder_pattern
        self.accepted_placeholder_pattern = accepted_placeholder_pattern

    def process(self, file_path: str) -> tuple[list[str], list[str]]:
        doc = load(file_path)
        paragraphs = doc.getElementsByType(P)
        extracted_fields = []
        invalid_fields = []
        for p in paragraphs:
            text = teletype.extractText(p)
            matches = re.findall(self.placeholder_pattern, text)
            for match in matches:
                if re.match(self.accepted_placeholder_pattern, match):
                    extracted_fields.append(match)
                else:
                    invalid_fields.append(match)

        return extracted_fields, invalid_fields
