from subprocess import call
from os import makedirs
from os import path
from shutil import copy
from jinja2 import Environment
from subprocess import Popen, PIPE


def do_step(context):

    if not path.isdir("bosh/manifests"):
        makedirs("bosh/manifests")

    if not path.isdir("bosh/certs"):
        makedirs("bosh/certs")

    settings = context.meta['settings']

    # Generate the private key and certificate
    call("sh create_cert.sh", shell=True)
    copy("bosh.key", "./bosh/bosh")
    with open('bosh_cert.pem', 'r') as tmpfile:
        ssh_cert = tmpfile.read()
    ssh_cert = "|\n" + ssh_cert
    ssh_cert = "\n        ".join([line for line in ssh_cert.split('\n')])

    settings['SSH_CERTIFICATE'] = ssh_cert
    settings['cf_ip'] = settings['cf-ip']

    # template openssl config
    env = Environment()

    template_path = "certs/openssl.conf"

    with open(template_path, 'r') as f:
        contents = f.read()
        contents = env.from_string(contents).render(settings)

    with open(path.join('bosh', template_path), 'w') as f:
        f.write(contents)

    cf_ip = settings["cf-ip"]
    call("openssl genrsa -out bosh/certs/server.key 2048", shell=True)
    call("openssl req -new -out bosh/certs/sub1.csr -key bosh/certs/server.key -config bosh/certs/openssl.conf -subj \"/C=US/ST=CA/L=San Francisco/O=Pivotal Labs/OU=Platform Engineering/CN={0}.xip.io\"".format(cf_ip), shell=True)
    call("openssl req -text -noout -in bosh/certs/sub1.csr", shell=True)
    call("openssl x509 -req -days 3650 -in bosh/certs/sub1.csr -signkey bosh/certs/server.key -out bosh/certs/sub1.crt -extensions v3_req -extfile bosh/certs/openssl.conf", shell=True)
    call("openssl x509 -in bosh/certs/sub1.crt -text -noout", shell=True)

    p = Popen(['cat', 'bosh/certs/sub1.crt', 'bosh/certs/sub1.csr', 'bosh/certs/server.key'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    settings['ha_proxy_cert'] = output

    return context
