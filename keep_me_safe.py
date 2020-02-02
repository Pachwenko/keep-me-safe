from bs4 import BeautifulSoup
import json
import os
from python_http_client.client import Response
import requests

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
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


def send_email(html_content='') -> Response:
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


def do_the_thing() -> Response:
    """Entrypoint for the app"""
    img_urls = get_image_urls(get_pages())
    html_content = build_html_content(img_urls)
    return send_email(html_content)


if "__main__" == __name__:
    do_the_thing()
