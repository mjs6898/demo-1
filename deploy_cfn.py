import boto3
import time
import os

def assume_member_account_role(account_id):
    # Read temporary credentials from readonly role
    sts = boto3.client("sts")

    try:
        response = sts.assume_role(
            RoleArn=f"arn:aws:iam::{account_id}:role/CFNDeployRole",
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


def create_update_stack(stack_name, assumed_session, account_id):
    # Check if the stack already exists

    cf_client = assumed_session.client('cloudformation')
    try:
        cf_client.describe_stacks(StackName=stack_name)
        stack_exists = True
    except cf_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            stack_exists = False
        else:
            print(f"Error checking stack {stack_name} existence in account {account_id}: {str(e)}")


    # Read the template file content
    try:
        with open(template_file_path, 'r') as template_file:
            template_body = template_file.read()
    except Exception as e:
        print(f"Error reading template file in account {account_id}: {str(e)}")


    # If the stack exists, update it; otherwise, create it
    if stack_exists:
        try:
            # Update the stack
            cf_client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM','CAPABILITY_IAM']
            )
            print(f'Updating stack {stack_name} in account {account_id}')
        except cf_client.exceptions.ClientError as e:
            print(f"Error updating stack {stack_name} in account {account_id}: {str(e)}")
    else:
        try:
            # Create the stack
            cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Capabilities=['CAPABILITY_NAMED_IAM','CAPABILITY_IAM']
            )
            print(f'Creating stack {stack_name} in account {account_id}')
        except cf_client.exceptions.ClientError as e:
            print(f"Error creating stack {stack_name} in account {account_id}: {str(e)}")

def describe_stack_status(stack_name, assumed_session,account_id):
    client = assumed_session.client('cloudformation')
    try:
        response = client.describe_stacks(StackName=stack_name)
        return response['Stacks'][0]['StackStatus']
    except client.exceptions.ClientError as e:
        print(f"Error describing stack {stack_name} in account {account_id}: {str(e)}")
        return None

def check_stack_status(stack_name, assumed_session, account_id):
    while True:
        stack_status = describe_stack_status(stack_name, assumed_session,account_id)

        if stack_status is None:
            print(f"Unable to describe the stack {stack_name} status in account {account_id} due to creation error")
            failed_accounts.append(account_id)
            break

        if stack_status == 'CREATE_COMPLETE' or stack_status == 'UPDATE_COMPLETE':
            print(f"Stack {stack_name} lastest status in account {account_id} is a success.")
            success_accounts.append(account_id)
            break
        elif 'IN_PROGRESS' in stack_status:
            print(f"Stack deployment is in progress in account {account_id}. Waiting for 10 seconds...")
            time.sleep(10)
        else:
            print(f"The CloudFormation stack {stack_name} is in a failed state in account {account_id}. Status: {stack_status}")
            failed_accounts.append(account_id)
            break


# Get target account list from env var
account_input_string = os.getenv("ACCOUNT_ID_LIST")
account_output_string = account_input_string.replace(" ","")
account_list = account_output_string.split(',')


# Get template name from env var
template_name = os.getenv("CFN_NAME") 
current_dir = os.path.dirname(os.path.realpath(__file__))
template_file_path = os.path.join(current_dir, "..", "cloudformation","templates", template_name)
stack_name = template_name.split('.')[0]



# Create or update cloudformation stack
success_accounts = []
failed_accounts = []


for account_id in account_list:
    assumed_session = assume_member_account_role(account_id)
    if assumed_session:
        create_update_stack(stack_name, assumed_session, account_id)
    else:
        print(f"Unable to create or update {stack_name} in account {account_id} due to assume role issue")
        failed_accounts.append(account_id)

# Check cloudformation stack status
for account_id in account_list:
    assumed_session = assume_member_account_role(account_id)
    if assumed_session:
        check_stack_status(stack_name, assumed_session, account_id)

print(f"Stack deployment completed successfully for those accounts: {success_accounts}")
print(f"Stack deployment failed for those accounts: {failed_accounts}")

