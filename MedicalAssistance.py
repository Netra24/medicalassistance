import json
import boto3
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
    
    fileName=''
    # if message is multipart
    if msg.is_multipart():
        multipart_content = {}
        # retrieving form-data
        for part in msg.get_payload():
            if part.get_filename():
                file_name = part.get_filename()
            multipart_content[part.get_param('name', header='content-disposition')] = part.get_payload(decode=True)


    emailid = multipart_content['mailid'].decode("utf-8") 
    pprint(emailid)
    audio = multipart_content['file']
    key = datetime.now().strftime("%m%d%Y%H%M%S")
    fileName = key+file_name
    try:
        data = s3.put_object(
            Bucket="medicalaudiofiles",
            Key=fileName,
            Body=audio,
            Metadata={}
        )
        pprint(datetime.now().strftime("%H:%M:%S"))
        time.sleep(70)
        pprint(datetime.now().strftime("%H:%M:%S"))
        
        sendEmail(fileName, emailid)
        return {
            'statusCode': 200,
            'body': json.dumps('Successful!')
        }
    except BaseException as e:
        print(e)
        raise(e)

def sendEmail(key, emailid):
    key = key.split('.')[0]+'.txt'
    try:
        fileObj = s3.get_object(
            Bucket="medicalreport",
            Key=key
        )
    except BaseException as e:
        print(e)
        raise(e)
    
    file_content = fileObj["Body"].read()

    msg = MIMEMultipart()
    # msg["Subject"] = 'Emergency - Medical Rocord'
    # msg["From"] = 'c.netra@gmail.com'
    # msg["To"] = emailid

    body = """<br>This email is to notify you regarding an emergency."""
    body_txt = MIMEText(body, "html")

    attachment = MIMEApplication(file_content)
    attachment.add_header("Content-Disposition", "attachment", filename=key)

    msg.attach(body_txt)
    msg.attach(attachment)
    try:
        response = ses.send_email(
            Source="c.netra@gmail.com",
            Destination={
                'ToAddresses': [emailid]
            },
            Message={
                'Subject': {
                    'Data': "Emergency - Medical Rocord"
                },
                'Body': {
                    'Html': {
                        'Data': msg.as_string()
                    }
                }
            }
        )
    except BaseException as e:
        print(e)
        raise(e)
    
    # response = ses.send_email(Source = sender, Destinations = [to], Message = {"Data": msg.as_string()})
    pprint(response)

    return