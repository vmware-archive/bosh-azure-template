# Epsilon - An Azure deployment template for BOSH and CF

### Quickstart

This repository contains an Azure Resource Manager template for
deploying BOSH and Pivotal CloudFoundry. 

#### Before you deploy the template make sure you have accepted Pivotal End User License Agreement:

Elastic Runtime 1.7.15:
https://network.pivotal.io/products/elastic-runtime/releases/2134/eula

MySQL for PCF 1.7.8:
https://network.pivotal.io/products/p-mysql/releases/1770/eula

RabbitMQ for PCF 1.6.0:
https://network.pivotal.io/products/pivotal-rabbitmq-service/releases/1799/eula

Redis for PCF 1.5.15:
https://network.pivotal.io/products/p-redis/releases/1876/eula

Spring Cloud Services for PCF 1.0.9:
https://network.pivotal.io/products/p-spring-cloud-services/releases/1735/eula


It also deploys 
- Concourse  https://github.com/concourse/concourse
- Azure Service Meta broker https://github.com/Azure/meta-azure-service-broker
- Apigee Edge Service Broker https://github.com/apigee/pivotal-cf-apigee/tree/master/apigee-cf-service-broker 


- Clone this repository `$ git clone https://github.com/cf-platform-eng/bosh-azure-template`
- Create an Azure deployment parameters file for go with the template itself, call it 'azure-deploy-parameters.json'. The file needs to look like this;

```
{
  "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "storageAccountNamePrefixString": {
      "value": "mystorage"
    },
   "adminSSHKey": {
      "value": "ssh-rsa XXXXxxxx"
    },
    "tenantID": {
      "value": "00000000-0000-0000-0000-000000000000"
    },
    "clientID": {
      "value": "00000000-0000-0000-0000-000000000000"
    },
    "clientSecret": {
      "value": "xxxxxxxxxxxxxxx"
    },
    "pivnetAPIToken": {
      "value": "xxxxxxxxxxxxxxx"
    }
  }
}
```

- Give each parameter a suitable value;

    - storageAccountNamePrefixString - this is a unique prefix name for you Azure storage account.
    - adminSSHKey - your rsa public key that will be trusted by the "jumpbox"
    - tenantID - your tenant ID for the subscription you wish to use
    - clientID - the client ID associated to the subscription
    - clientSecret - the clients secret (password)
    - pivnetAPIToken - all releases for BOSH are supported releases downloaded from Pivotal Network. Access to the network website is made available via the API token assigned to your account.


- Once that file is complete, you can deploy it like this;

```
$ azure group create -n "cf" -l "West US"
$ azure group deployment create -f azuredeploy.json -e azuredeploy.parameters.json -v cf cfdeploy
```

Once the azure CLI has returned, there should be a tmux process running on the "jumpbox", completing the rest of the install. Connect to the session like this;

```
ssh -t user@jumpboxname.westus.cloudapp.azure.com "tmux -S /tmp/shared-tmux-session attach -t shared"
```
