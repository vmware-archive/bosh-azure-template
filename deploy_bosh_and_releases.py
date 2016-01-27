#!/usr/bin/env python
import os
from subprocess import call
from Utils.WAAgentUtil import waagent
import Utils.HandlerUtil as Util

# Get settings from CustomScriptForLinux extension configurations
waagent.LoggerInit('/var/log/waagent.log', '/dev/stdout')

hutil =  Util.HandlerUtility(waagent.Log, waagent.Error, "bosh-all-deploy-script")
hutil.do_parse_context("enable")
settings = hutil.get_public_settings()

username = settings["username"]
home_dir = os.path.join("/home", username)
install_log = os.path.join(home_dir, "install.log")

# deploy director
os.environ["BOSH_INIT_LOG_LEVEL"] = 'INFO'
os.environ["BOSH_INIT_LOG_PATH"] = './bosh-init-debug.log'

call("bosh-init deploy bosh.yml >>{0} 2>&1;".format(install_log))
