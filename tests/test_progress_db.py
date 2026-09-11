import os
import tempfile
import progress.db as db_module


def setup_temp_db(monkeypatch):
    """Redirects the module's DB_PATH to a temporary file for test isolation,
    so tests never touch the real submission_history.db."""
    tmp_path = tempfile.mktemp(suffix=".db")
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path)
    db_module.init_db()
    return tmp_path


def test_first_submission_has_no_previous(monkeypatch):
    setup_temp_db(monkeypatch)
    result = db_module.get_previous_submission("user_a", "main.py")
    assert result is None


def test_save_and_retrieve_submission(monkeypatch):
    setup_temp_db(monkeypatch)
    issues = [{"rule_id": "bare_except", "message": "msg", "severity": "critical"}]
    db_module.save_submission("user_a", "main.py", issues, quality_score=4)

    previous = db_module.get_previous_submission("user_a", "main.py")
    assert previous is not None
    assert previous["total_issues"] == 1
    assert previous["quality_score"] == 4
    assert previous["issues"] == issues


def test_different_users_are_isolated(monkeypatch):
    setup_temp_db(monkeypatch)
    db_module.save_submission("user_a", "main.py", [{"rule_id": "x", "message": "m", "severity": "minor"}], 2)

    result = db_module.get_previous_submission("user_b", "main.py")
    assert result is None  # user_b has no history, even though user_a submitted the same filename


def test_different_filenames_are_isolated(monkeypatch):
    setup_temp_db(monkeypatch)
    db_module.save_submission("user_a", "main.py", [{"rule_id": "x", "message": "m", "severity": "minor"}], 2)

    result = db_module.get_previous_submission("user_a", "other.py")
    assert result is None


def test_get_previous_returns_most_recent(monkeypatch):
    setup_temp_db(monkeypatch)
    db_module.save_submission("user_a", "main.py", [{"rule_id": "first", "message": "m1", "severity": "minor"}], 2)
    db_module.save_submission("user_a", "main.py", [{"rule_id": "second", "message": "m2", "severity": "info"}], 1)

    previous = db_module.get_previous_submission("user_a", "main.py")
    assert previous["issues"][0]["rule_id"] == "second"