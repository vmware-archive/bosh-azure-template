mkdir manifests

for f in bosh.yml manifests/index.yml setup_dns.py create_cert.sh setup_devbox.py deploy_bosh_and_releases.py init.sh 98-msft-love-cf
do
   curl --silent \
        https://raw.githubusercontent.com/cf-platform-eng/bosh-azure-template/master/$f \
        > $f
done

\cp -R * ../../
cd ../../

# set up jump/dev box and template manifests
python setup_devbox.py

# start tmux, running deploy_bosh_and_releases
tmux -S /tmp/shared-tmux-session new -d -s shared 'python deploy_bosh_and_releases.py; python setup_devbox.py;'
chmod 777 /tmp/shared-tmux-session
