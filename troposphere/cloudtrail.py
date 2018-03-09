#!/usr/bin/python3
from troposphere import (
    Base64, 
    Tags, 
    Join, 
    GetAtt,
    Parameter,
    Output,
    Ref,
    Template,
    Sub
    )
from troposphere.cloudtrail import Trail
from pathlib import Path
import types
import sys, getopt
import os
import re

## BEGIN Input Parameter Definition ##
## These are "global" parameters that will be assigned to all instances
parameters = {
        "LogBucket" : Parameter(
            "LogBucket",
            Description = "The S3 bucket to write logs to",
            Type = "String",
            Default = "cloudtrail-elasticsearch-s3bucket-yvjvmo9n5z5r	",
            ),
         "SnsTopic" : Parameter(
            "SnsTopic",
            Description = "The arn of the SNS topic to notify for log delivery",
            Type = "String",
            Default = "arn:aws:sns:us-east-1:514107046317:cloudtrail-elasticsearch-SNSTopic-1M25KZBQ31OBB",
            ),
}
def gen_cloudtrail():
    trail = Trail(
        "CloudTrail",
        TrailName = "CloudTrail",
        IsLogging = True,
        IsMultiRegionTrail = True,
        IncludeGlobalServiceEvents = True,
        S3BucketName = Ref(parameters['LogBucket']),
        SnsTopicName = Ref(parameters['SnsTopic'])
    )
    return trail

# Function to write template to specified file
def write_to_file( template ):
    
    # Define the directory to write to as located one level up from the current directory, in a folder named templates
    dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..','templates'))
    
    # Create the directory if it does not exist
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    # Define filename for template equal to name of current script    
    filename = re.sub('\.py$','', sys.argv[0])
    file = os.path.join(dir,filename)
    
    # Write the template to file
    target = open(file + '.json', 'w')
    target.truncate()
    target.write(template)
    target.close()

######################## MAIN BEGINS HERE ###############################
def main(argv):
    
    # Set up a blank template
    t = Template()
    
    # Add description
    t.add_description("[Platform] CloudTrail")

    # Add all defined input parameters to template
    for p in parameters.values():
        t.add_parameter(p)
    
    t.add_resource(gen_cloudtrail())
        
    # Convert template to json
    template=(t.to_json())
    
    # Print template to console (for debugging) and write to file
    print(template)
    write_to_file(template)

if __name__ == "__main__":
    main(sys.argv[0:])
