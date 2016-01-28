#!/usr/bin/env python
import os
import yaml
from subprocess import call
from subprocess import Popen, PIPE

from Utils.WAAgentUtil import waagent
import Utils.HandlerUtil as Util

# Get settings from CustomScriptForLinux extension configurations
waagent.LoggerInit('/var/log/waagent.log', '/dev/stdout')
hutil =  Util.HandlerUtility(waagent.Log, waagent.Error, "bosh-deploy-script")
hutil.do_parse_context("enable")
settings = hutil.get_public_settings()

username = settings["username"]
home_dir = os.path.join("/home", username)
install_log = os.path.join(home_dir, "install.log")

os.environ["HOME"] = home_dir

# deploy director
os.environ["BOSH_INIT_LOG_LEVEL"] = 'INFO'
os.environ["BOSH_INIT_LOG_PATH"] = './bosh-init-debug.log'

# do we have a targeted bosh?
p = Popen(['bosh', 'target'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
output, err = p.communicate()

# assume if no bosh is target, there is no director
if "Target not set" in err:
    call("bosh-init deploy ./bosh/bosh.yml", shell=True)

    p = Popen(['bosh', 'target', '10.0.0.4'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate(b"admin\r\nadmin\r\n")
    rc = p.returncode

# load manifests in to memory
f = open('./manifests/index.yml')
manifests = yaml.safe_load(f)
f.close()

# process releases
#m_list = []
#for m in manifests['manifests']:
#    m_list.append("manifests/{0}".format(m['file']))

#m_list.append('bosh.yml')
