#!/usr/bin/env python
import os
import sys
import vim
import shlex
import urllib2
import webbrowser
import subprocess
import BaseHTTPServer as httpserv

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
    html = urllib2.urlopen(URL, data=params_quoted).read()
    show_preview(html)


class BackgroundBrowser(webbrowser.GenericBrowser):
    """Class for all browsers which are to be started in the background."""
    def open(self, url, new=0, autoraise=1):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 for arg in self.args]
        try:
            if sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
            else:
                setsid = getattr(os, 'setsid', None)
                if not setsid:
                    setsid = getattr(os, 'setpgrp', None)
                p = subprocess.Popen(cmdline, close_fds=True,
                                     preexec_fn=setsid, stdout=subprocess.PIPE)
            return (p.poll() is None)
        except OSError:
            return False


def _is_exe(fpath):
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)


def _which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if _is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if _is_exe(exe_file):
                return exe_file


def open_browser(url):
    # get 'default' browser from webbrowser module
    browser_cmd = webbrowser.get().name
    browser_defined = int(vim.eval("exists('g:ghwiki_preview_browser')"))
    if browser_defined:
        browser_cmd = vim.eval("g:ghwiki_preview_browser")
    cmd = shlex.split(browser_cmd)
    arg0 = cmd[0]
    if not _which(arg0):
        raise Exception("browser %s does not exist" % arg0)
    if "%s" not in browser_cmd:
        cmd.append("%s")
    browser = BackgroundBrowser(cmd)
    browser.open(url)


def show_preview(html):
    class RequestHandler(httpserv.BaseHTTPRequestHandler):
        def do_GET(self):
            bufferSize = 1024 * 1024
            for i in xrange(0, len(html), bufferSize):
                self.wfile.write(html[i:i + bufferSize])
    # create a temporary http server to handle one request
    server = httpserv.HTTPServer(('127.0.0.1', 0), RequestHandler)
    # calls URL to retrieve html from the temporary http server
    previewurl = 'http://127.0.0.1:%s' % server.server_port
    print "Local one-time preview url: %s " % previewurl
    try:
        open_browser(previewurl)
        server.handle_request()
    except Exception, e:
        print e
