import pytest

from streaming_transcriber.config import TranscriptionConfig


def test_config_validation_success() -> None:
    config = TranscriptionConfig()
    config.validate()


def test_config_validation_errors() -> None:
    with pytest.raises(ValueError):
        TranscriptionConfig(language_code="").validate()
    with pytest.raises(ValueError):
        TranscriptionConfig(sample_rate_hz=0).validate()
    with pytest.raises(ValueError):
        TranscriptionConfig(chunk_size=0).validate()
    with pytest.raises(ValueError):
        TranscriptionConfig(chunk_size=3).validate()
    with pytest.raises(ValueError):
        TranscriptionConfig(chunk_delay=-0.5).validate()

