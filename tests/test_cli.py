from asistente.main import main


def test_check(capsys):
    assert main(["--check"]) == 0
    assert "válidas" in capsys.readouterr().out


def test_dry_run_search(capsys):
    assert main(["--dry-run", "--command", "busca en google café & té"]) == 0
    assert "caf%C3%A9+%26+t%C3%A9" in capsys.readouterr().out


def test_invalid_config_exits_cleanly(tmp_path, capsys):
    path = tmp_path / "invalid.json"
    path.write_text("{}")
    assert main(["--config", str(path), "--check"]) == 1
    assert "wake_word" in capsys.readouterr().out
