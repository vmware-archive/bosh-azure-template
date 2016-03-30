# Gamma - An Azure deployment template for BOSH and CF

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fcf-platform-eng%2Fbosh-azure-template%2Fmaster%2Fazuredeploy.json" target="_blank">
    <img src="http://azuredeploy.net/deploybutton.png"/>
</a>

### Quickstart

This repository contains, amongst other things, an Azure Resource Manager template for
deploying BOSH and CloudFoundry.


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
