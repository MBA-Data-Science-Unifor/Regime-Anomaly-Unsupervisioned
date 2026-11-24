import json
from pathlib import Path

from regime_anomaly.artifacts import MANIFEST, verify_manifest, write_manifest


def published_root(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "artifacts"
    for relative in ("tables/a.csv", "metadata/final_metrics.json", "data/raw/raw.csv"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative, encoding="utf-8")
    return root, root / "data/raw/raw.csv"


def test_manifest_records_raw_provenance(tmp_path: Path) -> None:
    root, raw = published_root(tmp_path)
    manifest = write_manifest(raw, root=root)
    raw_entry = manifest["dados_brutos"]
    assert isinstance(raw_entry, dict)
    assert raw_entry["bytes"] == raw.stat().st_size
    assert raw_entry["doi"] == "10.24432/C52G8C"
    assert set(manifest["artefatos"]) == {"metadata/final_metrics.json", "tables/a.csv"}  # type: ignore[arg-type]
    assert json.loads((root / MANIFEST).read_text(encoding="utf-8")) == manifest


def test_verify_detects_changed_missing_and_unlisted_files(tmp_path: Path) -> None:
    root, raw = published_root(tmp_path)
    write_manifest(raw, root=root)
    assert set(verify_manifest(root).values()) == {"ok"}

    (root / "tables/a.csv").write_text("edited", encoding="utf-8")
    (root / "metadata/final_metrics.json").unlink()
    (root / "tables/new.csv").write_text("new", encoding="utf-8")
    raw.write_text("other raw", encoding="utf-8")

    assert verify_manifest(root) == {
        "data/raw/raw.csv": "alterado",
        "metadata/final_metrics.json": "ausente",
        "tables/a.csv": "alterado",
        "tables/new.csv": "nao_registrado",
    }
