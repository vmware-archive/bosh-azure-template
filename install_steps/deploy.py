import bosh_client
import os
import yaml

def do_step(context):
    settings = context.meta['settings']
    username = settings["username"]
    home_dir = os.path.join("/home", username)

    f = open('manifests/index.yml')
    manifests = yaml.safe_load(f)
    f.close()

    client = bosh_client.BoshClient("https://10.0.0.4:25555", "admin", "admin")

    # deploy!
    for m in manifests['manifests']:
	print "Deploying {0}/manifests/{1}...".format(home_dir, m['file'])
	manifest = open("{0}/manifests/{1}".format(home_dir, m['file'])).read()
	task_id = client.create_deployment(manifest)
	client.wait_for_task(task_id)
	print "Finished deploying {0}/manifests/{1}...".format(home_dir, m['file'])

    return context
