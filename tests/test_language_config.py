from exam_mode.language_config import LANGUAGE_CONFIG, is_language_supported_for_execution, get_language_config


def test_python_and_java_supported_without_config_entry():
    assert is_language_supported_for_execution("python") is True
    assert is_language_supported_for_execution("java") is True


def test_configured_languages_supported():
    for lang in ["c", "cpp", "javascript", "ruby", "go", "php"]:
        assert is_language_supported_for_execution(lang) is True


def test_unconfigured_language_not_supported():
    assert is_language_supported_for_execution("rust") is False
    assert is_language_supported_for_execution("haskell") is False


def test_get_language_config_returns_none_for_unknown():
    assert get_language_config("rust") is None


def test_each_config_entry_has_required_fields():
    for lang, config in LANGUAGE_CONFIG.items():
        assert "image" in config
        assert "filename" in config
        assert "run_cmd" in config
        assert "compile_cmd" in config