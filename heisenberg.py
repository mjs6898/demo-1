import boto3
import time
import sys
import os



account_input_string = os.getenv("ACCOUNT_ID_LIST")
account_output_string = account_input_string.replace(" ","")
account_list = account_output_string.split(',')

success_accounts = []
failed_accounts = []


for account_id in account_list:
  print(account_id)
  print("my name is heisenberg")
   
