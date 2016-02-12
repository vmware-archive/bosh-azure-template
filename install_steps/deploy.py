def do_step(context):
    settings = context.meta['settings']

    username = settings["username"]
    home_dir = os.path.join("/home", username)

    # deploy!
    for m in manifests['manifests']:
        call("bosh deployment {0}/manifests/{1}".format(home_dir, m['file']), shell=True)
        call("bosh -n deploy", shell=True)

    return context
