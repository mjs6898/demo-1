import boto3
import sys
import time
 
# Define the stack name with a timestamp
stack_name = f"SimpleS3Stack-{int(time.time())}"
# stack_name = "python-cf-stack"
 
# Initialize Boto3 CloudFormation client
cf_client = boto3.client('cloudformation')
 
# Get the path to the CloudFormation template file from the command line arguments
template_file_path = sys.argv[1]
 
try:
    # Create the CloudFormation stack using the provided template file
    response = cf_client.create_stack(
        StackName=stack_name,
        TemplateBody=open(template_file_path, 'r').read(),
        Capabilities=['CAPABILITY_IAM']
    )
    print(f"S3 stack {stack_name} creation initiated. StackId: {response['StackId']}")
except Exception as e:
    print(f"Error creating S3 stack: {str(e)}")
