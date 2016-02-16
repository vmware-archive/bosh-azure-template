import apt
import os

def download(url, path):
    res = urllib2.urlopen(url)

    code = res.getcode()
    length = int(res.headers["Content-Length"])

    # content-length
    if code is 200:

        CHUNK = 16 * 1024

        with open(path, 'wb') as temp:
            while True:
                chunk = res.read(CHUNK)

                if not chunk: break
                temp.write(chunk)

def do_step(context):
    settings = context.meta['settings']

    # install packages
    # package_list = ['build-essential', 'tmux', 'ruby2.0', 'ruby2.0-dev', \
    #     'libxml2-dev', 'libsqlite3-dev', 'libxslt1-dev', 'libpq-dev', \
    #     'libmysqlclient-dev', 'zlibc', 'zlib1g-dev', 'openssl', 'libxslt-dev', \
    #     'libssl-dev', 'libreadline6', 'libreadline6-dev', 'libyaml-dev', \
    #     'sqlite3', 'libffi-dev']
    #
    # print "Updating apt cache"
    # cache = apt.cache.Cache()
    # cache.update()
    #
    # for package in package_list:
    #     pkg = cache[package]
    #
    #     if not pkg.is_installed:
    #         pkg.mark_install()
    #
    # try:
    #     cache.commit()
    # except Exception, arg:
    #     print >> sys.stderr, "Sorry, package installation failed [{err}]".format(err=str(arg))
    #
    # for file in ['/usr/bin/ruby', '/usr/bin/gem', '/usr/bin/irb', \
    #     '/usr/bin/rdoc', '/usr/bin/erb']:
    #     os.remove(file)
    #
    # # Update Ruby 1.9 to 2.0
    # os.symlink('/usr/bin/ruby2.0', '/usr/bin/ruby')
    # os.symlink('/usr/bin/gem2.0', '/usr/bin/gem')
    # os.symlink('/usr/bin/irb2.0', '/usr/bin/irb')
    # os.symlink('/usr/bin/rdoc2.0', '/usr/bin/rdoc')
    # os.symlink('/usr/bin/erb2.0', '/usr/bin/erb')

    #Install bosh_cli and bosh-init
    # call("mkdir /mnt/bosh_install; cp init.sh /mnt/bosh_install; cd /mnt/bosh_install; sh init.sh >{0} 2>&1;".format(install_log), shell=True)

    # call("gem install bosh_cli -v 1.3184.0 --no-ri --no-rdoc", shell=True)
    download("https://s3.amazonaws.com/bosh-init-artifacts/bosh-init-0.0.81-linux-amd64", "/usr/local/bin/bosh-init")
    call("chmod +x /usr/local/bin/bosh-init", shell=True)

    return context
