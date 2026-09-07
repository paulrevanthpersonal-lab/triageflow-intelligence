# Operations Runbook

## Start

```bash
make setup
make data
make run
```

Open `http://localhost:8000` and confirm `/health` returns `model_ready: true`.

## Validate

```bash
make check
```

The check runs static analysis, API/model tests, and Python compilation. CI additionally enforces macro-F1 quality floors.

## Reset local state

Stop the service, remove `triageflow.db` and `artifacts/`, regenerate the dataset, and restart. Both paths are ignored by Git because they are local runtime evidence. Set `TRIAGEFLOW_RUNTIME_DIR` to keep both outputs together in another writable location.

## Container runtime state

Docker sets `TRIAGEFLOW_RUNTIME_DIR=/app/runtime`; Docker Compose persists that
directory in the `triageflow-data` volume. The SQLite database and trained model
artifact therefore survive a container restart without writing into the read-only
application source tree. To reset the container state, stop the compose service and
remove the named volume, then start it again. This is demonstration data only.

## Troubleshooting

- **Model startup is slow:** first startup trains and saves a local artifact; later runs reuse it when the dataset hash matches.
- **Model metrics changed:** regenerate the dataset with the committed script and confirm seed 42.
- **Classification returns 503:** wait for `/health` to report `model_ready: true`.
- **Screenshot capture fails:** confirm Google Chrome is installed or set `CHROME_BIN` to a compatible Chromium executable.
