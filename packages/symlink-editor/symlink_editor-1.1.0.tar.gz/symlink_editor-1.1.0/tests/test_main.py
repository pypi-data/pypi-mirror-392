#!../venv/bin/pytest

import pytest

from symlink_editor import __version__
from symlink_editor.main import main


def test_version(capsys: 'pytest.CaptureFixture[str]') -> None:
	with pytest.raises(SystemExit) as e:
		main(['--version'])
	assert e.value.code in (0, None)
	captured = capsys.readouterr()
	assert captured.err == ""
	assert captured.out.startswith("symlink-editor %s\n" % __version__)
