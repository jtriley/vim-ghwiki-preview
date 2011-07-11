#!/usr/bin/env python
import os
import vim
import urllib2
import tempfile
import webbrowser

from github import github

REPO_ERROR = ''

FORMATS_AND_EXTENSIONS = {'.asciidoc': 'asciidoc',
                          '.creole': 'creole',
                          '.org': 'org',
                          '.pod': 'pod',
                          '.rdoc': 'rdoc',
                          '.textile': 'textile'}
FORMATS_AND_EXTENSIONS.update(
    dict.fromkeys(['.rest.txt', '.rst.txt', '.rest', '.rst'], 'rest'))
FORMATS_AND_EXTENSIONS.update(
    dict.fromkeys(['.mediawiki', '.wiki'], 'mediawiki'))
FORMATS_AND_EXTENSIONS.update(
    dict.fromkeys(['.markdown', '.mdown', '.mkdn', '.mkd', '.md'], 'markdown'))


def get_preview_url():
    wiki_repo_defined = int(vim.eval("exists('g:ghwiki_preview_repo')"))
    if not wiki_repo_defined:
        REPO_ERROR = "please set ghwiki_preview_repo in your ~/.vimrc"
        return
    wiki_repo = vim.eval("g:ghwiki_preview_repo")
    if len(wiki_repo.split('/')) != 2:
        REPO_ERROR = "invalid ghwiki_preview_repo set, "
        REPO_ERROR += "must have the form: 'user/repo'"
        return
    user, repo = wiki_repo.split('/')
    gh = github.GitHub()
    try:
        repo_exists = gh.repos.show(user, repo)
        if not repo_exists.has_wiki:
            REPO_ERROR = "repo %s does not have a git-backed wiki enabled"
            REPO_ERROR = REPO_ERROR % repo
            return
    except urllib2.HTTPError:
        REPO_ERROR = "repo %s does not exist" % wiki_repo
        return
    return 'https://github.com/%s/%s/wiki/_preview' % (user, repo)

URL = get_preview_url()


def _build_and_quote_params(paramdict):
    params = []
    for key in paramdict:
        params.append('wiki[%s]=%s' % (key, paramdict.get(key)))
    return urllib2.quote('&'.join(params), safe='=&')


def ghwiki_preview_buffer():
    if not URL and REPO_ERROR:
        print "!!! ERROR (ghwiki-preview): %s" % REPO_ERROR
        return
    buf = vim.current.buffer
    bufname = os.path.basename(buf.name)
    bufext = os.path.splitext(buf.name)[-1]
    bufformat = FORMATS_AND_EXTENSIONS.get(bufext)
    if bufformat is None:
        print "ghwiki-preview: unsupported file extension '%s'" % bufext
        return
    params = dict(name=bufname, format=bufformat, body='\n'.join(buf))
    params_quoted = _build_and_quote_params(params)
    result = urllib2.urlopen(URL, data=params_quoted).read()
    tmpdir = tempfile.gettempdir()
    slashtemp = os.path.sep + 'tmp'
    if os.path.isdir(slashtemp):
        tmpdir = slashtemp
    outhtml = os.path.join(tmpdir, 'ghwikipreview.html')
    with open(outhtml, 'w') as htmlfile:
        htmlfile.write(result)
        webbrowser.open_new_tab(htmlfile.name)
