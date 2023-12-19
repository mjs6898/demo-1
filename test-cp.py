import boto3
import time
import sys
import os


stack_name = f"SimpleS3Stack-{int(time.time())}"

 
# Initialize Boto3 CloudFormation client


template_file_path = sys.argv[1]

def assume_member_account_role(account_id):
    # Read temporary credentials from readonly role
    sts = boto3.client("sts")

    try:
        response = sts.assume_role(
            RoleArn="arn:aws:iam::178273572362:role/Assume-role-test-4",
            RoleSessionName=f"cfn-{account_id}"
        )
        temp_credentials = response['Credentials']
        # Use the temporary credentials to create a new session
        target_session = boto3.Session(
            aws_access_key_id=temp_credentials['AccessKeyId'],
            aws_secret_access_key=temp_credentials['SecretAccessKey'],
            aws_session_token=temp_credentials['SessionToken'],
            region_name='ap-southeast-2'
        )
        return target_session
    except Exception as e:
        print(f"Error assuming role in account {account_id}: {str(e)}")
        return None
def create_resource(account_id):

    cf_client = boto3.client('cloudformation')

    try:
    # Create the CloudFormation stack using the provided template file
        response = cf_client.create_stack(
            StackName=stack_name,
            TemplateBody=open(template_file_path, 'r').read(),
            Capabilities=['CAPABILITY_IAM']
        )
        print(f"S3 stack {stack_name} creation initiated. StackId: {response['StackId']}")
        return response
    except Exception as e:
        print(f"Error creating S3 stack: {str(e)}")
        return None


# Get target account list from env var
account_input_string = os.getenv("ACCOUNT_ID_LIST")
account_output_string = account_input_string.replace(" ","")
account_list = account_output_string.split(',')

for account_id in account_list:
    assumed_session = assume_member_account_role(account_id)
    if assumed_session:
       print('ASSUMED ROLE')
    else:
        print(f"Unable to create or update in account due to assume role issue")

    resources_created = create_resource(account_id)
    if resources_created:
        print("resource creation is success")
    else:
        print("resource creation failed")
   
