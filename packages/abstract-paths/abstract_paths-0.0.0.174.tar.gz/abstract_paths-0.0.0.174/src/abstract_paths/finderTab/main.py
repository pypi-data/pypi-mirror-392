from abstract_utilities import *
kwargs = {'directory': '/home/flerb/Documents/pythonTools/modules/src/modules/abstract_paths/src/abstract_paths/finderTab',
          'get_lines': True,
          'spec_line': False,
          'parse_lines': False,
          'total_strings': False,
          'strings': ['gg'],
          'recursive': True,
          'cfg': define_defaults(allowed_exts={'.py'},
                            exclude_exts={'.pyc'},
                            allowed_types=None,
                            exclude_types=None,
                            allowed_dirs=None,
                            exclude_dirs=None,
                            allowed_patterns=None,
                            exclude_patterns=None,
                            add=False)
          }
result = get_files_and_dirs(**kwargs)
input(result)
from src import startFinderConsole
startFinderConsole()
