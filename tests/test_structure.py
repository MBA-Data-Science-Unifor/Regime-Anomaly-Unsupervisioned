from regime_anomaly.config import ARTIFACTS, RAW_DIR
from regime_anomaly.pipeline import ARTIFACT_CONTRACT


def test_artifact_contract_stays_inside_artifacts() -> None:
    assert RAW_DIR.is_relative_to(ARTIFACTS)
    assert ARTIFACT_CONTRACT["model"].startswith("models/")
    assert ARTIFACT_CONTRACT["metrics"].startswith("metadata/")
