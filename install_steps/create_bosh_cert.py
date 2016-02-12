def do_step(context):

    call("mkdir -p ./bosh", shell=True)
    call("mkdir -p ./bosh/manifests", shell=True)

    # Generate the private key and certificate
    call("sh create_cert.sh", shell=True)
    call("cp bosh.key ./bosh/bosh", shell=True)
    with open ('bosh_cert.pem', 'r') as tmpfile:
        ssh_cert = tmpfile.read()
    ssh_cert = "|\n" + ssh_cert
    ssh_cert="\n        ".join([line for line in ssh_cert.split('\n')])

    context.meta['settings']['SSH_CERTIFICATE'] = ssh_cert
    
    return context
