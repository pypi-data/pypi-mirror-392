# langchain-pymupdf-layout

An integration package connecting **PyMuPDF Layout** to **LangChain**.

Load PDF content to Markdown using AI-based, CPU only, layout analysis.

[![LangChain](https://img.shields.io/badge/LangChain-v1.0+-blue)](https://github.com/langchain-ai/langchain)
[![Python version](https://img.shields.io/badge/python-3.11+-blue)](https://pypi.org/project/pymupdf-layout/)
[![License PolyForm Noncommercial](https://img.shields.io/badge/license-Polyform_Noncommercial-purple)](https://polyformproject.org/licenses/noncommercial/1.0.0/)

## Features

- 📚 Structured data extraction from your documents
- 🧐 Advanced document page layout understanding, including semantic markup for titles, headings, headers, footers, tables, images and text styling
- 🔍 Detect and isolate header and footer patterns on each page

For more detailed information visit the [official PyMuPDF Layout documentation webpage](https://pymupdf.readthedocs.io/en/latest/pymupdf-layout/index.html).

## Requirements

- Python 3.11 or higher
- LangChain Core v1.0.0 or higher
- PyMuPDF v0.26.6 or higher
- PyMuPDF4LLM v0.2.0 or higher
- PyMuPDF Layout c0.26.6 or higher

## Installation

Install the package using pip to start using the Document Loader:

```bash
pip install -U langchain-pymupdf-layout

```

## Usage

You can easily integrate and use the PyMuPDF Layout Loader in your Python application for loading and parsing PDFs. 

Below is an example of how to set up and utilize this loader:

```python
from langchain_pymupdf_layout import version

print(version())  # Output: version number

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_pymupdf_layout import PyMuPDFLayoutLoader

loader = PyMuPDFLayoutLoader(
    file_path="https://www.adobe.com/support/products/enterprise/knowledgecenter/media/c4611_sample_explain.pdf",
    show_progress=False,  
    # See other loader options on https://pymupdf.readthedocs.io/en/latest/pymupdf-layout/index.html#pymupdf-layout-and-parameter-caveats
)

documents = loader.load()

# Chunk
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)

print(f"Loaded {len(documents)} document(s)")
print(f"Created {len(chunks)} chunk(s)")

content = chunks[0].page_content
print(f"\ncontent:\n{content}")

```
