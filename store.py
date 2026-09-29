"""
Stages 3 and 4 of the pipeline: embedding chunks and retrieving them.

Three things in here are worth knowing about, because they'd quietly break the
rest of the project if they were wrong:

1. The Chroma collection is created with cosine distance, explicitly. Chroma
   defaults to squared L2, and the 0.6 threshold the course uses is calibrated
   against cosine. Getting this wrong makes every distance number meaningless.

2. `search` returns the distance alongside each chunk. Milestone 4 has you
   compare distances, so they have to be visible.

3. The embedding model is the one Chroma bundles, not one loaded through
   `sentence-transformers`. It is the same model - `all-MiniLM-L6-v2`, 384
   dimensions - but it arrives as an ONNX build from Chroma's own CDN, so the
   install needs neither PyTorch nor a reachable Hugging Face. See `_embedder`.

Unit 2 addition: optional hybrid search. When `config.USE_HYBRID_SEARCH` is
True, `search` blends the Chroma cosine distance with a BM25 keyword score
computed over the same chunks, so exact terms (names, numbers, specific nouns
like "shuttle" or "hours") that semantic search glides past can still pull a
chunk to the top.

The BM25 score is converted to a 0-1 "boost" with a saturating curve
(score / (score + K)) instead of dividing by any kind of maximum. A max-based
normalization is fragile two different ways: normalizing per-query inflates
weak matches on off-topic questions to look strong (breaks the relevance
gate); normalizing against a global ceiling computed from unrelated text
(e.g. scoring a chunk against itself) creates a ceiling far higher than any
real question ever scores, which mutes the boost to near nothing. The
saturating curve needs no ceiling at all: it rewards real keyword overlap
and stays near zero when there isn't any, regardless of what else is in
the corpus.
"""

import os
import pickle
import re
import shutil
from dataclasses import dataclass

# Must be set BEFORE chromadb is imported. Without it, some Chroma versions
# print "Failed to send telemetry event ..." on every single call - which looks
# exactly like a real error, isn't one, and cost a previous cohort a lot of
# confused help-channel messages.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

import chromadb  # noqa: E402
from rank_bm25 import BM25Okapi  # noqa: E402

import config
from chunker import Chunk


@dataclass
class Result:
    """One retrieved chunk and how far it was from the question."""

    text: str
    source: str
    label: str
    distance: float   # LOWER IS BETTER. 0.3 is close, 0.9 is unrelated.
    produced_by: str


_model = None

# The model Chroma bundles. Anything else in config.EMBEDDING_MODEL means
# "fetch that one from Hugging Face instead" - see `_embedder`.
BUNDLED_MODEL = "all-MiniLM-L6-v2"

BM25_DIR = config.CACHE_DIR / "bm25"

# How quickly the BM25 boost saturates. A raw BM25 score equal to this value
# gives a boost of 0.5; much higher scores approach 1.0; scores near 0 (no
# real keyword overlap) give a boost near 0. Tuned against this corpus's
# question-level scores, which mostly land between 1 and 12.
BM25_SATURATION_K = 5.0


def _tokenize(text: str) -> list[str]:
    """Lowercase, alphanumeric-only tokens. Good enough for BM25 over short
    campus-life documents; no need for a real NLP tokenizer here."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _bm25_path(corpus, variant) -> "os.PathLike":
    name = config.collection_name(corpus, variant)
    return BM25_DIR / f"{name}.pkl"


class _OnnxEmbedder:
    """
    Chroma's built-in embedder, wrapped to look like the other two.

    Chroma's embedding functions are called directly and hand back numpy
    arrays. The rest of this file wants `.encode(texts)`, so the adapter lives
    here rather than making every caller care which embedder it got.
    """

    def __init__(self):
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        self._ef = ONNXMiniLM_L6_V2()

    def encode(self, texts, show_progress_bar: bool = False):
        return [vector.tolist() for vector in self._ef(list(texts))]


def _sentence_transformer(name: str):
    """
    The escape hatch: any model that isn't the bundled one.

    Unit 2's "try a second embedding model" stretch option comes through here,
    and so does anything you set `EMBEDDING_MODEL` to. This path *does* need
    `sentence-transformers` and a reachable Hugging Face, neither of which the
    default install has - which is the whole point of the default install.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            f"config.EMBEDDING_MODEL is set to {name!r}, which isn't the model "
            f"Chroma bundles ({BUNDLED_MODEL!r}), so it has to be downloaded "
            f"from Hugging Face.\n"
            f"Install the optional dependency first:\n"
            f"    pip install 'sentence-transformers>=3.4,<3.5'\n"
            f"Or set EMBEDDING_MODEL back to {BUNDLED_MODEL!r}."
        ) from exc

    return SentenceTransformer(name)


def _embedder():
    """
    Load the embedding model once and keep it.

    First call is slow - it downloads about 80 MB. That's why setup happens
    before class.
    """
    global _model

    if _model is not None:
        return _model

    # Used only by this repo's own smoke test, which runs where no model can be
    # downloaded at all. Never set this yourself.
    if os.getenv("AI201_FAKE_EMBEDDINGS") == "1":
        from _smoke_embedder import FakeEmbedder

        _model = FakeEmbedder()
    elif config.EMBEDDING_MODEL == BUNDLED_MODEL:
        _model = _OnnxEmbedder()
    else:
        _model = _sentence_transformer(config.EMBEDDING_MODEL)

    return _model


def embed(texts: list[str]) -> list[list[float]]:
    """Turn text into vectors. Runs on your machine, costs no API quota."""
    vectors = _embedder().encode(texts, show_progress_bar=False)
    # sentence-transformers and the smoke stand-in return something with a
    # .tolist(); _OnnxEmbedder has already done that conversion itself.
    return vectors.tolist() if hasattr(vectors, "tolist") else vectors


def _client():
    return chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=chromadb.config.Settings(anonymized_telemetry=False),
    )


def build_index(
    chunks: list[Chunk],
    corpus: str | None = None,
    variant: str = "default",
) -> int:
    """
    Embed every chunk and store it. Also builds and pickles a BM25 index over
    the same chunks, for unit 2's hybrid-search option.

    `variant` lets you keep more than one index of the same corpus at the same
    time. In unit 2, when you compare two chunking strategies, index the second
    one as variant="v2" and you can query both instead of deleting the first
    and starting over.
    """
    name = config.collection_name(corpus, variant)
    client = _client()

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(
        name=name,
        # Do not remove. Chroma defaults to squared L2, and every distance
        # number in this course assumes cosine.
        metadata={"hnsw:space": "cosine"},
    )

    batch = 256
    for start in range(0, len(chunks), batch):
        window = chunks[start : start + batch]
        collection.add(
            ids=[f"{c.source}#{c.index}" for c in window],
            documents=[c.text for c in window],
            embeddings=embed([c.text for c in window]),
            metadatas=[
                {"source": c.source, "index": c.index, "produced_by": c.produced_by}
                for c in window
            ],
        )

    # Build the BM25 index alongside it, keyed the same way as the Chroma ids.
    # No global maximum is stored - the saturating boost formula in `search`
    # doesn't need one.
    BM25_DIR.mkdir(parents=True, exist_ok=True)
    tokenized = [_tokenize(c.text) for c in chunks]
    bm25 = BM25Okapi(tokenized) if tokenized else None
    payload = {
        "bm25": bm25,
        "labels": [f"{c.source}#{c.index}" for c in chunks],
    }
    with open(_bm25_path(corpus, variant), "wb") as f:
        pickle.dump(payload, f)

    return len(chunks)


def _bm25_scores(question: str, corpus, variant):
    """Load the pickled BM25 index for this corpus/variant and score the
    question against every chunk. Returns {label: raw_score}, or None if no
    BM25 index has been built yet."""
    path = _bm25_path(corpus, variant)
    if not path.exists():
        return None

    with open(path, "rb") as f:
        payload = pickle.load(f)

    bm25 = payload.get("bm25")
    labels = payload.get("labels", [])
    if bm25 is None or not labels:
        return None

    scores = bm25.get_scores(_tokenize(question))
    return dict(zip(labels, scores))


def search(
    question: str,
    top_k: int | None = None,
    corpus: str | None = None,
    variant: str = "default",
) -> list[Result]:
    """
    Retrieve the chunks closest in meaning to a question.

    Returns them nearest-first, each with its distance.

    When `config.USE_HYBRID_SEARCH` is True, distance is a fused score: cosine
    similarity blended with a saturating BM25 keyword boost, weighted by
    `config.HYBRID_ALPHA` (1.0 = pure semantic, 0.0 = pure keyword). The fused
    value keeps the same "lower is better" convention as plain cosine distance,
    so the existing THRESHOLD gate and eval code don't need to change.
    """
    top_k = top_k or config.TOP_K
    name = config.collection_name(corpus, variant)

    try:
        collection = _client().get_collection(name)
    except Exception as exc:
        raise RuntimeError(
            f"No index called '{name}'. Run `python app.py index` first."
        ) from exc

    use_hybrid = getattr(config, "USE_HYBRID_SEARCH", False)
    total = collection.count()
    fetch_k = total if use_hybrid else min(top_k, total)

    raw = collection.query(
        query_embeddings=embed([question]),
        n_results=fetch_k,
    )

    # Step 1: collect every candidate from Chroma, with its plain cosine
    # distance. This loop does nothing else - fusion happens once, after it,
    # not on every iteration.
    candidates = []
    for text, meta, distance in zip(
        raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
    ):
        candidates.append(
            {
                "text": text,
                "meta": meta,
                "distance": float(distance),
            }
        )

    # Step 2: fuse in the BM25 boost, once, over the whole candidate list.
    if use_hybrid:
        bm25_scores = _bm25_scores(question, corpus, variant)
        if bm25_scores:
            alpha = getattr(config, "HYBRID_ALPHA", 0.5)
            k = getattr(config, "BM25_SATURATION_K", BM25_SATURATION_K)

            for cand in candidates:
                label = f"{cand['meta'].get('source')}#{cand['meta'].get('index')}"
                bm25_raw = max(bm25_scores.get(label, 0.0), 0.0)
                bm25_boost = bm25_raw / (bm25_raw + k)
                semantic_similarity = 1.0 - cand["distance"]
                fused_similarity = alpha * semantic_similarity + (1 - alpha) * bm25_boost
                cand["distance"] = 1.0 - fused_similarity

            candidates.sort(key=lambda c: c["distance"])

        candidates = candidates[:top_k]

    # Step 3: build the Result objects. Also runs once, on the final list.
    results: list[Result] = []
    for cand in candidates:
        meta = cand["meta"]
        results.append(
            Result(
                text=cand["text"],
                source=str(meta.get("source", "unknown")),
                label=f"{meta.get('source', 'unknown')}#{meta.get('index', 0)}",
                distance=cand["distance"],
                produced_by=str(meta.get("produced_by", "unknown")),
            )
        )
    return results


def index_exists(corpus: str | None = None, variant: str = "default") -> bool:
    """Is there an index here to search, without searching it?

    `serve.py`'s health check asks this. It deliberately does not embed
    anything: loading the embedding model takes 80 MB and a few seconds, and a
    health check that heavy is a health check nobody can afford to call.
    """
    try:
        collection = _client().get_collection(config.collection_name(corpus, variant))
        return collection.count() > 0
    except Exception:
        return False


def reset():
    """Delete every index. Occasionally the fastest way out of a mess."""
    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
    if BM25_DIR.exists():
        shutil.rmtree(BM25_DIR)
