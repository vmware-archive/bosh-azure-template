import urllib2
import tempfile

def authorizedPost(url, token):
    req = urllib2.Request(url)
    req.add_header("Authorization", "Token {0}".format(token))
    req.add_header("Accept", "application/json")
    req.data = ''

    res = urllib2.urlopen(req)
    return res

def do_step(context):
    settings = context.meta['settings']

    pivnetAPIToken = settings["pivnet-api-token"]

    eula_urls = ["https://network.pivotal.io/api/v2/products/{0}/releases/{1}/eula_acceptance".format(m['release-name'], m['release-number'])
        for m in manifests['manifests']]

    release_urls = ["https://network.pivotal.io/api/v2/products/{0}/releases/{1}/product_files/{2}/download".format(m['release-name'], m['release-number'], m['file-number'])
        for m in manifests['manifests']]

    stemcell_urls = [m['stemcell'] for m in manifests['manifests']]

    # accept eula for each product
    for url in eula_urls:
        res = authorizedPost(url, pivnetAPIToken)
        code = res.getcode()

    # releases
    is_release_file = re.compile("^releases\/.+")
    call("mkdir -p /tmp/releases", shell=True)

    print "Processing releases."

    for url in release_urls:

        print "Downloading {0}.".format(url)

        res = authorizedPost(url, pivnetAPIToken)
        code = res.getcode()

        length = int(res.headers["Content-Length"])

        # content-length
        if code is 200:

            total = 0
            pcent = 0.0
            CHUNK = 16 * 1024

            with tempfile.TemporaryFile() as temp:
                while True:
                    chunk = res.read(CHUNK)
                    total += CHUNK
                    pcent = (float(total) / float(length)) * 100

                    sys.stdout.write("Download progress: %.2f%% (%.2fM)\r" % (pcent, total / 1000000.0) )
                    sys.stdout.flush()

                    if not chunk: break
                    temp.write(chunk)

                print "Download complete."

                z = zipfile.ZipFile(temp)
                for name in z.namelist():

                    # is this a release?
                    if is_release_file.match(name):

                        release_filename = "/tmp/{0}".format(name)

                        print "Unpacking {0}.".format(name)
                        z.extract(name, "/tmp")

                        # upload the file with bosh
                        print "Uploading release {0} to BOSH director.".format(name)
                        call("bosh upload release {0}".format(release_filename), shell=True)

                        os.unlink(release_filename)

                z.close()
                temp.close()

    # stemcells
    print "Processing stemcells."

    for url in stemcell_urls:
        print "Processing stemcell {0}".format(url)
        call("bosh upload stemcell {0}".format(url), shell=True)


    return context
