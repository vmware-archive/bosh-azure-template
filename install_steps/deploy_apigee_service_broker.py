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

PROPERTIES = """
certFile=server.crt
keyFile=serverkey.pem
"""

VIRTUALHOST_SSL = """
<VirtualHost name="vhssl">
  <HostAliases>
    <HostAlias>{{apigee_hostname}}</HostAlias>
  </HostAliases>
  <Interfaces/>
  <Port>8443</Port>
    <SSLInfo>
      <Enabled>true</Enabled>
      <KeyStore>myKeystore</KeyStore>
      <KeyAlias>myServerKey</KeyAlias>
    </SSLInfo>
</VirtualHost>
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
    apigeeusername = settings['adminUsername']
    apigeepassword = settings['apigeeAdminPassword']
    apigeeadminemail = settings['apigeeAdminEmail']

    cf_ip = settings["cf-ip"]

    if apigeerequired == "ApigeeNotRequired":
        exit()
    sshpubkey = settings['adminSSHKey']
    client_secret = settings['CLIENT-SECRET']
    apigee_dashboard_url = settings['managementUI']
    apigee_mgmt_dns = settings['managementDNSName']
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
    mgmt_dns = apigee_mgmt_dns.split('//')
    apigee_hostname = mgmt_dns[1]+":8443"
    api_url = mgmt_url[0]+"8080/v1"



    template_context = {
        'redis_passphrase': apigeebroker_password,
        'apigee_dashboard_url': apigee_dashboard_url,
        'apigee_mgmt_api_url': api_url
    }

    manifest = Template(MANIFEST_YAML).render(template_context)

    with open('pivotal-cf-apigee/apigee-cf-service-broker/manifest.yml', 'w') as f:
        f.write(manifest)

    print "============================================================"
    print "api_endpoint            : {0}".format(api_endpoint)
    print "Apigee broker user      : {0}".format(apigeebroker_user)
    print "Apigee broker password  : {0}".format(apigeebroker_password)
    print "============================================================"

    call ("./cf login --skip-ssl-validation -a {0} -u {1}  -p {2}".format(api_endpoint, cf_user, cf_admin_password), shell=True)
    call ("./cf target -o system -s development" , shell=True)
    call ("./cf create-service p-redis shared-vm apigee_cf_service_broker-p-redis", shell=True)
    call ("./cf push -p ./pivotal-cf-apigee/apigee-cf-service-broker -f ./pivotal-cf-apigee/apigee-cf-service-broker/manifest.yml", shell=True)
    call ("./cf set-env apigee-cf-service-broker SECURITY_USER_NAME {0}".format(apigeebroker_user), shell=True)
    call ("./cf set-env apigee-cf-service-broker SECURITY_USER_PASSWORD {0}".format(apigeebroker_password), shell=True)
    call ("./cf restage apigee-cf-service-broker", shell=True)
    call ("./cf create-service-broker apigee-edge {0} {1} {2}".format(apigeebroker_user, apigeebroker_password, broker_url), shell=True)
    call ("./cf enable-service-access apigee-edge", shell=True)

    print "============================================================"
    print "deploging virtual host"

    call ("mkdir apigee", shell=True)
    call ("cd apigee", shell=True)
    call ("mkdir META-INF", shell=True)

    call ("openssl genrsa -des3 -passout pass:{0} -out serverkey.pem 1024".format(apigeebroker_password), shell=True)
    call ("openssl genrsa -des3 -passout pass:{0} -out  clientkey.pem 1024".format(apigeebroker_password), shell=True)
    call ("openssl req -passin pass:{0} -new -key serverkey.pem -out server.csr -subj \"/C=US/ST=CA/L=San Francisco/O=Pivotal Labs/OU=Platform Engineering/CN={1}.cf.pcfazure.com\"".format(apigeebroker_password,cf_ip), shell=True)
    call ("openssl req -passin pass:{0} -new -key clientkey.pem -out client.csr -subj \"/C=US/ST=CA/L=San Francisco/O=Pivotal Labs/OU=Platform Engineering/CN={1}.cf.pcfazure.com\"".format(apigeebroker_password,cf_ip), shell=True)

    call ("cp serverkey.pem server.key.org", shell=True)
    call ("openssl rsa  -passin pass:{0} -in server.key.org -out serverkey.pem".format(apigeebroker_password), shell=True)

    call ("cp clientkey.pem client.key.org", shell=True)
    call ("openssl rsa -passin pass:{0} -in client.key.org -out clientkey.pem".format(apigeebroker_password), shell=True)

    call ("openssl x509 -req -days 365 -in server.csr -signkey serverkey.pem -out server.crt", shell=True)
    call ("openssl x509 -req -days 365 -in client.csr -signkey clientkey.pem -out client.crt", shell=True)
    call ("apt-get install openjdk-7-jdk -y", shell=True)

    call ("jar -cf serverKey.jar server.crt serverkey.pem", shell=True)

    vhssl_template_context = {
        'apigee_hostname': apigee_hostname
    }

    vhssl = Template(VIRTUALHOST_SSL).render(vhssl_template_context)

    with open('vhssl.xml', 'w') as f:
        f.write(vhssl)

    with open('META-INF/descriptor.properties', 'w') as f:
        f.write(PROPERTIES)

    call ("jar -uf serverKey.jar META-INF/descriptor.properties", shell=True)

    print "api_url: {0}".format(api_url)

    keystore_cmd = "curl -u {0}:{1} {2}/o/{3}/environments/test/keystores -H \"Content-Type: text/xml\" -d '<KeyStore name=\"myKeystore\"/>'".format(apigeeadminemail, apigeepassword, api_url, apigeeusername)
    print "keystore cmd: {0}".format(keystore_cmd)
    call (keystore_cmd, shell=True)

    postkeystore_cmd = "curl -u {0}:{1} -X POST -H \"Content-Type: multipart/form-data\" -F file=\"@serverKey.jar\" '{2}/o/{3}/environments/test/keystores/myKeystore/keys?alias=myServerKey'".format(apigeeadminemail, apigeepassword, api_url, apigeeusername)
    print ("postkeystore_cmd: {0}". format(postkeystore_cmd))
    call (postkeystore_cmd, shell=True)

    virtualhost_cmd = "curl -X POST -H \"Content-Type: text/xml\" -d @vhssl.xml {0}/o/{1}/environments/test/virtualhosts -u {2}:{3}".format(api_url, apigeeusername, apigeeadminemail, apigeepassword)
    print ("virtualhost_cmd: {0}".format(virtualhost_cmd))
    call (virtualhost_cmd, shell=True)

    return context
