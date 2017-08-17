from CMakeBuilder.generators import CMakeGenerator
from CMakeBuilder.generators.windows.support.vcvarsall import query_vcvarsall
import os
import sublime
import subprocess

class MinGW(CMakeGenerator):

    def __repr__(self):
        return 'CodeBlocks - MinGW Makefiles'

    def syntax(self):
        return 'Packages/CMakeBuilder/Syntax/Make.sublime-syntax'

    def file_regex(self):
        return r'(.+[^:]):(\d+):(\d+): (?:fatal )?((?:error|warning): .+)$'

    def variants(self):
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        lines = subprocess.check_output(
            'cmake --build . --target help', 
            cwd=self.build_folder, 
            startupinfo=startupinfo).decode('utf-8').splitlines()

        variants = []
        EXCLUDES = [
            'are some of the valid targets for this Makefile:',
            'All primary targets available:', 
            'depend',
            'all (the default if no target is provided)',
            'help', 
            'edit_cache', 
            '.ninja', 
            '.o',
            '.i',
            '.s']
            
        for target in lines:
            try:
                if any(exclude in target for exclude in EXCLUDES): 
                    continue
                target = target[4:]
                name = target
                if (self.filter_targets and 
                    not any(f in name for f in self.filter_targets)):
                    continue
                shell_cmd = 'cmake --build . --target {}'.format(target)
                variants.append({'name': name, 'shell_cmd': shell_cmd})
            except Exception as e:
                sublime.error_message(str(e))
                # Continue anyway; we're in a for-loop
        return variants
        
