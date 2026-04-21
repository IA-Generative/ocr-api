from pathlib import Path
from odf.opendocument import load
from odf.text import P
from business.templating.filling_template import FillingTemplate


TEMPLATE_PATH = "tests/data/valid/file-sample_100kB-valid-to-fill.odt"


def test_templating_field_extraction_empty(tmp_path: Path):
    output_path = str(tmp_path / "filled_template.odt")

    filler = FillingTemplate()
    result = filler.process(TEMPLATE_PATH, {}, output_path=output_path)

    assert result == output_path
    assert Path(output_path).exists(), "Le fichier de sortie n'a pas été créé"
    assert Path(output_path).stat().st_size > 0, "Le fichier de sortie est vide"


def test_templating_field_extraction_valid(tmp_path: Path):
    output_path = str(tmp_path / "filled_template.odt")

    filler = FillingTemplate()
    result = filler.process(
        TEMPLATE_PATH,
        {
            "value_placeholder1": "Value 1",
        },
        output_path=output_path,
    )

    assert result == output_path
    assert Path(output_path).exists(), "Le fichier de sortie n'a pas été créé"
    assert Path(output_path).stat().st_size > 0, "Le fichier de sortie est vide"

    doc = load(output_path)
    full_text = " ".join(str(p) for p in doc.getElementsByType(P))
    print(f"\n=== Contenu du document (valid) ===\n{full_text}\n===================================")
    assert "Value 1" in full_text, f"'Value 1' absent du document généré. Contenu : {full_text[:500]}"
