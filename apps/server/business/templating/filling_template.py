import io
import re
import zipfile


class FillingTemplate:
    def __init__(
        self,
        placeholder_pattern: str = r"\[\[(.*?)\]\]",
        accepted_placeholder_pattern: str = r"^[a-zA-Z0-9_]+$",
    ):
        self.placeholder_pattern = placeholder_pattern
        self.accepted_placeholder_pattern = accepted_placeholder_pattern

    def process(
        self,
        file_path: str,
        replacements: dict[str, str],
        output_path: str = "filled_template.odt",
    ) -> str:

        buf = io.BytesIO()
        with zipfile.ZipFile(file_path, "r") as zin:
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    data = zin.read(item.filename)
                    if item.filename == "content.xml":
                        content = data.decode("utf-8")
                        content = self._replace_placeholders(content, replacements)
                        data = content.encode("utf-8")
                    zout.writestr(item, data)

        with open(output_path, "wb") as f:
            f.write(buf.getvalue())

        return output_path

    def _replace_placeholders(self, content: str, replacements: dict[str, str]) -> str:
        tag = r"(?:<[^>]*>)*"
        for name, value in replacements.items():
            escaped = re.escape(name)
            # [[name]] — preferred format, robust against XML splits
            content = re.sub(
                r"\[" + tag + r"\[" + tag + escaped + tag + r"\]" + tag + r"\]",
                value,
                content,
            )
            # {{name}} — alternate format
            content = re.sub(
                r"\{" + tag + r"\{" + tag + escaped + tag + r"\}" + tag + r"\}",
                value,
                content,
            )
            # ${name} — py3o format, may be split as $ | {name}
            content = re.sub(r"\$" + tag + r"\{" + escaped + r"\}", value, content)
        return content
