#!/bin/bash

set -ex

nuke_aws() {
  cloud-nuke --version
  cloud-nuke aws \
      --log-level debug \
      --resource-type s3 \
      --resource-type vpc \
      --resource-type ebs \
      --resource-type eip \
      --resource-type ec2 \
      --resource-type efs \
      --resource-type asg \
      --resource-type ekscluster \
      --resource-type nat-gateway \
      --resource-type iam-role \
      --resource-type elb \
      --region us-west-2 \
      --log-level debug \
      --config tests/scripts/cloud-nuke-config.yml
}

nuke_aws || true
echo "Trying again to nuke to be sure"
nuke_aws
echo "Done"
