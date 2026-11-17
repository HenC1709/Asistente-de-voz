import pytest
from asistente.infrastructure.system.local_actions import LocalFiles, ConfiguredLauncher
from asistente.application.use_cases.local_actions import LocalActions


@pytest.mark.parametrize('name', ['../escape.txt', 'C:\\escape.txt', 'a:b', '..', 'CON.txt', 'LPT1', 'trailing.', 'x/y', ''])
def test_reject_unsafe_names(tmp_path, name):
    with pytest.raises(ValueError):
        LocalFiles(tmp_path).create(name)


def test_create_search_and_no_overwrite(tmp_path):
    files = LocalFiles(tmp_path)
    files.create('nota.txt')
    assert files.search('nota') == ['nota.txt']
    with pytest.raises(FileExistsError):
        files.create('nota.txt')


def test_changed_file_not_deleted(tmp_path):
    files = LocalFiles(tmp_path)
    files.create('nota.txt')
    token = files.inspect('nota.txt')
    (tmp_path / 'nota.txt').write_text('changed')
    with pytest.raises(ValueError):
        files.trash('nota.txt', token)


def test_confirmation_expiration_and_cancel(tmp_path, monkeypatch):
    files = LocalFiles(tmp_path)
    files.create('nota.txt')
    calls = []
    monkeypatch.setattr(files, 'trash', lambda *args: calls.append(args))
    now = [0]
    actions = LocalActions(files, None, lambda: now[0])
    actions.confirm('nota.txt')
    assert not calls
    actions.delete('nota.txt')
    now[0] = 21
    actions.confirm('nota.txt')
    assert not calls
    actions.delete('nota.txt')
    actions.cancel('')
    actions.confirm('nota.txt')
    assert not calls
    actions.delete('nota.txt')
    actions.confirm('nota.txt')
    assert len(calls) == 1
    actions.confirm('nota.txt')
    assert len(calls) == 1


def test_trash_uses_recycle_bin(tmp_path, monkeypatch):
    import send2trash
    calls = []
    monkeypatch.setattr(send2trash, 'send2trash', calls.append)
    files = LocalFiles(tmp_path)
    files.create('demo.txt')
    files.trash('demo.txt', files.inspect('demo.txt'))
    assert calls == [str(tmp_path / 'demo.txt')]


def test_launcher_does_not_execute_unknown(tmp_path):
    with pytest.raises(ValueError):
        ConfiguredLauncher({}, tmp_path).open('cmd /c anything')
