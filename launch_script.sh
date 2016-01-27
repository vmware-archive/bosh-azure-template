mkdir manifests

for f in bosh.yml manifests/index.yml setup_dns.py create_cert.sh setup_devbox.py init.sh deploy_bosh.sh 98-msft-love-cf
do
   curl --silent \
        https://raw.githubusercontent.com/cf-platform-eng/bosh-azure-template/master/$f \
        > $f
done

\cp -R * ../../
cd ../../
python setup_devbox.py
