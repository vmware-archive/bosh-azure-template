from subprocess import call
from os import makedirs
from os import path
from shutil import copy


def do_step(context):

    if not path.isdir("bosh/manifests"):
        makedirs("bosh/manifests")

    # Generate the private key and certificate
    call("sh create_cert.sh", shell=True)
    copy("bosh.key", "./bosh/bosh")
    with open('bosh_cert.pem', 'r') as tmpfile:
        ssh_cert = tmpfile.read()
    ssh_cert = "|\n" + ssh_cert
    ssh_cert = "\n        ".join([line for line in ssh_cert.split('\n')])

    context.meta['settings']['SSH_CERTIFICATE'] = ssh_cert

    return context
