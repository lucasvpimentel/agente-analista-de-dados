from src import config


def test_default_model_is_in_models_list():
    assert config.DEFAULT_MODEL in config.MODELS


def test_thresholds_are_positive():
    assert config.MAX_FILE_SIZE_MB > 0
    assert config.MAX_ROWS_FULL_PROFILE > 0
    assert config.SAMPLE_ROWS_FOR_AGENT > 0
    assert config.OUTLIER_IQR_MULTIPLIER > 0
    assert config.OUTLIER_ZSCORE_THRESHOLD > 0
    assert 0 < config.RARE_CATEGORY_THRESHOLD < 1
    assert 0 < config.CORRELATION_THRESHOLD <= 1
    assert config.MAX_CORRELATION_COLUMNS > 0
