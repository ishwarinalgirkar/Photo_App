import json
import json
import smtplib
import boto3

def lambda_handler(event, context):
    # TODO implement
    send_plain_email(event)
    #sqs_queue()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    print("We did it!")