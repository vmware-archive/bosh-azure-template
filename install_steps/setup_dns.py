def do_step(context):
    settings = context.meta['settings']
    username = settings["username"]
    home_dir = os.path.join("/home", username)

    # Setup the devbox as a DNS
    enable_dns = settings["enable-dns"]
    if enable_dns:
        try:
            import urllib2
            cf_ip = settings["cf-ip"]
            dns_ip = re.search('\d+\.\d+\.\d+\.\d+', urllib2.urlopen("http://www.whereismyip.com").read()).group(0)
            call("python setup_dns.py -d cf.azurelovecf.com -i 10.0.16.4 -e {0} -n {1} >/dev/null 2>&1".format(cf_ip, dns_ip), shell=True)
            # Update motd
            call("cp -f 98-msft-love-cf /etc/update-motd.d/", shell=True)
            call("chmod 755 /etc/update-motd.d/98-msft-love-cf", shell=True)
        except Exception as e:
            err_msg = "\nWarning:\n"
            err_msg += "\nFailed to setup DNS with error: {0}, {1}".format(e, traceback.format_exc())
            err_msg += "\nYou can setup DNS manually with \"python setup_dns.py -d cf.azurelovecf.com -i 10.0.16.4 -e External_IP_of_CloudFoundry -n External_IP_of_Devbox\""
            err_msg += "\nExternal_IP_of_CloudFoundry can be found in {0}/settings.".format(home_dir)
            err_msg += "\nExternal_IP_of_Devbox is the dynamic IP which can be found in Azure Portal."
            with open(install_log, 'a') as f:
                f.write(err_msg)

    return context
