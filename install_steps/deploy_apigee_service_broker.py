import bosh_client
import os
import yaml
from urllib2 import Request
from urllib2 import urlopen
from urllib import urlencode
import json
from jinja2 import Template
from hashlib import sha256


from subprocess import call


MANIFEST_YAML = """
---
applications:
- name: apigee-cf-service-broker
command: node server.js
services:
- apigee_cf_service_broker-p-redis
buildpack: nodejs_buildpack
env:
  APIGEE_REDIS_PASSPHRASE: {{redis_passphrase}}
  APIGEE_DASHBOARD_URL: {{apigee_dashboard_url}}
  APIGEE_MGMT_API_URL: {{apigee_mgmt_api_url}}
"""

def password(key, sshpubkey, short=False):
    password = sha256("{0}:{1}".format(sshpubkey, key)).hexdigest()
    if short:
        return password[:20]
    else:
        return password


def do_step(context):
    settings = context.meta['settings']
    apigeerequired = settings['apigeeEdge']

    if apigeerequired == "ApigeeNotRequired":
        exit()
    sshpubkey = settings['adminSSHKey']
    client_secret = settings['CLIENT-SECRET']
    apigee_dashboard_url = settings['managementUI']
    username = settings["username"]
    home_dir = os.path.join("/home", username)

    f = open("{0}/manifests/elastic-runtime.yml".format(home_dir))
    manifest = yaml.safe_load(f)
    f.close()

    api_endpoint = "https://api.{0}".format(manifest['system_domain'])
    broker_name = "apigee-cf-service-broker"
    broker_url = "https://{0}.{1}".format(broker_name, manifest['apps_domain'])
    cf_admin_password = manifest['properties']['admin_password']
    cf_user = "admin"

    apigeebroker_user = "admin"
    apigeebroker_password = password(client_secret, sshpubkey, True)

    mgmt_url = apigee_dashboard_url.split('9000')
    api_url = mgmt_url[0]+"8080/v1"


    template_context = {
        'redis_passphrase': apigeebroker_password,
        'apigee_dashboard_url': apigee_dashboard_url,
        'apigee_mgmt_api_url': api_url
    }

    manifest = Template(MANIFEST_YAML).render(template_context)

    with open('pivotal-cf-apigee/apigee-cf-service-broker/manifest.yml', 'w') as f:
        f.write(manifest)

    call ("./cf login --skip-ssl-validation -a {0} -u {1}  -p {2}".format(api_endpoint, cf_user, cf_admin_password), shell=True)
    call ("./cf target -o system -s development" , shell=True)
    call ("./cf create-service p-redis shared-vm apigee_cf_service_broker-p-redis", shell=True)
    call ("./cf push -p ./pivotal-cf-apigee/apigee-cf-service-broker -f ./pivotal-cf-apigee/apigee-cf-service-broker/manifest.yml", shell=True)
    call ("./cf set-env apigee-cf-service-broker SECURITY_USER_NAME {0}".format(apigeebroker_user), shell=True)
    call ("./cf set-env apigee-cf-service-broker SECURITY_USER_PASSWORD {0}".format(apigeebroker_password), shell=True)
    call ("./cf restage apigee-cf-service-broker", shell=True)
    call ("./cf create-service-broker apigee-edge {0} {1} {2}".format(apigeebroker_user, apigeebroker_password, broker_url), shell=True)
    call ("./cf enable-service-access apigee-edge", shell=True)
    return context
