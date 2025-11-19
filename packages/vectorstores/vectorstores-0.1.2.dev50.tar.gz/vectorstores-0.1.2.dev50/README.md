# vectorstores

Utilities for pushing vectors and metadata into a Weaviate instance. The package ships a `WeaviateVectorStore` implementation plus a simple `VectorStore` interface you can build on.

## Installation

```bash
pip install vectorstores
```

## Quickstart

```python
import weaviate
from vectorstores import WeaviateVectorStore

# create a client (configure URL/auth to match your deployment)
client = weaviate.connect_to_local()  # or weaviate.connect_to_wcs(...)

store = WeaviateVectorStore(
    client=client,
    index_name="MyIndex",
    text_key="text",
)

# add data (stores text plus optional metadata; vectors can be provided explicitly)
ids = store.add_vector(
    vectors=["Hello world", "Another sample"],
    metadatas=[{"topic": "greeting"}, {"topic": "example"}],
)
print(ids)

# delete by id
store.delete(ids=[ids[0]])
```

### Notes
- If you want multi-tenancy, pass `use_multi_tenancy=True` when constructing the store and provide `tenant=...` to write/delete calls.
- If you already have embeddings and want to bypass internal embedding, pass them via `vectors` and supply matching `metadatas`/`ids`.

## Development

Create a virtual environment and install dependencies with tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[tests]
```

Run checks:

```bash
ruff check .
mypy .
pytest
```

## Building and uploading to PyPI

1) Clean old artifacts (optional but recommended):
```bash
rm -rf dist build *.egg-info
```
2) Build the wheel and sdist:
```bash
python -m build
```
3) Upload to PyPI with Twine:
```bash
twine upload dist/*
```
Make sure your PyPI credentials are configured (e.g., via `~/.pypirc` or environment variables) before running the upload.
