
# Set up Variables
PROFILE="gsoyka-sandbox"
S3_BUCKET="grant-cf-test"
STACK_NAME="cloudtrail-elasticsearch"

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
