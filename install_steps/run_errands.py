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

    for m in manifests['manifests']:
        print "Running errands for {0}/manifests/{1}...".format(home_dir, m['file'])

        for errand in m['errands']:
            print "Running errand {0}".format(errand)

            task_id = client.run_errand(m['deployment-name'], errand)
            client.wait_for_task(task_id)

    return context
