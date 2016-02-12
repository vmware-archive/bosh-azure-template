def do_step(context):
    settings = context.meta['settings']

    username = settings["username"]
    home_dir = os.path.join("/home", username)

    # Copy all the files in ./bosh into the home directory
    call("cp -r ./bosh/* {0}".format(home_dir), shell=True)
    call("cp ./manifests/index.yml {0}/manifests/".format(home_dir), shell=True)

    call("chown -R {0} {1}".format(username, home_dir), shell=True)
    call("chmod 400 {0}/bosh".format(home_dir), shell=True)

    return context
