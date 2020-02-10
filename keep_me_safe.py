from datetime import datetime
import os

import boto3
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup
from python_http_client.client import Response
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class ParameterNotFound(Exception):
    pass


def get_pages() -> list:
    return [
            "https://lb.511ia.org/ialb/cameras/camera.jsf?id=59169775&view=state&text=m&textOnly=false",  # noqa: E501
    ]


def get_env_variable(parameter_name: str) -> str:
    if not parameter_name or not isinstance(parameter_name, str):
        return ''
    result = os.environ.get(parameter_name)
    if not result:
        raise ParameterNotFound(parameter_name)
    return result


def get_image_data(pages: list, img_id='cam-0-img') -> dict:
    result = {}
    for page_url in pages:
        try:
            traffic_page = requests.get(page_url)
            soup = BeautifulSoup(traffic_page.content, features='html.parser')
            result[page_url] = {
                'src': soup.find(id=img_id)['src'],
                'title': soup.find('title').getText()
            }
        except Exception:
            pass
    return result


def build_html_content(img_urls: dict) -> str:
    result = ''
    for key, value in img_urls.items():
        result += '<p><h2>{}</h2><a href={}><img src={}></a><br/></p>'.format(value['title'], key, value['src'])
    return result


def sendgrid_email(html_content=''):
    message = Mail(from_email=get_env_variable('KEEP_ME_SAFE_SENDER_EMAIL'),
                   to_emails=get_env_variable('KEEP_ME_SAFE_RECIPIENT_EMAIL'),
                   subject='Traffic Conditions Today',
                   html_content=html_content)
    sg = SendGridAPIClient(get_env_variable('SENDGRID_API_KEY'))

    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response


def ses_email(html_content=''):
    SENDER = get_env_variable('KEEP_ME_SAFE_SENDER_EMAIL')
    RECIPIENT = get_env_variable('KEEP_ME_SAFE_RECIPIENT_EMAIL')
    AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', None) or "us-west-2"
    SUBJECT = "Keepin you safe every day. {}".format(datetime.now())
    BODY_TEXT = ("A daily email with current road conditiona over your commute.")
    BODY_HTML = html_content
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        return response


def send_email(html_content='') -> Response:
    # sendgrid_email(html_content)
    return ses_email(html_content)


def do_the_thing(message=None, context=None) -> Response:
    """
    Entrypoint for the app, compatable with AWS lambda

    Uses multiple environment variables:
        KEEP_ME_SAFE_RECIPIENT_EMAIL
        KEEP_ME_SAFE_SENDER_EMAIL
        AWS_DEFAULT_REGION (defaults to us-west-2)
        SENDGRID_API_KEY (unused)

    Also requires aws credentials to be set up if not using SendGrid
    """
    try:
        img_urls = get_image_data(get_pages())
        html_content = build_html_content(img_urls)
        return send_email(html_content)
    except Exception as e:
        print('Got an exception trying to keep you safe.\nException: {}'.format(repr(e)))
        raise


if "__main__" == __name__:
    do_the_thing()
