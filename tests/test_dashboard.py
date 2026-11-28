import hashlib
import json

import pandas as pd

from regime_anomaly import dashboard
from regime_anomaly.dashboard import parse_timestamps


def test_parse_timestamps_keeps_iso_days_above_twelve_and_uci_dates() -> None:
    values = pd.Series(["2018-01-13 00:15:00", "2019-01-01 00:00:00", "13/01/2018 00:30"])
    parsed = parse_timestamps(values)
    assert parsed.tolist() == [
        pd.Timestamp("2018-01-13 00:15"),
        pd.Timestamp("2019-01-01 00:00"),
        pd.Timestamp("2018-01-13 00:30"),
    ]


def test_artifact_versions_detects_creation_and_modification(tmp_path, monkeypatch) -> None:
    paths = [
        tmp_path / name
        for name in (
            "results.csv",
            "metrics.json",
            "model.joblib",
            "prep.json",
            "prepared.csv",
            "manifest.json",
            "raw.csv",
        )
    ]
    for key, path in zip(
        (
            "RESULTS_PATH",
            "METRICS_PATH",
            "MODEL_PATH",
            "PREPROCESSING_PATH",
            "PREPARED_PATH",
            "MANIFEST_PATH",
            "RAW_PATH",
        ),
        paths,
    ):
        monkeypatch.setattr(dashboard, key, path)
    assert dashboard.artifact_versions() == (0, 0, 0, 0, 0, 0, 0)
    paths[0].write_text("first", encoding="utf-8")
    first = dashboard.artifact_versions()
    assert first[0] > 0
    paths[1].write_text("{}", encoding="utf-8")
    assert dashboard.artifact_versions()[1] > 0
    paths[0].unlink()
    assert dashboard.artifact_versions()[0] == 0


def test_artifact_audit_detects_modified_output_and_provenance(tmp_path, monkeypatch) -> None:
    root = tmp_path / "artifacts"
    paths = {
        "RAW_PATH": root / "data/raw/source.csv",
        "PREPARED_PATH": root / "data/processed/prepared_dataset.csv",
        "PREPROCESSING_PATH": root / "metadata/preprocessing.json",
        "RESULTS_PATH": root / "data/processed/analysis_results.csv",
        "METRICS_PATH": root / "metadata/final_metrics.json",
        "MODEL_PATH": root / "models/final_model.joblib",
        "MANIFEST_PATH": root / "metadata/manifest.json",
    }
    monkeypatch.setattr(dashboard, "ARTIFACTS", root)
    for key, path in paths.items():
        monkeypatch.setattr(dashboard, key, path)
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["RAW_PATH"].write_bytes(b"raw")
    raw_hash = hashlib.sha256(b"raw").hexdigest()
    paths["PREPROCESSING_PATH"].write_text(json.dumps({"fonte": {"sha256": raw_hash}}))
    paths["METRICS_PATH"].write_text(json.dumps({"dados_sha256": raw_hash}))
    for key in ("PREPARED_PATH", "RESULTS_PATH", "MODEL_PATH"):
        paths[key].write_bytes(b"result")
    hashes = {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for key, path in paths.items()
        if key not in {"MANIFEST_PATH", "RAW_PATH"}
    }
    paths["MANIFEST_PATH"].write_text(
        json.dumps({"dados_brutos": {"sha256": raw_hash}, "artefatos": hashes})
    )
    statuses = dashboard.audit_artifacts().set_index("Artefato")["Integridade"]
    assert (statuses == "Íntegro").all()
    paths["RESULTS_PATH"].write_bytes(b"changed")
    assert (
        dashboard.audit_artifacts().set_index("Artefato").loc["Resultados", "Integridade"]
        == "Divergente"
    )
    paths["PREPROCESSING_PATH"].write_text(json.dumps({"fonte": {"sha256": "another_source"}}))
    statuses = dashboard.audit_artifacts().set_index("Artefato")["Integridade"]
    assert statuses["Modelo"] == "Proveniência divergente"


def test_alert_counts_separate_kept_suppressed_and_unknown() -> None:
    frame = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2018-01-01 00:15", "2018-01-01 01:00", "2018-01-02 00:15", "2018-01-02 00:30"]
            ),
            "is_anomaly_raw": pd.Series([True, True, True, False], dtype="boolean"),
            "is_anomaly": pd.Series([True, False, pd.NA, False], dtype="boolean"),
        }
    )
    kept, suppressed = dashboard.alert_masks(frame)
    assert kept.tolist() == [True, False, False, False]
    assert suppressed.tolist() == [False, True, False, False]
    result = dashboard.daily_alert_counts(frame)
    assert result["Mantidos"].tolist() == [1, 0]
    assert result["Suprimidos"].tolist() == [1, 0]
