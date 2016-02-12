def do_step(context):
    settings = context.meta['settings']

    #Install bosh_cli and bosh-init
    call("mkdir /mnt/bosh_install; cp init.sh /mnt/bosh_install; cd /mnt/bosh_install; sh init.sh >{0} 2>&1;".format(install_log), shell=True)

    return context
