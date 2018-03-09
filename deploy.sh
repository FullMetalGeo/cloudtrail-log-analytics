#!/bin/bash
set -e

# Get options
while getopts "b:s:p:" opt; do
  case $opt in
    b )
      S3_BUCKET=$OPTARG
      echo "S3 Bucket: $OPTARG" >&2
      ;;
    s )
      STACK_NAME=$OPTARG
      echo "Stack Name: $OPTARG" >&2
      ;;
    p ) 
      PROFILE=$OPTARG
      echo "Profile: $OPTARG" >&2
      ;;
    \? ) echo "Usage: deploy [-b] bucket_name [-s] stack_name [-p] profile"
      ;;
  esac
done

# Set up Variables
if [[ -z $PROFILE ]]; then PROFILE="default"; fi
if [[ -z $STACK_NAME ]]; then STACK_NAME="cloudtrail-elasticsearch"; fi
if [[ -z $S3_BUCKET ]]; then echo "ERROR: You must provide a bucket name to store the code bundle" && exit 1; fi

# Somewhat hacky fix for mac and pip
case "$(uname -s)" in
   Darwin)
      cat << EOF > setup.cfg
[install]
prefix=
EOF
      ;;
esac

# Install python requirements
python -m pip install --upgrade -r requirements.txt -t ./

# Cleanup
if [[ -f setup.cfg ]]; then rm setup.cfg; fi

aws --profile $PROFILE cloudformation package \
  --template-file template.yml \
  --s3-bucket $S3_BUCKET \
  --output-template-file serverless-output.yml

aws --profile $PROFILE cloudformation deploy \
  --template-file serverless-output.yml \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM

echo "Stack $STACK_NAME has been created, but you still need to enter the ElasticSearch password"
echo 'Create a parameter in Parameter Store with path $CONFIG_PATH/ES_PASS with the password value'
