def do_step(context):
    settings = context.meta['settings']

    # cf specific configuration (configure security groups for haproxy)
    bosh_address = "10.0.0.4"
    deployment_name = "router-and-lb"
    subscription_id = settings['SUBSCRIPTION-ID']
    tenant = settings['TENANT-ID']
    endpoint = "https://login.microsoftonline.com/{0}/oauth2/token".format(tenant)
    client_token = settings['CLIENT-ID']
    client_secret = settings['CLIENT-SECRET']

    ip = get_job_ip_address("admin", "admin", bosh_address, deployment_name, "haproxy")

    token = get_token_from_client_credentials(endpoint, client_token, client_secret)
    creds = SubscriptionCloudCredentials(subscription_id, token)

    network_client = azure.mgmt.network.NetworkResourceProviderClient(creds)
    rules_client = azure.mgmt.network.networkresourceprovider.SecurityRuleOperations(network_client)

    ha_proxy_address = "10.0.16.200"

    rule = azure.mgmt.network.SecurityRule(
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

    rule = azure.mgmt.network.SecurityRule(
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

    rules_client.create_or_update("cf", "CFSecurityGroup", "http_inbound", rule)

    return context
