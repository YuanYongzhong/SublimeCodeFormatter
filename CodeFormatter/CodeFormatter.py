import sublime
import sublime_plugin
import subprocess
import os.path as path

class AutoCodeFormatter(sublime_plugin.EventListener):

	def load_settings(self):
		'''Load settings from file.'''
		settings = sublime.load_settings('CodeFormatter.sublime-settings')
		self.formatters = settings.get('formatters')
		self.format_on_save = False

		if settings.get('format_on_save', False) == "True":
			self.format_on_save = True


	def on_pre_save(self, view):
		'''Format before saving.

		When the document is saved check if format_on_save is True. If
		so, check if the file extension is known and if known run format
		command.
		'''

		self.load_settings()

		if self.format_on_save:
			file_extension = view.file_name()
			file_extension = file_extension[file_extension.rfind("."):]

			if file_extension in self.formatters:
				view.window().run_command("codeformatter")


class CodeformatterCommand(sublime_plugin.TextCommand):

	def load_settings(self):
		'''Load settings from file.'''
		settings = sublime.load_settings('CodeFormatter.sublime-settings')
		self.formatters = settings.get('formatters')


	def format_file(self, args):
		'''Start a subproces with the given args and return the output'''
		popen = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
		popen.wait()
		return popen.stdout.read().decode("utf-8")


	def run(self, edit):
		'''Format code.

		First there is a check if the file extension is known. If so the
		args for this file extension will be stored from the settings.
		Then the subprocess is started with the file location and args.
		the result is used to replace all the text in the file.
		'''
		self.load_settings()

		region = sublime.Region(0, self.view.size())
		file_name = self.view.file_name()

		file_extension = file_name
		file_extension = file_extension[file_extension.rfind('.'):]

		if file_extension in self.formatters:
			parser = self.formatters[file_extension]

			if 'args' in parser.keys():
				args = parser['args'].split(',')
			else:
				args = ''

			args = (parser['parser'], args, file_name)

			parsed_content = self.format_file(args)

			self.view.replace(edit, region, parsed_content)

		else:
			print('Formatter for "{0}"" file not defined.'.format(file_extension))
