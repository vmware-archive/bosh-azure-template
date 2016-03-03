#!/usr/bin/env python
import urllib2
import json
import apt
import tarfile
import sys

from distutils import dir_util
from os import chdir
from os import symlink
from subprocess import call

# install packages
package_list = [
    "python-pip",
    "build-essential",
    "tmux",
    "ruby2.0",
    "ruby2.0-dev",
    "libxml2-dev",
    "libsqlite3-dev",
    "libxslt1-dev",
    "libpq-dev",
    "libmysqlclient-dev",
    "zlibc",
    "zlib1g-dev",
    "openssl",
    "libxslt1-dev",
    "libssl-dev",
    "libreadline6",
    "libreadline6-dev",
    "libyaml-dev",
    "sqlite3",
    "libffi-dev"]

print "Updating apt cache"
cache = apt.cache.Cache()
cache.update(raise_on_error=False)
cache.open(None)

for package in package_list:
    pkg = cache[package]

    if not pkg.is_installed:
        pkg.mark_install(auto_inst=True)

try:
    cache.commit()
except Exception as arg:
    print >> sys.stderr, "Sorry, package installation failed [{err}]".format(
        err=str(arg))

import pip

pip_packages = ['jinja2', 'azure', 'azure-mgmt', 'click']
for package in pip_packages:
    pip.main(['install', package])

gh_url = 'https://api.github.com/repos/cf-platform-eng/bosh-azure-template/releases/latest'

req = urllib2.Request(gh_url)
headers = req.headers = {
    'Content-Type': 'application/json'
}

# upload the release asset
handler = urllib2.urlopen(req)
release = json.loads(handler.read())

release_url = release['assets'][0]['browser_download_url']
res = urllib2.urlopen(release_url)

code = res.getcode()
length = int(res.headers["Content-Length"])

# content-length
if code is 200:

    CHUNK = 16 * 1024
    filename = '/tmp/archive.tgz'

    with open(filename, 'wb') as temp:
        while True:
            chunk = res.read(CHUNK)

            if not chunk:
                break
            temp.write(chunk)

        print "Download complete."

    tfile = tarfile.open(filename, 'r:gz')
    tfile.extractall(".")

dir_util.copy_tree(".", "../..")
symlink('/usr/local/lib/python2.7/dist-packages/azure/mgmt', '../../azure/mgmt')

chdir("../..")

index_file = "index-{0}.yml".format(sys.argv[1].lower())
gamma_cmd = "./gamma.py --index {0}".format(index_file)

# start tmux, running deploy_bosh_and_releases
call("tmux new -d -s shared '{0}'".format(gamma_cmd), shell=True)
call("./gotty -c gamma:{0} -t --tls-crt '.gotty.crt' --tls-key '.gotty.key' -p '443' tmux attach -d -t shared &".format(sys.argv[2]), shell=True)
