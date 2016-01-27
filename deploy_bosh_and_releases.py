#!/usr/bin/env python
import os
from subprocess import call

home_dir = os.environ["HOME"]
install_log = os.path.join(home_dir, "install.log")

# deploy director
os.environ["BOSH_INIT_LOG_LEVEL"] = 'INFO'
os.environ["BOSH_INIT_LOG_PATH"] = './bosh-init-debug.log'

call("bosh-init deploy bosh.yml", shell=True)
