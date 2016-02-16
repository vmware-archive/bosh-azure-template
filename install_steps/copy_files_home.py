import os

from subprocess import call
from distutils import dir_util
from shutil import copy

def do_step(context):
    settings = context.meta['settings']

    username = settings["username"]
    home_dir = os.path.join("/home", username)

    # Copy all the files in ./bosh into the home directory
    dir_util.copy_tree("./bosh/", home_dir)
    copy("./manifests/index.yml", "{0}/manifests/".format(home_dir))

    call("chown -R {0} {1}".format(username, home_dir), shell=True)
    call("chmod 400 {0}/bosh".format(home_dir), shell=True)

    return context
