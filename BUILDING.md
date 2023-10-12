# BUILDING with AWS and AWS SSO credentials

##Install AWS CLI

```
# mac
brew install awscli
# linux
pip install awscliv2
# windows
choco install awscli
```

And you'll want a $HOME/.aws/config with at least the following:  
  
```  
[profile poweruser]  
region = us-east-1  
output = json
sso_account_id = 1234512345
sso_start_url = https://d-91234512345.awsapps.com/start  
sso_region = us-east-1  
sso_role_name = PowerUserAccess  
sso_registration_scopes = sso:account:access  
```  
  
I'm working on "normalizing" the nebari-ioos repo at the moment, but you should be able to give it a go with the following:  

```
git clone git@github.com/kumulustech/nebari-ioos -b remove-datascience

cd nebari-ioos  
python3 -m venv .venv

. .venv/bin/activate

pip install -U -e .

```

  

Login to AWS via the SSO mechanism:  
  
```
unset AWS_DEFAULT_PROFILE
export AWS_PROFILE=poweruser
export AWS_REGION=us-west-2

aws sso login
```

  

`nebari init` "should" work, but just in case, I'd use the following nebari-config.yaml:

  

```
provider: aws  
namespace: testproj  
nebari_version: 2023.9.1rc2.dev4+gebb2aa6c.d20231002  
project_name: testproj  
domain: testproj.example.com

terraform_state:  
  type: remote  
#ci_cd:  
#  type: github-actions  
monitoring:  
  enabled: true  
amazon_web_services:  
  region: us-west-2  
  kubernetes_version: '1.28'  
  node_groups:  
    general:  
      instance: m5.2xlarge  
      min_nodes: 2  
      max_nodes: 5  
helm_extensions:  
  - name: wordpress  
    version: 17.1.17  
    repository: https://charts.bitnami.com/bitnami  
    chart: wordpress  
    overrides:  
      wordpressUsername: admin  
      #wordpressPassword: admin  
      wordpressEmail: rstarmer@rhkpventures.com  
      service:  
        type: ClusterIP  
        ports:  
          http: 80  
  - name: wordpressir  
    version: 0.1.4  
    repository: https://kumulustech.github.io/ingressroute-helm  
    chart: ingressroute  
    overrides:  
      host: test.pacioos.dev  
      path: /  
      service:  
        name: wordpress  
        port: 80  
certificate:  
  type: lets-encrypt  
  acme_email: rstarmer@rhkpventures.com  
  acme_server: https://acme-v02.api.letsencrypt.org/directory  

```

You will have to add a CNAME record for the AWS SLB for this cluster, but it _should_ function.  This can be done in Route 53 via the console (after you login with AWS SSO, it should point you at the start page from your aws profile, e.g. https://d-91234512345.awsapps.com/start) and from there you should be able to get access to the console as a power user.
  
At which point, you should have wordpress up and running...
  
