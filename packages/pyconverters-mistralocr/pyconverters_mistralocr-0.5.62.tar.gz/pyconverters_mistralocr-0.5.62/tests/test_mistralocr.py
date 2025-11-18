from pathlib import Path
from typing import List

import pytest
from pyconverters_mistralocr.md_splitter import ExperimentalMarkdownSyntaxTextSplitter
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile

from pyconverters_mistralocr.mistralocr import MistralOCRConverter, MistralOCRParameters


@pytest.mark.skip(reason="Not a test")
def test_mistralocr_pdf():
    converter = MistralOCRConverter()
    # parameters = MistralOCRParameters(model_str="mistral-document-ai-2505", segment=True)
    parameters = MistralOCRParameters(segment=True)
    testdir = Path(__file__).parent
    source = Path(testdir, "data/AFP Stories_Product Fact Files EN 2025.pdf")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "application/pdf"), parameters
        )
    assert len(docs) == 1
    assert docs[0].identifier == 'AFP Stories_Product Fact Files EN 2025.pdf'
    assert docs[0].title == "AFP Stories"

    json_file = source.with_suffix(".json")
    with json_file.open("w") as fout:
        print(docs[0].json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


@pytest.mark.skip(reason="Not a test")
def test_mistralocr_pdf_no_latex():
    converter = MistralOCRConverter()
    parameters = MistralOCRParameters(segment=True)
    testdir = Path(__file__).parent
    source = Path(testdir, "data/ijms-22-07070-v2.pdf")
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(
            UploadFile(source.name, fin, "application/pdf"), parameters
        )
    assert len(docs) == 1
    assert docs[0].identifier == 'ijms-22-07070-v2.pdf'
    assert "$" not in docs[0].text

    json_file = source.with_suffix(".json")
    with json_file.open("w") as fout:
        print(docs[0].json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


@pytest.mark.skip(reason="Not a test")
def test_mistralocr_dir():
    converter = MistralOCRConverter()
    parameters = MistralOCRParameters(segment=True)
    testdir = Path(__file__).parent
    datadir = Path(testdir, "data")
    for pdf_file in datadir.glob("*.pdf"):
        with pdf_file.open("rb") as fin:
            docs: List[Document] = converter.convert(
                UploadFile(pdf_file.name, fin, "	application/pdf"), parameters
            )
            doc = docs[0]
            # Add additional metadata
            doc.metadata = {'foo': 'bar'}
            json_file = pdf_file.with_suffix(".json")
            with json_file.open("w") as fout:
                print(docs[0].json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def test_md_splitter():
    text = """[^0] [^0]: *Average from January to December 2024

```
Non-binding

```
** Topics = last version articles
** Actualisations = all versions articles
```
# AFP STORIES IN ARABIC

## Coverage
"""
    splitter = ExperimentalMarkdownSyntaxTextSplitter(headers_to_split_on=-1,
                                                      strip_headers=False)
    chunks = splitter.split_text(text)
    ctext = ""
    for chunk in chunks:
        ctext += chunk.text
        cmetas = {k: v for k, v in chunk.metadata.items() if isinstance(k, int)}
        headers = [v for k, v in sorted(cmetas.items())]
        smetadata = {}
        if headers:
            smetadata['Headers'] = ' / '.join(headers)
    assert ctext == text
