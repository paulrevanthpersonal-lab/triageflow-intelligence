from pathlib import Path

from app.runtime_paths import runtime_paths


def test_runtime_paths_keep_local_defaults_under_the_project_root():
    paths = runtime_paths(Path("/project"), {})

    assert paths.database == Path("/project/triageflow.db")
    assert paths.artifact == Path("/project/artifacts/ticket_classifier.joblib")


def test_runtime_paths_use_one_configured_writable_directory_for_both_outputs():
    paths = runtime_paths(Path("/project"), {"TRIAGEFLOW_RUNTIME_DIR": "/runtime"})

    assert paths.database == Path("/runtime/triageflow.db")
    assert paths.artifact == Path("/runtime/artifacts/ticket_classifier.joblib")


def test_explicit_runtime_paths_override_the_shared_directory():
    paths = runtime_paths(
        Path("/project"),
        {
            "TRIAGEFLOW_RUNTIME_DIR": "/runtime",
            "TRIAGEFLOW_DB_PATH": "/state/support.db",
            "TRIAGEFLOW_ARTIFACT_PATH": "/models/current.joblib",
        },
    )

    assert paths.database == Path("/state/support.db")
    assert paths.artifact == Path("/models/current.joblib")
