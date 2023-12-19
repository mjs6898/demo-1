import boto3
import sys


 
def assume_role(org_role_arn, session_name):
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=org_role_arn,
        RoleSessionName=session_name
    )
    return response['Credentials']
 
def create_cloudformation_stack(stack_name, template_file, credentials):
    cloudformation_client = boto3.client(
        'cloudformation',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )
 
    with open(template_file, 'r') as file:
        template_body = file.read()
 
    response = cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
 
    return response
 
# Replace with your actual values
org_role_arn =  "arn:aws:iam::178273572362:role/Assume-role-test-4"
session_name = 'AssumeRoleSession'
stack_name = 'YourStackName'
template_file_path = sys.argv[1]
 
# Step 1: Assume role in the organization account
credentials = assume_role(org_role_arn, session_name)
 
# Step 2: Create CloudFormation stack in the member account
response = create_cloudformation_stack(stack_name, template_file_path, credentials)
 
# Optional: Wait for the stack to be created
cloudformation_client = boto3.client('cloudformation')
cloudformation_client.get_waiter('stack_create_complete').wait(StackName=stack_name)
 
print("CloudFormation stack created successfully.")
