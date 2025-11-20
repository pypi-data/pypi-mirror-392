"""Contains PyMuPDF4LLM parser class to parse blobs from PDFs."""

import logging
import threading

try:
    import pymupdf.layout 
except ImportError:
    raise ImportError(
        "pymupdf.layout package not found, please install it "
        "with `pip install pymupdf-layout`"
    )

from datetime import datetime

from typing import (
    Any,
    Iterator,
    Optional,
)

from langchain_core.documents import Document
from langchain_core.document_loaders import (
    Blob,
    BaseBlobParser
)

_STD_METADATA_KEYS = {"source", "total_pages", "creationdate", "creator", "producer"}

logger = logging.getLogger(__name__)

def _validate_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Validate that the metadata has all the standard keys and the page is an integer.

    The standard keys are:
    - source
    - total_page
    - creationdate
    - creator
    - producer

    Validate that page is an integer if it is present.
    """
    if not _STD_METADATA_KEYS.issubset(metadata.keys()):
        raise ValueError("The PDF parser must valorize the standard metadata.")
    if not isinstance(metadata.get("page", 0), int):
        raise ValueError("The PDF metadata page must be a integer.")
    return metadata


def _purge_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Purge metadata from unwanted keys and normalize key names.

    Args:
        metadata: The original metadata dictionary.

    Returns:
        The cleaned and normalized the key format of metadata dictionary.
    """
    new_metadata: dict[str, Any] = {}
    map_key = {
        "page_count": "total_pages",
        "file_path": "source",
    }
    for k, v in metadata.items():
        if type(v) not in [str, int]:
            v = str(v)
        if k.startswith("/"):
            k = k[1:]
        k = k.lower()
        if k in ["creationdate", "moddate"]:
            try:
                new_metadata[k] = datetime.strptime(
                    v.replace("'", ""), "D:%Y%m%d%H%M%S%z"
                ).isoformat("T")
            except ValueError:
                new_metadata[k] = v
        elif k in map_key:
            # Normalize key with others PDF parser
            new_metadata[map_key[k]] = v
            new_metadata[k] = v
        elif isinstance(v, str):
            new_metadata[k] = v.strip()
        elif isinstance(v, int):
            new_metadata[k] = v
    return new_metadata


class PyMuPDFLayoutParser(BaseBlobParser):
    """Parse a blob from a PDF using `PyMuPDF4LLM` library with `PyMuPDF Layout` imported.

    Examples:
        Setup:

        .. code-block:: bash

            pip install -U langchain-pymupdf-layout

        Load a blob from a PDF file:

        .. code-block:: python

            from langchain_core.documents.base import Blob

            blob = Blob.from_path("./test.pdf")

        Instantiate the parser:

        .. code-block:: python

            from langchain_pymupdf_layout import PyMuPDFLayoutParser

            parser = PyMuPDFLayoutParser()

        Lazily parse the blob:

        .. code-block:: python

            docs = []
            docs_lazy = parser.lazy_parse(blob)

            for doc in docs_lazy:
                docs.append(doc)
            print(docs[0].page_content[:100])
            print(docs[0].metadata)
    """

    # PyMuPDF is not thread safe.
    # See https://pymupdf.readthedocs.io/en/latest/recipes-multiprocessing.html
    _lock = threading.Lock()

    def __init__(
        self,
        *,
        password: Optional[str] = None,
        **pymupdf_layout_kwargs,
    ) -> None:
        """Initialize a parser to extract PDF content in markdown using PyMuPDF4LLM.

        Args:
            password: Optional password for opening encrypted PDFs.
            **pymupdf_layout_kwargs: Additional keyword arguments to pass directly to the
                `pymupdf4llm.to_markdown` function. 
                See: https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html#to_markdown
                And: https://pymupdf.readthedocs.io/en/latest/pymupdf-layout/index.html#pymupdf-layout-and-parameter-caveats

        Returns:
            This method does not directly return data. Use the `parse` or `lazy_parse`
            methods to retrieve parsed documents with content and metadata.

        Raises:
            ValueError: If unsupported `pymupdf_layout_kwargs` are provided (e.g.,
                `table_strategy`, `detect_bg_color`, `ignore_images`).
        """

        if "table_strategy" in pymupdf_layout_kwargs:
            raise ValueError("PyMuPDF Layout argument: table_strategy should not be set")
        
        if "ignore_images" in pymupdf_layout_kwargs:
            raise ValueError("PyMuPDF Layout argument: ignore_images should not be set")
        
        if "graphics_limit" in pymupdf_layout_kwargs:
            raise ValueError("PyMuPDF Layout argument: graphics_limit should not be set")
        
        if "detect_bg_color" in pymupdf_layout_kwargs:
            raise ValueError("PyMuPDF Layout argument: detect_bg_color should not be set")
            
        super().__init__()

        self.password = password
        self.pymupdf_layout_kwargs = pymupdf_layout_kwargs

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        """Lazily parse a blob from a PDF document.

        Args:
            blob: The blob from a PDF document to parse.

        Raises:
            ImportError: If the `pymupdf4llm` package is not found.

        Yield:
            An iterator over the parsed documents with PDF content.
        """
        
        with PyMuPDFLayoutParser._lock:
            with blob.as_bytes_io() as file_path:
                if blob.data is None:
                    doc = pymupdf.open(file_path)
                else:
                    doc = pymupdf.open(stream=file_path, filetype="pdf")
                if doc.is_encrypted:
                    doc.authenticate(self.password)
                doc_metadata = self._extract_metadata(doc, blob)

                yield Document(
                        page_content=self._get_md(doc),
                        metadata=_validate_metadata(doc_metadata),
                    )

    def _get_md(
        self,
        doc: pymupdf.Document,
        #pages: list | range | None = None,
    ) -> str:
        """Get the content of the page in markdown using PyMuPDF4LLM 

        Args:
            doc: The PyMuPDF document object.
            pages: The pages. If omitted (None) all pages are processed.

        Returns:
            str: The content of the page in markdown.
        """
        try:
            import pymupdf4llm 
        except ImportError:
            raise ImportError(
                "pymupdf4llm package not found, please install it "
                "with `pip install pymupdf4llm`"
            )

        pymupdf4llm_params: dict[str, Any] = {
            **self.pymupdf_layout_kwargs,
        }

        md = pymupdf4llm.to_markdown(
            doc,
            **pymupdf4llm_params,
        )
        
        return md

    def _extract_metadata(self, doc: pymupdf.Document, blob: Blob) -> dict:
        """Extract metadata from the PDF document.

        Args:
            doc: The PyMuPDF document object.
            blob: The blob being parsed.

        Returns:
            dict: The extracted metadata from the PDF.
        """
        metadata = _purge_metadata(
            {
                **{
                    "producer": "PyMuPDF Layout",
                    "creator": "PyMuPDF Layout",
                    "creationdate": "",
                    "source": blob.source,
                    "file_path": blob.source,
                    "total_pages": len(doc),
                },
                **{
                    k: doc.metadata[k]
                    for k in doc.metadata
                    if isinstance(doc.metadata[k], (str, int))
                },
            }
        )
        for k in ("modDate", "creationDate"):
            if k in doc.metadata:
                metadata[k] = doc.metadata[k]
        return metadata
