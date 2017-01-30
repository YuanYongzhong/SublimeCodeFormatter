import shlex 
import subprocess 
import tempfile 
import re 
import os 
import os.path as path 
 
import sublime 
import sublime_plugin 
 
 
class AutoCodeFormatter(sublime_plugin.EventListener): 
 
    def load_settings(self): 
        '''Load settings from file.''' 
        settings = sublime.load_settings('CodeFormatter.sublime-settings') 
 
        # Formatters is made lowercase so user input can be case 
        # insensitive. 
        self.formatters = dict((k.lower(), v) 
                               for k, v in settings.get('formatters', {}).items()) 
        self.format_on_save = settings.get('format_on_save', False) 
        self.verbose = settings.get('verbose', 0) 
 
    def get_syntax(self, view): 
        '''Get the file syntax from Sublime. 
 
        The function uses a regex to get the syntax name and returns it] 
        in lower case. This so the user input can be case insensitive 
        later on. 
        ''' 
        syntax = view.settings().get('syntax') 
        syntax = re.search('Packages\/.+\/(.+)\.sublime-syntax', syntax) 
        return syntax.group(1).lower() 
 
    def on_pre_save(self, view): 
        '''Format before saving. 
 
        When the document is saved check if format_on_save is True. If 
        so, check if the file extension is known and if known run format 
        command. 
        ''' 
        self.load_settings() 
 
        if self.format_on_save == True: 
            if self.verbose >= 2: 
                print('SublimeCodeFormatter: Formatting on save') 
            syntax = self.get_syntax(view) 
 
            if syntax in self.formatters: 
                view.window().run_command('codeformatter') 
            else: 
                if self.verbose >= 2: 
                    print('SublimeCodeParser: Formatter for "{0}" file not defined.'.format( 
                        syntax)) 
 
 
class CodeformatterCommand(sublime_plugin.TextCommand): 
 
    def load_settings(self): 
        '''Load settings from file.''' 
        settings = sublime.load_settings('CodeFormatter.sublime-settings') 
 
        # Formatters is made lowercase so user input can be case 
        # insensitive. 
        self.formatters = dict((k.lower(), v) 
                               for k, v in settings.get('formatters').items()) 
        self.verbose = settings.get('verbose', 0) 
 
    def format_file(self, args): 
        '''Start a subproces with the given args and return the output.''' 
        popen = subprocess.Popen( 
            args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        out, err = popen.communicate() 
 
        if err != b'': 
            # Print if something went wrong 
            if self.verbose >= 1: 
                print('SublimeCodeFormatter: {0}'.format(err)) 
            return False 
 
        return out.decode().replace('\r', ' ') 
 
    def make_temp_file(self, region): 
        '''Create a temp file to use while formatting. 
 
        The temp file will not be deleted when closed so the formatters 
        can work with it. Later on it will be deleted by the run 
        function. 
        ''' 
 
        f = tempfile.NamedTemporaryFile(delete=False) 
        content = self.view.substr(region) 
        f.write(content.encode('utf-8')) 
        f.close() 
        return f.name 
 
    def get_syntax(self): 
        '''Get the file syntax from Sublime. 
 
        The function uses a regex to get the syntax name and returns it] 
        in lower case. This so the user input can be case insensitive 
        later on. 
        ''' 
        syntax = self.view.settings().get('syntax') 
        syntax = re.search('Packages\/.+\/(.+)\.sublime-syntax', syntax) 
        return syntax.group(1).lower() 
 
    def run(self, edit): 
        '''Format code. 
 
        First there is a check if the file syntax is known. If so the 
        args for this file extension will be loaded from the settings. 
        Then a tempfile will be made with the unsaved content of the 
        file that will be formatted. Then the subprocess is started with 
        the temp file location and args. The result is used to replace 
        the content of the original file. Finally the temp file will be 
        removed. 
        ''' 
        self.load_settings() 
 
        region = sublime.Region(0, self.view.size()) 
        file_name = self.view.file_name() 
 
        if file_name: 
            print('SublimeCodeFormatter: Formatting {0}'.format(file_name)) 
            syntax = self.get_syntax() 
 
            if syntax in self.formatters: 
                file_name = self.make_temp_file(region) 
 
                parser = self.formatters[syntax] 
 
                args = shlex.split(parser) + [file_name] 
 
                parsed_content = self.format_file(args) 
 
                if parsed_content != False: 
                    self.view.replace(edit, region, parsed_content) 
 
                os.unlink(file_name) 
 
            else: 
                if self.verbose >= 1: 
                    print('SublimeCodeParser: Formatter for "{0}" file not defined.'.format( 
                        syntax)) 
 
        else: 
            if self.verbose >= 1: 
                print("SublimeCodeParser: No File selected") 
