def do_step(context):

    settings = context.meta['settings']
    username = settings["username"]
    home_dir = os.path.join("/home", username)


    # run bosh status and get the id back to inject in to manifests
    bosh_uuid = subprocess.Popen(["bosh", "status", "--uuid"], stdout=subprocess.PIPE).communicate()[0]
    print "Director uuid is {0}".format(bosh_uuid)

    # set the director id on the manifests
    for m in manifests['manifests']:
        with open ("{0}/manifests/{1}".format(home_dir, m['file']), 'r+') as f:

            contents = f.read()
            template = Template(contents)
            contents = template.render(DIRECTOR_UUID=bosh_uuid)

            f.seek(0)
            f.write(contents)
            f.truncate()
            f.close()

    return context
