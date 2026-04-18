"""OcrChunkSaver — persists a list of OcrChunkBase objects to the database.

Usage
-----
::

    saver = OcrChunkSaver()
    saved = saver.save(chunks, replace=True)
    # → list[OcrChunkModel]

When ``replace=True`` (the default) any existing chunks for the same
``content_hash`` are deleted first so re-indexing a document is idempotent.
"""

from __future__ import annotations


import time
from typing import List

from src.logger import logger
from src.schemas.ocr_chunks import OcrChunkBase, OcrChunkModel
from services.client.tools import server_client


class OcrChunkSaver:
    """Saves OCR chunks to the database via ``OcrChunkRepository``."""

    def save(
        self,
        chunks: List[OcrChunkBase],
        replace: bool = True,
    ) -> List[OcrChunkModel]:
        """Persist *chunks* and return the stored models.

        Parameters
        ----------
        chunks:
            Non-empty list of ``OcrChunkBase`` objects sharing the same
            ``content_hash``.  Mixed content hashes are not supported and will
            raise a ``ValueError``.
        replace:
            When ``True``, all existing chunks for the ``content_hash`` are
            deleted before inserting the new ones.  Set to ``False`` to append
            without clearing.

        Returns
        -------
        list[OcrChunkModel]
            The rows as they exist in the database after the operation.
        """
        if not chunks:
            logger.debug("[OcrChunkSaver] No chunks to save — skipping.")
            return []

        content_hashes = {c.content_hash for c in chunks}
        if len(content_hashes) > 1:
            raise ValueError(
                f"OcrChunkSaver.save() received chunks with multiple content_hashes: "
                f"{content_hashes}.  All chunks must belong to the same document."
            )

        content_hash = content_hashes.pop()
        t0 = time.perf_counter()

        if replace:
            server_client.delete_by_content_hash(content_hash)
            logger.debug(f"[OcrChunkSaver] Cleared existing chunks for content_hash={content_hash!r}")
        chunk_to_dicts = [c.model_dump() for c in chunks]
        server_client.upsert_chunks(chunk_to_dicts, content_hash, replace=False)
        saved = server_client.get_by_content_hash(content_hash)
        saved_models = [OcrChunkModel.model_validate(c) for c in saved]

        elapsed = time.perf_counter() - t0
        logger.info(
            f"[OcrChunkSaver] Saved {len(saved_models)} chunks for content_hash={content_hash!r} in {elapsed * 1000:.1f} ms"
        )
        return saved_models
