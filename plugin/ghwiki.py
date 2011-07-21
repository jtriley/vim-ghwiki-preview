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


class BackgroundBrowser(webbrowser.GenericBrowser):
    """
    Class for all browsers which are to be started in the background.

    (same as BackgroundBrowser included in webbrowser module except pipe stdout
    in order to keep the browser's output from cluttering the vim buffer)
    """
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


class GHWikiPreview(object):

    _err = ''
    _url = None

    @property
    def url(self):
        if not self._url:
            self._url = self._get_preview_url()
        return self._url

    def _get_preview_url(self):
        wiki_repo_defined = int(vim.eval("exists('g:ghwiki_preview_repo')"))
        if not wiki_repo_defined:
            self._err = "please set ghwiki_preview_repo in your ~/.vimrc"
            return
        wiki_repo = vim.eval("g:ghwiki_preview_repo")
        if len(wiki_repo.split('/')) != 2:
            self._err = "invalid ghwiki_preview_repo set, "
            self._err += "must have the form: 'user/repo'"
            return
        user, repo = wiki_repo.split('/')
        gh = github.GitHub()
        try:
            repo_exists = gh.repos.show(user, repo)
            if not repo_exists.has_wiki:
                self._err = "repo %s does not have a git-backed wiki enabled"
                self._err = self._err % repo
                return
        except urllib2.HTTPError:
            self._err = "repo %s does not exist" % wiki_repo
            return
        except urllib2.URLError:
            self._err = "no internet connection available"
            return
        return 'https://github.com/%s/%s/wiki/_preview' % (user, repo)

    def _build_and_quote_params(self, paramdict):
        params = []
        for key in paramdict:
            params.append('wiki[%s]=%s' % (key, paramdict.get(key)))
        return urllib2.quote('&'.join(params), safe='=&')

    def _print_err(self, msg):
        print '!!! ERROR (ghwiki-preview): %s' % msg

    def ghwiki_preview_buffer(self):
        buf = vim.current.buffer
        bufname = os.path.basename(buf.name)
        bufext = os.path.splitext(buf.name)[-1]
        bufformat = FORMATS_AND_EXTENSIONS.get(bufext)
        if bufformat is None:
            return self._print_err("unsupported file extension '%s'" % bufext)
        if not self.url:
            msg = self._err or 'error occured while fetching preview'
            return self._print_err(msg)
        params = dict(name=bufname, format=bufformat, body='\n'.join(buf))
        params_quoted = self._build_and_quote_params(params)
        html = urllib2.urlopen(self.url, data=params_quoted).read()
        self.show_preview(html)

    def _is_exe(self, fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    def _which(self, program):
        fpath, fname = os.path.split(program)
        if fpath:
            if self._is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if self._is_exe(exe_file):
                    return exe_file

    def open_browser(self, url):
        # get 'default' browser from webbrowser module
        browser_cmd = webbrowser.get().name
        browser_defined = int(vim.eval("exists('g:ghwiki_preview_browser')"))
        if browser_defined:
            browser_cmd = vim.eval("g:ghwiki_preview_browser")
        cmd = shlex.split(browser_cmd)
        arg0 = cmd[0]
        if not self._which(arg0):
            raise Exception("browser %s does not exist" % arg0)
        if "%s" not in browser_cmd:
            cmd.append("%s")
        browser = BackgroundBrowser(cmd)
        browser.open(url)

    def show_preview(self, html):
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
            self.open_browser(previewurl)
            server.handle_request()
        except Exception, e:
            print e

_obj = GHWikiPreview()

ghwiki_preview_buffer = _obj.ghwiki_preview_buffer
