import sublime
import sublime_plugin
import subprocess
import os.path as path

class AutoCodeFormatter(sublime_plugin.EventListener):

	def load_settings(self):
		settings = sublime.load_settings('CodeFormatter.sublime-settings')
		self.parsers = settings.get('parsers')
		self.format_on_save = False

		if settings.get('format_on_save', False) == "True":
			self.format_on_save = True


	def on_pre_save(self, view):
		self.load_settings()

		if self.format_on_save:
			file_extension = view.file_name()
			file_extension = file_extension[file_extension.rfind("."):]

			if file_extension in self.parsers:
				view.window().run_command("codeformatter")


class CodeformatterCommand(sublime_plugin.TextCommand):

	def load_settings(self):
		settings = sublime.load_settings('CodeFormatter.sublime-settings')
		self.parsers = settings.get('parsers')


	def format_file(self, args):
		popen = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
		popen.wait()
		return popen.stdout.read().decode("utf-8")


	def run(self, edit):
		self.load_settings()

		region = sublime.Region(0, self.view.size())
		file_name = self.view.file_name()

		file_extension = file_name
		file_extension = file_extension[file_extension.rfind('.'):]

		if file_extension in self.parsers:
			parser = self.parsers[file_extension]

			if 'args' in parser.keys():
				args = parser['args'].split(',')
			else:
				args = ''

			args = (parser['parser'], args, file_name)

			parsed_content = self.format_file(args)

			self.view.replace(edit, region, parsed_content)

		else:
			print('Formatter for "{0}"" file not defined.'.format(file_extension))
