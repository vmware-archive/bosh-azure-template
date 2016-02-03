#!/usr/bin/env python
import yaml
import urllib2
import tempfile
import zipfile
import re
import subprocess, os, sys

from jinja2 import Template
from subprocess import call
from subprocess import Popen, PIPE

from Utils.WAAgentUtil import waagent
import Utils.HandlerUtil as Util

def authorizedPost(url, token):
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token {0}".format(token))
    req.add_header("Accept", "application/json")
    req.data = ''

    res = urllib2.urlopen(req)
    return res

# Get settings from CustomScriptForLinux extension configurations
waagent.LoggerInit('/var/log/waagent.log', '/dev/stdout')
hutil =  Util.HandlerUtility(waagent.Log, waagent.Error, "bosh-deploy-script")
hutil.do_parse_context("enable")
settings = hutil.get_public_settings()

username = settings["username"]
home_dir = os.path.join("/home", username)
install_log = os.path.join(home_dir, "install.log")

# Unbuffer output to install_log
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

tee = subprocess.Popen(["tee", "-a", install_log], stdin=subprocess.PIPE)
os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

os.environ["HOME"] = home_dir

# deploy director
os.environ["BOSH_INIT_LOG_LEVEL"] = 'INFO'
os.environ["BOSH_INIT_LOG_PATH"] = './bosh-init-debug.log'

# do we have a targeted bosh?
p = Popen(['bosh', 'target'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate()

# assume if no bosh is target, there is no director
if "Target not set" in err:

    res = None

    while res != 0:
        res = call("bosh-init deploy ./bosh/bosh.yml", shell=True)

    p = Popen(['bosh', 'target', '10.0.0.4'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"admin\r\nadmin\r\n")
    rc = p.returncode

# change owner for bosh.yaml
call("chown -R {0} {1}/.bosh_config".format(username, home_dir), shell=True)

# load manifests in to memory
f = open('./manifests/index.yml')
manifests = yaml.safe_load(f)
f.close()

# run bosh status and get the id back to inject in to manifests
p = Popen(['bosh', 'status', '--uuid'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
bosh_uuid, err = p.communicate()

# set the director id on the manifests
for m in manifests['manifests']:
    with open ("./manifests/".format(m['file']), 'r+') as f:

        contents = f.read()
        template = Template(contents)
        contents = template.render(DIRECTOR_UUID=bosh_uuid)

        f.seek(0)
        f.write(contents)
        f.trucate()
        f.close()

pivnetAPIToken = settings["pivnet-api-token"]

eula_urls = ["https://network.pivotal.io/api/v2/products/{0}/releases/{1}/eula_acceptance".format(m['release-name'], m['release-number'])
    for m in manifests['manifests']]

release_urls = ["https://network.pivotal.io/api/v2/products/{0}/releases/{1}/product_files/{2}/download".format(m['release-name'], m['release-number'], m['file-number'])
    for m in manifests['manifests']]

stemcell_urls = [m['stemcell'] for m in manifests['manifests']]

# accept eula for each product
for url in eula_urls:
    res = authorizedPost(url, pivnetAPIToken)
    code = res.getcode()

# releases
is_release_file = re.compile("^releases\/.+")
call("mkdir -p /tmp/releases", shell=True)

print "Processing releases."

for url in release_urls:

    print "Downloading {0}.".format(url)

    res = authorizedPost(url, pivnetAPIToken)
    code = res.getcode()

    length = int(res.headers["Content-Length"])

    # content-length
    if code is 200:

        total = 0
        pcent = 0.0
        CHUNK = 16 * 1024

        with tempfile.TemporaryFile() as temp:
            while True:
                chunk = res.read(CHUNK)
                total += CHUNK
                pcent = (float(total) / float(length)) * 100

                sys.stdout.write("Download progress: %.2f%% (%.2fM)\r" % (pcent, total / 1000000.0) )
                sys.stdout.flush()

                if not chunk: break
                temp.write(chunk)

            print "Download complete."

            z = zipfile.ZipFile(temp)
            for name in z.namelist():

                # is this a release?
                if is_release_file.match(name):

                    release_filename = "/tmp/{0}".format(name)

                    print "Unpacking {0}.".format(name)
                    z.extract(name, "/tmp")

                    # upload the file with bosh
                    print "Uploading release {0} to BOSH director.".format(name)
                    call("bosh upload release {0}".format(release_filename), shell=True)

                    os.unlink(release_filename)

            z.close()
            temp.close()

# stemcells
print "Processing stemcells."

for url in stemcell_urls:
    print "Processing stemcell {0}".format(url)
    call("bosh upload stemcell {0}".format(url), shell=True)

# deploy!
for m in manifests['manifests']:
    call("bosh deployment {0}".format("./manifests/".format(m['file']), shell=True)
    call("bosh deploy -n", shell=True)
