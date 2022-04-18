import json
import boto3
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

host = 'search-photos2-uzcqowwehbpuzvdgua5ugk3mqu.us-east-1.es.amazonaws.com'

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()

auth = ('admin', 'Cloud22$')
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

search = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection)

#labels = ['dog', 'cat']


def lambda_handler(event, context):

    
    rawUserInput = event.get('queryStringParameters').get('q')
    print ('event : ', event)

    q1 = event["queryStringParameters"]['q']
    
    if(q1 == "searchAudio" ):
       q1 = convert_speechtotext()
        
    print("q1:", q1 )
    labels = get_labels(q1)
    print("labels", labels)
    
    img_paths = get_photo_path(labels)
    if len(labels) != 0:
        img_paths = get_photo_path(labels)

    return {
        'statusCode': 200,
        'body': json.dumps(img_paths),
        'headers':{
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS'
        }
    }

def get_labels(query):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
         botName='Photo_bot',                 
         botAlias='$LATEST',
         userId="string",           
         inputText=query
     )
    print("lex-response", response)
    
    labels = []
    if 'slots' not in response:
        print("No photo collection for query {}".format(query))
    else:
        print ("slot: ",response['slots'])
        slot_val = response['slots']
        for key,value in slot_val.items():
            if value!=None:
                labels.append(value)
    return labels

def get_photo_path(keys):
    
    resp = []
    for key in keys:
        if (key is not None) and key != '':
            searchData = search.search({"query": {"match": {"labels": key}}})
            resp.append(searchData)
    # print(resp)
    output = []
    for r in resp:
        if 'hits' in r:
             for val in r['hits']['hits']:
                key = val['_source']['objectKey']
                if key not in output:
                    output.append('https://photoscc22.s3.amazonaws.com/'+key)
    print ("MAI YAHA HOON",output)
    return output
    
