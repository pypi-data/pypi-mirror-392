import logging
import os
import re
import tempfile
from abc import ABC
from pathlib import PurePath
from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    Optional,
    Union,
)
from urllib.parse import urlparse

import requests
from langchain_core.documents import Document
from langchain_core.document_loaders import (
    Blob,
    BaseLoader,
)

from langchain_pymupdf_layout.pymupdf_layout_parser import PyMuPDFLayoutParser

logger = logging.getLogger(__file__)


# Directly taken from:-
# github.com/langchain-ai/langchain/
# libs/community/langchain_community/document_loaders/pdf.py
class BasePDFLoader(BaseLoader, ABC):
    """Base Loader class for `PDF` files.

    If the file is a web path, it will download it to a temporary file, use it, then
        clean up the temporary file after completion.
    """

    def __init__(
        self, file_path: Union[str, PurePath], *, headers: Optional[dict] = None
    ):
        """Initialize with a file path.

        Args:
            file_path: Either a local, S3 or web path to a PDF file.
            headers: Headers to use for GET request to download a file from a web path.
        """
        self.file_path = str(file_path)
        self.web_path = None
        self.headers = headers
        if "~" in self.file_path:
            self.file_path = os.path.expanduser(self.file_path)

        # If the file is a web path or S3, download it to a temporary file,
        # and use that. It's better to use a BlobLoader.
        if not os.path.isfile(self.file_path) and self._is_valid_url(self.file_path):
            self.temp_dir = tempfile.TemporaryDirectory()
            _, suffix = os.path.splitext(self.file_path)
            if self._is_s3_presigned_url(self.file_path):
                suffix = urlparse(self.file_path).path.split("/")[-1]
            temp_pdf = os.path.join(self.temp_dir.name, f"tmp{suffix}")
            self.web_path = self.file_path
            if not self._is_s3_url(self.file_path):
                r = requests.get(self.file_path, headers=self.headers)
                if r.status_code != 200:
                    raise ValueError(
                        "Check the url of your file; returned status code %s"
                        % r.status_code
                    )

                with open(temp_pdf, mode="wb") as f:
                    f.write(r.content)
                self.file_path = str(temp_pdf)
        elif not os.path.isfile(self.file_path):
            raise ValueError("File path %s is not a valid file or url" % self.file_path)

    def __del__(self) -> None:
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Check if the url is valid."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    @staticmethod
    def _is_s3_url(url: str) -> bool:
        """check if the url is S3"""
        try:
            result = urlparse(url)
            if result.scheme == "s3" and result.netloc:
                return True
            return False
        except ValueError:
            return False

    @staticmethod
    def _is_s3_presigned_url(url: str) -> bool:
        """Check if the url is a presigned S3 url."""
        try:
            result = urlparse(url)
            return bool(re.search(r"\.s3\.amazonaws\.com$", result.netloc))
        except ValueError:
            return False

    @property
    def source(self) -> str:
        return self.web_path if self.web_path is not None else self.file_path


class PyMuPDFLayoutLoader(BasePDFLoader):

    def __init__(
        self,
        file_path: Union[str, PurePath],
        *,
        headers: Optional[dict] = None,
        password: Optional[str] = None,
        **pymupdf_layout_kwargs,
    ) -> None:
        
        super().__init__(file_path, headers=headers)
        self.parser = PyMuPDFLayoutParser(
            password=password,
            **pymupdf_layout_kwargs,
        )
 

    def _lazy_load(self, **kwargs: Any) -> Iterator[Document]:
        """Lazily parse a blob from a PDF document.

        Args:
            blob: The blob from a PDF document to parse.

        Yield:
            An iterator over the parsed documents with PDF content.
        """
        if kwargs:
            logger.warning(
                f"Received runtime arguments {kwargs}. Passed runtime args to `load`"
                " are completely ignored."
                " Please pass arguments during initialization instead."
            )
        if self.web_path:
            blob = Blob.from_data(open(self.file_path, "rb").read(), path=self.web_path)
        else:
            blob = Blob.from_path(self.file_path)
        yield from self.parser.lazy_parse(blob)

    def load(self, **kwargs: Any) -> list[Document]:
        return list(self._lazy_load(**kwargs))

