from install_steps import bosh_client
from azure.mgmt.network import NetworkResourceProviderClient, SecurityRule
from azure.mgmt.network.networkresourceprovider import SecurityRuleOperations
from azure.mgmt.common import SubscriptionCloudCredentials
from urllib2 import Request
from urllib2 import urlopen
from urllib import urlencode
import json


def get_token_from_client_credentials(endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    request = Request(endpoint)
    request.data = urlencode(payload)
    result = urlopen(request)
    return json.loads(result.read())['access_token']


def do_step(context):
    settings = context.meta['settings']

    # cf specific configuration (configure security groups for haproxy)
    deployment_name = "elastic-runtime"
    subscription_id = settings['SUBSCRIPTION-ID']
    tenant = settings['TENANT-ID']
    endpoint = "https://login.microsoftonline.com/{0}/oauth2/token".format(tenant)
    client_token = settings['CLIENT-ID']
    client_secret = settings['CLIENT-SECRET']

    client = bosh_client.BoshClient("https://10.0.0.4:25555", "admin", "admin")
    ip_table = client.ip_table(deployment_name)

    ha_proxy_address = ip_table['haproxy'][0]

    token = get_token_from_client_credentials(endpoint, client_token, client_secret)
    creds = SubscriptionCloudCredentials(subscription_id, token)

    network_client = NetworkResourceProviderClient(creds)
    rules_client = SecurityRuleOperations(network_client)

    rule = SecurityRule(
        description="",
        protocol="*",
        source_port_range="*",
        destination_port_range="80",
        source_address_prefix="*",
        destination_address_prefix=ha_proxy_address,
        access="Allow",
        priority=1100,
        direction="InBound"
    )

    rules_client.create_or_update("cf", settings['NSG-NAME-FOR-CF'], "http_inbound", rule)

    rule = SecurityRule(
        description="",
        protocol="*",
        source_port_range="*",
        destination_port_range="443",
        source_address_prefix="*",
        destination_address_prefix=ha_proxy_address,
        access="Allow",
        priority=1200,
        direction="InBound"
    )

    rules_client.create_or_update("cf", settings['NSG-NAME-FOR-CF'], "https_inbound", rule)

    return context
