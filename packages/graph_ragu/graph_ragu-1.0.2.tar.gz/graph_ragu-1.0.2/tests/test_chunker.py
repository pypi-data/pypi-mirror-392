import sys
import types

import pytest

from ragu.chunker.chunkers import SimpleChunker, SmartSemanticChunker
from ragu.utils.ragu_utils import compute_mdhash_id


@pytest.fixture
def multi_sentence_text():
    return (
        "A" * 80 + ". "
        "B" * 90 + ". "
        "C" * 60 + "."
    )


def _chunk_contents(chunks):
    return [chunk.content for chunk in chunks]


def _chunk_doc_ids(chunks):
    return [chunk.doc_id for chunk in chunks]


def test_simple_chunker_accepts_str_and_list_input(multi_sentence_text):
    chunker = SimpleChunker(max_chunk_size=80, overlap=0)

    as_string = chunker.split(multi_sentence_text)
    as_list = chunker.split([multi_sentence_text])

    assert _chunk_contents(as_string) == _chunk_contents(as_list)
    assert _chunk_doc_ids(as_string) == _chunk_doc_ids(as_list)


def test_simple_chunker_applies_overlap_between_chunks(multi_sentence_text):
    chunker = SimpleChunker(max_chunk_size=60, overlap=6)
    chunks = chunker.split(multi_sentence_text)

    assert len(chunks) >= 2, "Overlap scenario requires at least two chunks."

    carry_over = chunks[0].content[-6:].strip()
    assert carry_over, "Overlap fragment must be non-empty."
    assert carry_over in chunks[1].content, "Next chunk should contain the overlapped tail."


@pytest.fixture
def stub_smart_chunker(monkeypatch):
    calls = {"documents": []}

    class DummySmartChunker:
        def __init__(self, **kwargs):
            calls["init_kwargs"] = kwargs

        def split_into_chunks(self, source_text: str):
            calls["documents"].append(source_text)
            return [f"{source_text}::part0", f"{source_text}::part1"]

    monkeypatch.setitem(sys.modules, "smart_chunker", types.SimpleNamespace(SmartChunker=DummySmartChunker))
    return calls


def test_smart_semantic_chunker_wraps_underlying_impl(stub_smart_chunker):
    chunker = SmartSemanticChunker(device="cpu", max_chunk_length=32, minibatch_size=2, verbose=False)
    documents = ["Doc one.", "Doc two."]
    chunks = chunker.split(documents)

    # Underlying SmartChunker must be called once per document.
    assert stub_smart_chunker["documents"] == documents

    # Each document produces two chunks with deterministic order.
    assert len(chunks) == len(documents) * 2
    for doc in documents:
        doc_id = compute_mdhash_id(doc)
        doc_chunks = [c for c in chunks if c.doc_id == doc_id]
        assert [c.chunk_order_idx for c in doc_chunks] == [0, 1]
        assert [c.content for c in doc_chunks] == [f"{doc}::part0", f"{doc}::part1"]
