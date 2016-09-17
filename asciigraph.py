import sublime
import sublime_plugin
import os
import subprocess
import locale
from os.path import dirname, realpath
# Thanks to Pandoc Project, some codes are borrowed there.

isWindows = sublime.platform() == 'windows'

class AsciiGraphRegionCommand(sublime_plugin.WindowCommand):
    def is_enable(self):
        return True

    def run(self):
        binary_name = "graph-easy"
        graph_easy = _find_binary(binary_name, _s("Binary Path"))
        current_view = self.window.active_view()
        selection_text = ""
        for region in current_view.sel():
            selection_text += current_view.substr(region)
        if graph_easy is None:
            return

        if isWindows:
            selection_text = selection_text.encode('UTF-8').decode(locale.getpreferredencoding())

        # Fix echo command extra double quotes on Windows platform
        echo = dirname(realpath(__file__)) + '/echo.exe' if isWindows else 'echo'
        cmd_1 = [echo, selection_text]
        cmd_2 = [graph_easy]
        process_1 = subprocess.Popen(cmd_1,
                                     shell=False,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        process_2 = subprocess.Popen(cmd_2,
                                     shell=False,
                                     stdin=process_1.stdout,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        result, error = process_2.communicate()
        if error:
            sublime.error_message('\n\n'.join([
                'Error when running:',
                ' '.join(cmd_2),
                error.decode('utf-8').strip()]))
            return
        result_str = result.decode('utf-8')
        if isWindows:
            result_str = result_str.replace('\r', '')  # Remove CR
        new_view = self.window.new_file()
        new_view.run_command("insert_snippet", {"contents":
                                                result_str})


class AsciiGraphFileCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return True

    def run(self):
        binary_name = "graph-easy"
        graph_easy = _find_binary(binary_name, _s("Binary Path"))
        graph_source = self.window.active_view().file_name()
        if graph_easy is None:
            return
        cmd = [graph_easy, graph_source]
        process = subprocess.Popen(cmd,
                                   shell=False,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        result, error = process.communicate()
        if error:
            sublime.error_message('\n\n'.join([
                'Error when running:',
                ' '.join(cmd),
                error.decode('utf-8').strip()]))
            return
        result_str = result.decode('utf-8')
        if isWindows:
            result_str = result_str.replace('\r', '')  # Remove CR
        new_view = self.window.new_file()
        new_view.run_command("insert_snippet", {"contents":
                                                result_str})


def _find_binary(name, default=None):
    '''Returns a configure path or looks for an executable on the system path.
    '''

    if default is not None:
        if os.path.exists(default):
            return default
        msg = 'configured path for {0} {1} not found.'.format(name, default)
        sublime.error_message(msg)
        return None

    for dirname in os.environ['PATH'].split(os.pathsep):
        path = os.path.join(dirname, name)
        print(path)
        if os.path.exists(path):
            return path.replace('\\', '/') + '.bat' if isWindows else path

    sublime.error_message('Could not find graph-easy executable on PATH.')
    return None


def _s(key):
    '''Convenience function for getting the setting dict.'''
    return sublime.load_settings("Asciigraph.sublime-settings").get(key)

