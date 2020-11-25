import json
import boto3
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

s3 = boto3.client('s3')
ses = boto3.client("ses")

def handler(event, context):
    data = event['body']
    email = data['email']
    audio = data['file']['body'].read()
    key = datetime.now().strftime("%m%d%Y%H%M%S")
    fileName = key+data['headers']['content-type']
    try:
        data = s3.put_object(
            Bucket="medicalaudiofiles",
            Key=fileName,
            Body=audio,
            Metadata={}
        )
    except BaseException as e:
        print(e)
        raise(e)

    time.sleep(70)
    
    sendEmail(key, email)
    return {"message": "Successfully executed"}

def sendEmail(key, email):
    key = key+'.txt'
    try:
        fileObj = s3.get_object(
            Bucket="medicalreport",
            Key=key
        )
    except BaseException as e:
        print(e)
        raise(e)
    
    file_content = fileObj["Body"].read()

    sender = "c.netra@gmail.com"
    to = email
    subject = 'Emergency - Medical Rocord'
    body = "This email is to notify you regarding an emergency."

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    body_txt = MIMEText(body, "text")

    attachment = MIMEApplication(file_content)
    attachment.add_header("Content-Disposition", "attachment", filename=object)

    msg.attach(body_txt)
    msg.attach(attachment)

    try:
        data = ses.send_email(
            Source="c.netra@gmail.com",
            Destination={
                'ToAddresses': email
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
    return "Thanks"