#!/bin/bash

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -a|--action)
    ACTION="$2"
    shift # past argument
    shift # past value
    ;;
esac
done

terraform init -backend-config="bucket=arn:aws:s3:::backetname" -backend-config="key=lambda/backup_retention_lambda.tfstate" -backend-config="region=region-name" -backend=true

if [ "$ACTION" == "plan" ]; then
  terraform plan
fi

if [ "$ACTION" == "apply" ]; then
  terraform apply -auto-approve
fi
