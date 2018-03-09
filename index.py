""" This module reads the SNS message to get the S3 file location for cloudtrail
 log and stores into Elasticsearch. """

from __future__ import print_function
import json
import boto3
import logging
import datetime
import gzip
import urllib
import os
import traceback
import io

# from awses.connection import AWSConnection
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
                                
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3', region_name=os.environ['AWS_REGION'])

# AWS Auth credentials, not currently using, but may some day
#awsauth = AWS4Auth(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], os.environ['AWS_REGION'], 'es', session_token=os.environ['AWS_SESSION_TOKEN'])

def get_config():
    # get SSM client
    client = boto3.client('ssm', region_name=os.environ['AWS_REGION'])
    
    # Get parameters on our path from SSM
    response = client.get_parameters_by_path(
        Path = '/dev/CloudTrailPushFunction/',
        Recursive = False,
        WithDecryption = True
    )
    
    config = {}
    for item in response['Parameters']:
        # Hacky, but trim first 28 characters off name to remove prefix
        name = item['Name'][28:]
        config[name] = item['Value']
    
    # Uncomment for debugging config
    #logger.info('Config ' + json.dumps(config, indent=2))
    
    return config
    
def handler(event, context):
    # Get config from SSM parameter store
    config = get_config()
    
    # Setup elasticsearch connection
    es = Elasticsearch(
        hosts=[{'host': config['ES_HOST'], 'port': int(config['ES_PORT'])}],
        http_auth=(config['ES_USER'], config['ES_PASS']),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    # Log Incoming Message
    logger.info('Event: ' + json.dumps(event, indent=2))
    message = json.loads(event['Records'][0]['Sns']['Message'])

    # Define s3 bucket and object
    s3Bucket = message['s3Bucket']
    s3ObjectKey = urllib.parse.unquote(message['s3ObjectKey'][0])
    
    # Log bucket and object key data
    logger.info('S3 Bucket: ' + s3Bucket)
    logger.info('S3 Object Key: ' + s3ObjectKey)

    try:
        response = s3.get_object(Bucket=s3Bucket, Key=s3ObjectKey)
        
        # Get compressed file object
        file = io.BytesIO(response['Body'].read())
        
        # Read compressed file
        content = gzip.GzipFile(fileobj=file).read()

        # Process lines in file
        for record in json.loads(content)['Records']:
            recordJson = json.dumps(record)
            logger.info(recordJson)
            indexName = config['ES_INDEX'] + '-' + datetime.datetime.now().strftime("%Y-%m-%d")
            res = es.index(index=indexName, doc_type='record', id=record['eventID'], body=recordJson)
            logger.info(res)
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        traceback.print_exc()
        return False
