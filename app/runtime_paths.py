from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimePaths:
    database: Path
    artifact: Path


def runtime_paths(project_root: Path, environment: Mapping[str, str]) -> RuntimePaths:
    runtime_dir = Path(environment.get("TRIAGEFLOW_RUNTIME_DIR", project_root))
    return RuntimePaths(
        database=Path(environment.get("TRIAGEFLOW_DB_PATH", runtime_dir / "triageflow.db")),
        artifact=Path(
            environment.get(
                "TRIAGEFLOW_ARTIFACT_PATH", runtime_dir / "artifacts" / "ticket_classifier.joblib"
            )
        ),
    )
