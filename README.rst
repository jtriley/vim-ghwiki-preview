vim-ghwiki-preview
==================

:Author: Justin Riley <justin.t.riley@gmail.com>
:License: GPL
:Homepage: https://github.com/jtriley/vim-ghwiki-preview

A `pathogen`_-friendly vim plugin that renders a preview of the current buffer
using an existing wiki on github. The current buffer must be a markup file
(rst, markdown, textile, and the rest that gollum supports).

To install with pathogen::

        cd ~/.vim/bundle
        git clone git://github.com/jtriley/vim-ghwiki-preview.git
        cd vim-ghwiki-preview
        git submodule init
        git submodule update

If you're not using `pathogen`_ (why aren't you using `pathogen`_?)::

        git clone git://github.com/jtriley/vim-ghwiki-preview.git
        mkdir ~/.vim/plugin
        cd ~/.vim/plugin
        cp ~/vim-ghwiki-preview/plugin/ghwikipreview.vim .
        git clone git://github.com/jtriley/py-github.git
        cd py-github
        git checkout -t -b fix-src-layout origin/fix-src-layout

Then you must set the following variable some where in your ~/.vimrc::

        let ghwiki_preview_repo = "youruser/repo"

NOTE: *ghwiki_preview_repo* must have a git-backed wiki enabled otherwise the
plugin won't work

Once that's set you can use the following command in normal mode to preview the
markup in the current buffer on github::

        :python ghwiki_preview_buffer()

.. _pathogen: https://github.com/tpope/vim-pathogen
