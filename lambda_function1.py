import json
import os
import time
import logging
import boto3
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

rekognition = boto3.client('rekognition')

host = 'search-photos2-uzcqowwehbpuzvdgua5ugk3mqu.us-east-1.es.amazonaws.com'

auth = ('admin', 'Cloud22$')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)



def lambda_handler(event, context):

    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    #logger.debug(credentials)
    records = event['Records']
    #print(records)
    s3 = boto3.client('s3')

    for record in records:

        s3object = record['s3']
        bucket = s3object['bucket']['name']
        objectKey = s3object['object']['key']
        metadata = s3.head_object(Bucket=bucket, Key=objectKey)
        
        print("META", metadata)

        image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : objectKey
            }
        }

        response = rekognition.detect_labels(Image = image, MaxLabels=10, MinConfidence=50)
        print("IMAGE LABELS", format(response['Labels']))
        labels = list(map(lambda x : x['Name'], response['Labels']))
        timestamp = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')
        
        if metadata["Metadata"]:
            customlabels = (metadata["Metadata"]["customlabels"]).split(",")
        
        if metadata["Metadata"]:
            for c_labels in customlabels:
                c_labels = c_labels.strip()
                c_labels = c_labels.lower()
                if c_labels not in labels:
                    labels.append(c_labels)
                    
        
        esObject = json.dumps({
            'objectKey' : objectKey,
            'bucket' : bucket,
            'createdTimestamp' : timestamp,
            'labels' : labels
        })
        
        print("LABELS", labels)

        es.index(index = "photos", doc_type = "Photo", id = objectKey, body = esObject, refresh = True)
        
        print("DONE")


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
