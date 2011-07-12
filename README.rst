vim-ghwiki-preview
==================

:Author: Justin Riley <justin.t.riley@gmail.com>
:License: GPL
:Homepage: https://github.com/jtriley/vim-ghwiki-preview

A `pathogen`_-friendly vim plugin that renders a preview of the current buffer
using an existing wiki on github. The current buffer must be a markup file
(rst, markdown, textile, and the rest that gollum supports).

Installation
------------

**NOTE**: This plugin requires VIM compiled with **python+** support

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

After you've installed the plugin you need to specify a git-backed-wiki-enabled
github repo in your ~/.vimrc::

        let ghwiki_preview_repo = "youruser/repo"

The vim-ghwiki-preview plugin uses this repo to render the previews.

**NOTE**: *ghwiki_preview_repo* must have a git-backed wiki enabled otherwise the
plugin won't work

Usage
-----
To use the plugin you must first be editing a file in VIM with one of the
following formats/extensions:

+-----------+---------------------------------+
| Format    | Extension                       |
+===========+=================================+
| rest      | .rest.txt .rst.txt .rest .rst   |
+-----------+---------------------------------+
| markdown  | .markdown .mdown .mkdn .mkd .md |
+-----------+---------------------------------+
| textile   | .textile                        |
+-----------+---------------------------------+
| mediawiki | .mediawiki .wiki .mediawiki     |
+-----------+---------------------------------+
| asciidoc  | .asciidoc                       |
+-----------+---------------------------------+
| creole    | .creole                         |
+-----------+---------------------------------+
| org       | .org                            |
+-----------+---------------------------------+
| pod       | .pod                            |
+-----------+---------------------------------+
| rdoc      | .rdoc                           |
+-----------+---------------------------------+

Assuming you have one of the formats/extensions loaded into a buffer you can
then display a github wiki preview in a web browser using::

        <leader><leader>g

Changing the Default Keybinding
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you'd rather use a different keybinding you can specify it in your ~/.vimrc
using the *ghwiki_preview_keybinding* variable. For example, to change the
keybinding to *<leader>g*::

        let ghwiki_preview_keybinding = "<leader>g"

You can also manually run the plugin using the following command in normal mode::

        :python ghwiki_preview_buffer()

Changing the Default Web Browser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

vim-ghwiki-preview uses the `webbrowser`_ module in the standard Python library
to launch a web-browser and display the github wiki preview. The `webbrowser`_
module will try to automatically launch the best browser for your platform. If
you'd like to use a different browser other than the default chosen by
`webbrowser`_, set the following in your ~/.vimrc::

        let ghwiki_preview_browser = "chromium"

You can also specify additional browser arguments and options::

        let ghwiki_preview_browser = 'open -a "Google Chrome" %s'

In the above example *%s* will be replaced by the plugin with the url to the
local preview page.

.. _pathogen: https://github.com/tpope/vim-pathogen
.. _webbrowser: http://docs.python.org/library/webbrowser.html
