import json
import boto3
import re
import time
import base64
import email
from pprint import pprint
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

s3 = boto3.client('s3')
ses = boto3.client("ses")

def handler(event, context):
    data = base64.b64decode(event['body'])

    content_type = event["headers"]['content-type']
    ct = "Content-Type: "+content_type+"\n"

    # parsing message from bytes
    msg = email.message_from_bytes(ct.encode()+data)

    # if message is multipart
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            if part.get_filename():
                file_name = part.get_filename()
            multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)

    audio = multipart_content['file']
    key = datetime.now().strftime("%m%d%Y%H%M%S")
    fileName = key+'.'+file_name.split('.')[1]
    
    emailid = multipart_content['mailid'].decode("utf-8") 
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(not re.search(regex,emailid)):  
        return {
            'Error': 'Invalid Email ID'
        }
    
    data = s3.put_object(
        Bucket="medicalaudiofiles",
        Key=fileName,
        Body=audio,
        Metadata={'email':emailid}
    )
    
    time.sleep(20)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Report is being generated. Mail will be sent soon!')
    }