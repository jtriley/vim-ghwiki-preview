if !has('python')
    echo "Error: VIM must be compiled with +python"
    finish
endif

python << endpython
import os
import sys
import vim

# add this script's parent folder to vim's PYTHONPATH.
# python deps live there (e.g. ghwiki)
parentdir = os.path.dirname(vim.eval('expand("<sfile>")'))
if parentdir not in sys.path:
    sys.path.insert(0, parentdir)
# add py-github source folder containing github package to vim's PYTHONPATH.
pygithubsrc = os.path.join(parentdir, 'py-github')
if pygithubsrc not in sys.path:
    sys.path.insert(0, pygithubsrc)

from ghwiki import *
endpython
