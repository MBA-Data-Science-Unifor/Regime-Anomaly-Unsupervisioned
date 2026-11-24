from regime_anomaly import ARTIFACT_CONTRACT, ARTIFACTS, RAW_DIR


def test_artifact_contract_stays_inside_artifacts() -> None:
    assert RAW_DIR.is_relative_to(ARTIFACTS)
    assert ARTIFACT_CONTRACT["model"].startswith("models/")
    assert ARTIFACT_CONTRACT["metrics"].startswith("metadata/")
