def do_step(context):

    settings = context.meta['settings']

    username = settings["username"]
    home_dir = os.path.join("/home", username)

    os.environ["HOME"] = home_dir

    # deploy director
    os.environ["BOSH_INIT_LOG_LEVEL"] = 'INFO'
    os.environ["BOSH_INIT_LOG_PATH"] = './bosh-init-debug.log'

    # do we have a targeted bosh?
    p = Popen(['bosh', 'target'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    # assume if no bosh is target, there is no director
    if "Target not set" in err:

        res = None

        while res != 0:
            res = call("bosh-init deploy ./bosh/bosh.yml", shell=True)

        p = Popen(['bosh', 'target', '10.0.0.4'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"admin\r\nadmin\r\n")
        rc = p.returncode

    # change owner for bosh.yaml
    call("chown -R {0} {1}/.bosh_config".format(username, home_dir), shell=True)

    return context
