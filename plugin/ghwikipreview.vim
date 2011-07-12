if !has('python')
    echo "Error: VIM must be compiled with +python"
    finish
endif

if exists('g:ghwiki_preview_loaded')
    finish
endif
let g:ghwiki_preview_loaded = 1

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

has_keybinding = int(vim.eval("exists('g:ghwiki_preview_keybinding')"))
keybinding = '<leader><leader>g'
if has_keybinding:
    keybinding = vim.eval("g:ghwiki_preview_keybinding")
vim.command('map %s :python ghwiki_preview_buffer()<CR>' % keybinding)
endpython
