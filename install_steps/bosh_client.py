from urllib2 import urlopen
from urllib2 import Request
import ssl
import json
import base64
import time

class BoshClient:
    def __init__(self, url, username, password):
        self.bosh_url = url
        self.username = username
        self.password = password

        self.ssl_ctx = ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    def get(self, url):
        request = Request(url)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urlopen(request, context=self.ssl_ctx).read()
        return result

    def post(self, url, data, files=None):
        request = Request(url)
        request.data = data

        if files is not None:
            request.files = files
            request.add_header("Content-Type", "multipart/form-data")
        else:
            request.add_header("Content-Type", "application/json")

        print request.headers

        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        result = urlopen(request, context=self.ssl_ctx)
        return result

    def wait_for_task(self, task_id):
        task_url = "{0}/tasks/{1}".format(self.bosh_url, task_id)
        result = json.loads(self.get(task_url))
        while result['state'] == 'queued' or result['state'] == 'processing':
            result = json.loads(self.get(task_url))
            time.sleep(1)
        return result

    def get_uuid(self):
        return self.get_info()["uuid"]

    def get_info(self):
        info_url = "{0}/info".format(self.bosh_url)
        self.info = json.loads(self.get(info_url))
        return self.info

    def get_deployments(self):
        deployments_url = "{0}/deployments".format(self.bosh_url)
        self.deployments = json.loads(self.get(deployments_url))
        return self.deployments

    def get_vms(self, deployment_name):
        vms_url = "{0}/deployments/{1}/vms".format(self.bosh_url, deployment_name)
        vms = json.loads(self.get(vms_url))
        return vms

    def upload_stemcell(self, stemcell_url):
        stemcells_url = "{0}/stemcells".format(self.bosh_url)
        payload = '{"location":"%s"}' % stemcell_url
        result = self.post(stemcells_url, payload)
        task_id = json.loads(result.read())["id"]
        return task_id

    def upload_release(self, release_url):
        releases_url = "{0}/releases".format(self.bosh_url)
        payload = '{"location":"%s"}' % release_url
        result = self.post(releases_url, payload)
        task_id = json.loads(result.read())["id"]
        return task_id
