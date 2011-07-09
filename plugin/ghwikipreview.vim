if !has('python')
    echo "Error: VIM must be compiled with +python"
    finish
endif

python << endpython
import os
import sys
import vim
import urllib2
import webbrowser

# get the directory this script is in: the py-github module should be installed there.
scriptdir = os.path.join(os.path.dirname(vim.eval('expand("<sfile>")')), 'py-github')
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)

from github import github

REPO_ERROR = ''

def get_preview_url():
    wiki_repo_defined = int(vim.eval("exists('g:ghwiki_preview_repo')"))
    if not wiki_repo_defined:
        REPO_ERROR = "please set ghwiki_preview_repo in your ~/.vimrc"
        return
    wiki_repo = vim.eval("g:ghwiki_preview_repo")
    if len(wiki_repo.split('/')) != 2:
        REPO_ERROR = "invalid ghwiki_preview_repo set, must have the form: 'user/repo'"
        return
    user, repo = wiki_repo.split('/')
    gh = github.GitHub()
    try:
        repo_exists = gh.repos.show(user, repo)
        if not repo_exists.has_wiki:
            REPO_ERROR = "repo %s does not have a git-backed wiki enabled" % repo
            return
    except urllib2.HTTPError:
        REPO_ERROR = "repo %s does not exist" % wiki_repo
        return
    return 'https://github.com/%s/%s/wiki/_preview' % (user, repo)

URL = get_preview_url()
FORMATS_AND_EXTENSIONS = {'.asciidoc': 'asciidoc',
                          '.creole': 'creole',
                          '.org': 'org',
                          '.pod': 'pod',
                          '.rdoc': 'rdoc',
                          '.textile': 'textile'}
FORMATS_AND_EXTENSIONS.update(dict.fromkeys(['.rest.txt', '.rst.txt', '.rest', '.rst'], 'rest'))
FORMATS_AND_EXTENSIONS.update(dict.fromkeys(['.mediawiki', '.wiki'], 'mediawiki'))
FORMATS_AND_EXTENSIONS.update(dict.fromkeys(['.markdown', '.mdown', '.mkdn', '.mkd', '.md'], 'markdown'))


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
    result = urllib2.urlopen(url, data=params_quoted).read()
    with open('/tmp/delete.html', 'w') as htmlfile:
            htmlfile.write(result)
            webbrowser.open_new_tab(htmlfile.name)
endpython
