from urllib2 import urlopen
from urllib2 import Request
import json
import base64
import time
import sys


class BoshClient:
    def __init__(self, url, username, password):
        self.bosh_url = url
        self.username = username
        self.password = password

    def get(self, url):
        request = Request(url)
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        result = urlopen(request).read()
        return result

    def post(self, url, data, content_type):
        request = Request(url)
        request.data = data
        request.add_header("Content-Type", content_type)

        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        result = urlopen(request)
        return result

    def wait_for_task(self, task_id):
        events = []

        task_url = "{0}/tasks/{1}".format(self.bosh_url, task_id)
        result = json.loads(self.get(task_url))
        while result['state'] == 'queued' or result['state'] == 'processing':
            result = json.loads(self.get(task_url))
            task_events = self.get_task_events(task_id)
            for event in task_events:
                existing = filter(lambda x: x['stage'] == event['stage'] and \
			x['task'] == event['task'] and \
			x['state'] == event['state'], events)
		if len(existing) == 0:
			events.append(event)
			tags = "".join(event['tags'])
			print "{0}\033[92m{1}\033[0m > \033[92m{2}\033[0m {3}".format(event['stage'], tags, event['task'], event['state'])

            time.sleep(3)
        return result

    def get_uuid(self):
        return self.get_info()["uuid"]

    def get_info(self):
        info_url = "{0}/info".format(self.bosh_url)
        self.info = json.loads(self.get(info_url))
        return self.info

    def get_task_events(self, task_id):
        task_url = "{0}/tasks/{1}/output?type=event".format(self.bosh_url, task_id)
        result = self.get(task_url)
        items = []

        for line in result.split("\n"):
	    try:
                items.append(json.loads(line))
	    except ValueError:
		pass

        return items

    def get_deployments(self):
        deployments_url = "{0}/deployments".format(self.bosh_url)
        self.deployments = json.loads(self.get(deployments_url))
        return self.deployments

    def create_deployment(self, manifest):
        deployments_url = "{0}/deployments".format(self.bosh_url)
        result = self.post(deployments_url, manifest, 'text/yaml')
        task_id = json.loads(result.read())["id"]
        return task_id

    def get_releases(self):
        releases_url = "{0}/releases".format(self.bosh_url)
        self.releases = json.loads(self.get(releases_url))
        return self.releases

    def get_vms(self, deployment_name):
        vms_url = "{0}/deployments/{1}/vms".format(self.bosh_url, deployment_name)
        vms = json.loads(self.get(vms_url))
        return vms

    def upload_stemcell(self, stemcell_url):
        stemcells_url = "{0}/stemcells".format(self.bosh_url)
        payload = '{"location":"%s"}' % stemcell_url
        result = self.post(stemcells_url, payload, 'application/json')
        task_id = json.loads(result.read())["id"]
        return task_id

    def upload_release(self, release_url):
        releases_url = "{0}/releases".format(self.bosh_url)
        payload = '{"location":"%s"}' % release_url
        result = self.post(releases_url, payload, 'application/json')
        task_id = json.loads(result.read())["id"]
        return task_id

    def ip_table(self, deployment_name):
        url = "{0}/deployments/{1}/vms?format=full".format(self.bosh_url, deployment_name)
        res = self.get(url)
        task_id = json.loads(res)['id']
        self.wait_for_task(task_id)

        task_url = "{0}/tasks/{1}/output?type=result".format(self.bosh_url, task_id)
        response = self.get(task_url)
        ips = {}

        for vm in response.split("\n"):
            if vm:
                vm_dict = json.loads(vm)
                ips[vm_dict['job_name']] = vm_dict['ips']

        self.address_table = ips
        return self.address_table
