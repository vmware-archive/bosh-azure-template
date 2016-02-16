#!/usr/bin/env python
import urllib2
import json
import apt
import tarfile
import tempfile
import shutil
import sys

from shutil import copytree
from os import environ
from os import listdir
from os import symlink
from os.path import isfile, join

# install python-pip and it's dependencies...
package_list = ["binutils", "build-essential", "cpp", "cpp-4.8", "dpkg-dev", \
    "fakeroot", "g++", "g++-4.8", "gcc", "gcc-4.8", "libalgorithm-diff-perl", \
    "libalgorithm-diff-xs-perl", "libalgorithm-merge-perl", "libasan0", \
    "libatomic1", "libc-dev-bin", "libc6-dev", "libcloog-isl4", \
    "libdpkg-perl", "libfakeroot", "libfile-fcntllock-perl", "libgcc-4.8-dev", \
    "libgomp1", "libisl10", "libitm1", "libmpc3", "libmpfr4", "libquadmath0", \
    "libstdc++-4.8-dev", "libtsan0", "linux-libc-dev", "make", "manpages-dev", \
    "python-chardet-whl", "python-colorama", "python-colorama-whl", \
    "python-distlib", "python-distlib-whl", "python-html5lib", \
    "python-html5lib-whl", "python-pip", "python-pip-whl", \
    "python-requests-whl", "python-setuptools", "python-setuptools-whl", \
    "python-six-whl", "python-urllib3-whl", "python-wheel", "python3-pkg-resources"]

print "Updating apt cache"
cache = apt.cache.Cache()
cache.update()

for package in package_list:
    pkg = cache[package]

    if not pkg.is_installed:
        pkg.mark_install()

try:
    cache.commit()
except Exception, arg:
    print >> sys.stderr, "Sorry, package installation failed [{err}]".format(err=str(arg))

import pip

pip_packages = ['jinja2', 'azure', 'azure-mgmt', 'click']
for package in pip_packages:
    pip.main(['install', package])

gh_url = 'https://api.github.com/repos/cf-platform-eng/bosh-azure-template/releases/latest'

req = urllib2.Request(gh_url)
headers = req.headers = {
  'Content-Type':'application/json'
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

            if not chunk: break
            temp.write(chunk)

        print "Download complete."

    tfile = tarfile.open(filename, 'r:gz')
    tfile.extractall(".")

copytree('.' '../..')
symlink('/usr/local/lib/python2.7/dist-packages/azure/mgmt', '../../azure/mgmt')
