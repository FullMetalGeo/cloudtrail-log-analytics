# CloudTrail Log Analytics using AWS Lambda and Amazon ElasticSearch Service
This AWS Serverless Application will help you analyze AWS CloudTrail Logs using 
Amazon Elasticsearch Service. The application creates:
* An S3 bucket to hold logs from CloudTrail
* An SNS topic to receive messages from CloudTrail
* An SNS subscription to deliver messages to Lambda
* A Lambda function to receive the message, process the data, and push it to Elasticsearch

As originally designed, the Lambda function pushed data to an AWS Elasticsearch cluster.
It has been redesigned to push to the Elastic Cloud service instead, which offers features
such as the X-Pack.  When and if AWS updates their offering to includes such features,
the function could be returned to using the AWS option. 

This repo also includes a template for enabling CloudTrail to publish logs to the 
pusher function.  Simply create a stack using the `templates/cloudtrail.json` file.
You will need to fill in the S3 Bucket name that was created, as well as the ARN for
the SNS topic.

## Prerequisites
- [python 3.6](https://www.python.org/download/releases/3.6/)
- [pip](https://bootstrap.pypa.io/get-pip.py)

## Quick Deploy
Simply run the `deploy.sh` script, providing the profile, stack-name, and bucket to store packaged code: 
```bash
deploy.sh -p my_profile -s my-stack-name -b my-storage-bucket
```

## Step by Step Manual Deploy

### Install the required python packages for the AWS Lambda function 
```bash
$ python -m pip install -r requirements.txt -t ./
```

### Packing Artifacts
Before you can deploy a SAM template, you should first upload your Lambda 
function code zip. Set the `CodeUri` properties to the S3 URI of uploaded files. You
can choose to do this manually or use `aws cloudformation package` [CLI command](http://docs.aws.amazon.com/cli/latest/reference/cloudformation/package.html) to automate the task of uploading local artifacts to S3 bucket. The command returns a copy of your template, replacing references to local artifacts with S3 location where the command uploaded your artifacts. 

To use this command, set `CodeUri` property to be the path to your 
source code folder/zip/jar as shown in the example below. 

**This is already taken care for you, the below documentation is for reference**

```YAML
Function:
    Type: AWS::Serverless::Function
    Properties:
        CodeUri: ./
        ...
```

Run the following command to upload your artifacts to S3 and output a 
packaged template that can be readily deployed to CloudFormation.
```bash
$ aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket bucket-name \
    --output-template-file serverless-output.yaml
```

The packaged template will look something like this:
```YAML
Function:
    Type: AWS::Serverless::Function
    Properties:
        CodeUri: s3://<mybucket>/<my-zipfile-path>
        ...
```

### Deploying to AWS CloudFormation
SAM template is deployed to AWS CloudFormation by [creating a changeset](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-create.html)
using the SAM template followed by [executing the changeset](http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets-execute.html). 
Think of a ChangeSet as a diff between your current stack template and the new template that you are deploying. After you create a ChangeSet, you have the opportunity to examine the diff before executing it. Both the AWS Console and AWS CLI provide commands to create and execute a changeset. 

Alternatively, you can use `aws cloudformation deploy` CLI command to deploy the SAM template. Under-the-hood it creates and executes a changeset and waits until the deployment completes. It also prints debugging hints when the deployment fails. Run the following command to deploy the packaged template to a stack called `cloudtrail-log-analytics`:

```bash
$ aws cloudformation deploy \
    --template-file serverless-output.yaml \
    --stack-name cloudtrail-log-analytics \
    --capabilities CAPABILITY_IAM
```

Refer to the [documentation](http://docs.aws.amazon.com/cli/latest/reference/cloudformation/deploy/index.html) for more details.

