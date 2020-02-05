import json
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
    result = []
    with open('511_pages.json', 'r') as f:
        result = json.loads(f.read())
        if not isinstance(result, list):
            return []
    return result


def get_env_variable(parameter_name: str) -> str:
    if not parameter_name or not isinstance(parameter_name, str):
        return ''
    result = os.environ.get(parameter_name)
    if not result:
        raise ParameterNotFound(parameter_name)
    return result


def get_image_urls(pages: list, img_id='cam-0-img') -> dict:
    result = {}
    for page in pages:
        traffic_page = requests.get(page)
        soup = BeautifulSoup(traffic_page.content)
        result[page] = (soup.find(id=img_id)['src'])
    return result


def build_html_content(img_urls: dict) -> str:
    result = ''
    for key, value in img_urls.items():
        result += '<a href={}><img src={}></a><br/>'.format(key, value)
    return result


def sendgrid_email(html_content=''):
    """
    Requires 2 environment variables to be set:
        KEEP_ME_SAFE_EMAIL and SENDGRID_API_KEY
    """
    message = Mail(
        from_email='keep_me_safe@me_so_safe.com',
        to_emails=get_env_variable('KEEP_ME_SAFE_EMAIL'),
        subject='Traffic Conditions Today',
        html_content=html_content
    )
    sg = SendGridAPIClient(get_env_variable('SENDGRID_API_KEY'))

    response = sg.send(message)
    print(type(response))
    print(response.status_code)
    print(response.body)
    print(response.headers)
    return response


def ses_email(html_content=''):

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = get_env_variable('KEEP_ME_SAFE_EMAIL')

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = get_env_variable('KEEP_ME_SAFE_EMAIL')

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', None) or "us-west-2"

    # The subject line for the email.
    SUBJECT = "Amazon SES Test (SDK for Python)"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("")

    # The HTML body of the email.
    BODY_HTML = html_content
    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
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
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def send_email(html_content='') -> Response:
    # sendgrid_email(html_content)
    ses_email(html_content)


def do_the_thing() -> Response:
    """Entrypoint for the app"""
    img_urls = get_image_urls(get_pages())
    html_content = build_html_content(img_urls)
    return send_email(html_content)


if "__main__" == __name__:
    do_the_thing()
