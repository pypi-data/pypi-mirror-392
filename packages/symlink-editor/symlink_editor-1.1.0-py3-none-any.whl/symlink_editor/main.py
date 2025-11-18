#!/usr/bin/env python3

import os
import inspect
import enum
import typing
from pathlib import Path
from collections.abc import Callable, Iterator

import confattr
from confattr import Config
from confattr.quickstart import ConfigManager

import prompt_toolkit
from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, FloatContainer, Float, Dimension, WindowAlign
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.widgets import TextArea, Frame
from prompt_toolkit.completion import Completer, PathCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.formatted_text import StyleAndTextTuples
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings

from . import __doc__, __version__
from .fuzzy_completer import FuzzyPathCompleter, CompleterMatch, BoolWithAuto

APP_NAME = 'symlink-editor'
CHANGE_LOG = 'https://gitlab.com/erzo/symlink-editor/-/tags'


# ---------- typing ----------

def assert_str(value: object) -> str:
	assert isinstance(value, str)
	return value


# ---------- Config ----------

for config in ('notification-level.user-interface', 'include.extensions', 'include.home'):
	del Config.instances[config]


class FPath:

	'''
	A path with the following properties. Properties can be combined.
	'''

	def __init__(self, path: str) -> None:
		self.raw = path

	def __str__(self) -> str:
		return self.raw

	@property
	def parent(self) -> 'FPath':
		'''The parent directory'''
		return FPath(os.path.dirname(self.raw))

	@property
	def name(self) -> 'FPath':
		'''The final component of the path'''
		return FPath(os.path.basename(self.raw))

	@property
	def abs(self) -> 'FPath':
		'''The absolute path'''
		return FPath(os.path.abspath(self.raw))

	@property
	def real(self) -> 'FPath':
		'''The canonical path with symlinks resolved'''
		return FPath(os.path.realpath(self.raw))

	@property
	def rel(self) -> 'FPath':
		'''The path relative to the directory in which the link is located'''
		return FPath(os.path.relpath(self.raw))

	@property
	def ext(self) -> 'FPath':
		"""The file extension including the dot, e.g. '.jpg'"""
		return FPath(os.path.splitext(self.raw)[1])

	@property
	def base(self) -> 'FPath':
		"""The path without the file extension"""
		return FPath(os.path.splitext(self.raw)[0])

	@property
	def tilde(self) -> 'FPath':
		'''The path in ~/ notation'''
		home = os.path.expanduser("~")
		path = self.raw
		if path.startswith(home):
			path = path.replace(home, "~", 1)
		return FPath(path)

	@property
	def existing(self) -> 'FPath':
		'''The existing beginning of the path'''
		return FPath(self.raw[:index_broken_part(self.raw)])


	@classmethod
	def iter_properties(cls) -> 'Iterator[tuple[str, str]]':
		for name, attr in inspect.getmembers(cls):
			if name.startswith('_'):
				continue
			if not isinstance(attr, property):
				continue

			assert attr.__doc__
			yield (name, attr.__doc__)


config_title = Config('window-title', "symlink-editor {link}", help="The title of the terminal window. Supports two wild cards: {link} and {target}. Both are paths supporting the following properties which can also be chained: %s" % ', '.join('%s: %s' % (name, help) for name, help in FPath.iter_properties()))
config_completer_match = Config('completer.match', CompleterMatch.CONTAINS, help='''If the word before the cursor is abc, `start` matches any file/directory starting with abc, `contains` matches any file/directory containing abc, `fuzzy` matches any file/directory which contains abc with arbitrary characters in between allowed e.g. abbc would be matched but bac would not.''')
config_case_sensitive = Config('completer.case-sensitive', BoolWithAuto.AUTO, help="auto is true if the word before the cursor contains upper case letters, false otherwise.")
config_ttimeoutlen = Config('app.ttimeoutlen', 0.1, unit="seconds", help="""\
Like Vim’s ttimeoutlen option. When to flush the input (For flushing escape keys.) This is important on terminals that use vt100 input. We can’t distinguish the escape key from for instance the left-arrow key, if we don’t know what follows after “x1b”. This little timer will consider “x1b” to be escape if nothing did follow in this time span. This seems to work like the ttimeoutlen option in Vim.
https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1181
https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/key_bindings.html#timeouts
""")


# ---------- Coloring logic ----------

def colorize_path(text: str) -> StyleAndTextTuples:
	"""Return green for existing path prefix, red for non-existing suffix."""
	if not text:
		return [("class:nonexistent", "")]

	i = index_broken_part(text)

	existing = text[:i]
	broken = text[i:]

	out: 'StyleAndTextTuples' = []
	if existing:
		out.append(("class:existing", existing))
	if broken:
		out.append(("class:nonexistent", broken))

	return out

def index_broken_part(target: str) -> int:
	parts = Path(target).parts
	existing_len = 0
	for i in range(len(parts)):
		test = Path(*parts[: i + 1])
		if test.exists():
			existing_len = len(os.path.join(*parts[: i + 1]))
		else:
			break

	# Include trailing slash if it’s part of the text
	if target[existing_len:existing_len+1] == os.sep:
		existing_len += 1

	return existing_len



class PathLexer(Lexer):
	"""Color existing/non-existing path parts."""
	def lex_document(self, document: Document) -> 'Callable[[int], StyleAndTextTuples]':
		text = document.text

		def get_line(lineno: int) -> StyleAndTextTuples:
			return colorize_path(text)

		return get_line


# ---------- Main ----------

def set_timeouts(app: 'Application[typing.Any]') -> None:
	'''
	make escape key faster
	https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1181
	'''
	# When to flush the input (For flushing escape keys.)
	# This is important on terminals that use vt100 input.
	# We can't distinguish the escape key from for instance the left-arrow key,
	# if we don't know what follows after "\x1b".
	# This little timer will consider "\x1b" to be escape if nothing did follow in this time span.
	app.ttimeoutlen = config_ttimeoutlen.value

	# Suppose that we have a key binding AB and a second key binding A.
	# If the uses presses A and then waits, we don't handle this binding yet (unless it was marked 'eager'),
	# because we don't know what will follow.
	app.timeoutlen = 0

def main(largs: 'list[str]|None' = None) -> None:
	cfg = ConfigManager(APP_NAME, __version__, __doc__, changelog_url=CHANGE_LOG, show_additional_modules_in_version=[prompt_toolkit, confattr], show_python_version_in_version=True)
	p = cfg.create_argument_parser()
	p.add_argument('-w', '--window', action='store_true', help="Give feedback in a window. This is useful if you want to integrate this into other TUI programs like yazi or ranger.")

	p.add_argument("link", help="path to the symlink to edit")
	args = p.parse_args(largs)

	if args.window:
		def print_or_display_in_window(msg: str) -> None:
			help_text = "Press [Enter] or [Escape] to quit"
			root_container = HSplit([
				Window(height=Dimension(weight=1), always_hide_cursor=True),
				Window(FormattedTextControl([("class:msg", msg)]), dont_extend_height=True, align=WindowAlign.CENTER),
				#Window(height=1),
				Window(FormattedTextControl([("class:help", help_text)]), dont_extend_height=True, align=WindowAlign.CENTER),
				Window(height=Dimension(weight=1)),
			])
			style = Style.from_dict({
				"help": "fg:#888888",
			})

			kb = KeyBindings()
			@kb.add("enter")
			@kb.add("escape")
			@kb.add("c-c")
			@kb.add("q")
			def _(event: KeyPressEvent) -> None:
				"""Exit."""
				event.app.exit()

			app: 'Application[None]' = Application(
				layout = Layout(root_container),
				key_bindings = kb,
				style = style,
				full_screen = True,
			)
			set_timeouts(app)
			app.run()
	else:
		def print_or_display_in_window(msg: str) -> None:
			print(msg)

	messages: 'list[confattr.Message]' = []
	cfg.set_ui_callback(messages.append)
	load_config_successful = cfg.load()
	formatted_messages = '\n'.join(str(msg) for msg in messages)
	if not load_config_successful:
		print_or_display_in_window(formatted_messages)
		exit(1)

	link = assert_str(args.link)
	link_path = Path(link).absolute()
	os.chdir(link_path.parent)
	if not link_path.is_symlink():
		print_or_display_in_window(f"Error: {link_path} is not a symlink.")
		exit(1)

	target = os.readlink(link_path)

	# --- UI setup ---
	header = Window(
		content=FormattedTextControl(
			text=[("class:header", f"Link: {link_path}\n")]
		),
		height=1,
	)

	footer = Window(
		content=FormattedTextControl(
			text=[("class:footer", "Press [Enter] to accept or save, [Escape] to cancel")]
		),
		height=1,
	)

	completer = FuzzyPathCompleter(config_completer_match.value, config_case_sensitive.value)

	textarea = TextArea(
		text=target,
		lexer=PathLexer(),
		completer=completer,
		multiline=False,
		focus_on_click=True,
	)

	# Position cursor at start of non-existing part
	textarea.buffer.cursor_position = index_broken_part(target)

	frame = Frame(
		body=textarea,
		title="Target",
		style="class:frame",
	)

	def update_frame_style() -> None:
		text = textarea.text
		if text and Path(text).exists():
			style_dict['frame.border'] = style_dict['existing']
			style_dict['frame.label'] = style_dict['existing']
		else:
			style_dict['frame.border'] = style_dict['nonexistent']
			style_dict['frame.label'] = style_dict['nonexistent']

		app.style = Style.from_dict(style_dict)

	def open_menu() -> None:
		textarea.buffer.start_completion()

	textarea.buffer.on_text_changed.add_handler(lambda _: update_frame_style())
	textarea.buffer.on_text_changed.add_handler(lambda _: open_menu())

	# --- Layout ---

	float_container = FloatContainer(
		content = HSplit([frame, Window(height=Dimension(weight=1))]),
		floats = [
			Float(
				xcursor = True,  # position the menu where the cursor is instead of centering it
				ycursor = True,  # position the menu where the cursor is instead of centering it
				content = CompletionsMenu(
					scroll_offset = 1,  # scroll if the cursor gets closer than this number of lines to the edge
				),
			)
		],
	)

	root_container = HSplit([
		header,
		float_container,
		Window(height=1),
		footer,
	])

	style_dict = {
		"header": "fg:#888888",
		"footer": "fg:#888888",
		"existing": "fg:green",
		"nonexistent": "fg:red",
		"frame.border": "fg:ansiblue",
		"frame.label": "fg:ansiblue bold",
	}

	# --- Key bindings ---
	kb = KeyBindings()

	@kb.add("enter")
	def _(event: KeyPressEvent) -> None:
		"""Save and exit."""
		buff = event.app.current_buffer
		if buff.complete_state:
			# The completions menu is open
			if os.path.isdir(textarea.text):
				# Enter the currently selected directory
				buff.insert_text(os.path.sep)
			elif buff.complete_state.current_completion:
				buff.apply_completion(buff.complete_state.current_completion)
			else:
				buff.cancel_completion()
			return

		new_target = textarea.text
		event.app.exit(result=new_target)

	@kb.add("escape")
	def _(event: KeyPressEvent) -> None:
		"""Cancel without saving."""
		buff = event.app.current_buffer
		if buff.complete_state:
			# The completions menu is open
			buff.cancel_completion()
		else:
			event.app.exit(result=None)

	@kb.add("c-c")
	def _(event: KeyPressEvent) -> None:
		"""Cancel without saving."""
		event.app.exit(result=None)

	# --- Application ---
	app: 'Application[str|None]' = Application(
		layout=Layout(root_container, focused_element=textarea),
		key_bindings=kb,
		style=Style.from_dict(style_dict),
		full_screen=True,
	)
	set_timeouts(app)
	try:
		title = config_title.value.format(link=FPath(link), target=FPath(target))
	except Exception as e:
		print_or_display_in_window("Invalid value for %s: %r\n%s" % (config_title.key, config_title.value, e))
		exit(1)
	app.output.set_title(title)

	update_frame_style()
	new_target = app.run()

	# --- After exit ---
	if new_target is None:
		print_or_display_in_window("Cancelled.")
		return

	try:
		# Write to a tmp link first to not corrupt the real link in case something goes wrong.
		tmp = link_path.parent / (link_path.name + ".tmp_symlink")
		if tmp.exists() or tmp.is_symlink():
			tmp.unlink()
		os.symlink(new_target, tmp)
		tmp.replace(link_path)
		print_or_display_in_window(f"Updated {link_path} → {new_target}")
	except OSError as e:
		print_or_display_in_window(f"Error updating symlink: {e}")
		exit(1)


if __name__ == '__main__':
	main()
