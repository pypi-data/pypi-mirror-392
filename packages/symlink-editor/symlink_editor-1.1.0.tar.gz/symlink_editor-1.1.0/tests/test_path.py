#!../venv/bin/pytest

import os
import pathlib

from symlink_editor.main import FPath as Path


def test_path_raw() -> None:
	p = Path('/a/b/c')
	assert "<{p}>".format(p=p) == "</a/b/c>"


def test_path_parent() -> None:
	p = Path('/a/b/c')
	assert "<{p.parent}>".format(p=p) == "</a/b>"

def test_path_double_parent() -> None:
	p = Path('/a/b/c')
	assert "<{p.parent.parent}>".format(p=p) == "</a>"


def test_path_name() -> None:
	p = Path('/a/b/c')
	assert "<{p.name}>".format(p=p) == "<c>"


def test_path_abs() -> None:
	p = Path('.')
	assert "{p.abs}".format(p=p) == os.path.abspath(os.path.curdir)

def test_path_parent_of_abs() -> None:
	p = Path('abc')
	assert "Parent of abs: {p.abs.parent}".format(p=p) == "Parent of abs: %s" % os.path.abspath(os.path.curdir)
	assert "Abs of parent: {p.parent.abs}".format(p=p) == "Abs of parent: %s" % os.path.abspath(os.path.curdir)


def test_path_rel() -> None:
	p = Path(os.path.abspath(os.path.curdir))
	assert "{p.rel}".format(p=p) == "."


def test_path_real(tmp_path: 'pathlib.Path') -> None:
	os.mkdir(tmp_path / 'target')
	os.symlink(tmp_path / 'target', tmp_path / 'link')

	link = Path(str(tmp_path / 'link' / 'a'))
	assert "{link.real}".format(link=link) == str(tmp_path / 'target' / 'a')


def test_path_ext() -> None:
	link = Path('/a/b/c.jpg')
	assert "{link.ext}".format(link=link) == '.jpg'

def test_path_base() -> None:
	link = Path('/a/b/c.jpg')
	assert "{link.base}".format(link=link) == '/a/b/c'


def test_tilde() -> None:
	link = Path(os.path.expanduser('~/img.jpg'))
	assert "{link.tilde}".format(link=link) == '~/img.jpg'
