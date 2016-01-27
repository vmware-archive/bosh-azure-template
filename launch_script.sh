mkdir manifests

for f in bosh.yml manifests/index.yml setup_dns.py create_cert.sh setup_devbox.py init.sh deploy_bosh.sh 98-msft-love-cf
do
   curl --silent \
        https://raw.githubusercontent.com/cf-platform-eng/bosh-azure-template/master/$f \
        > $f
done

\cp -R * ../../
cd ../../

# set up jump/dev box and template manifests
python setup_devbox.py

# deploy bosh director
export BOSH_INIT_LOG_LEVEL='Debug'
export BOSH_INIT_LOG_PATH='./bosh-init-debug.log'

bosh-init deploy bosh.yml >>./install.log 2>&1
