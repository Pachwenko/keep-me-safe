from bs4 import BeautifulSoup
import os
import requests

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class ParameterNotFound(Exception):
    pass


def get_env_variable(parameter_name: str) -> str:
    if not parameter_name or not isinstance(parameter_name, str):
        return ''
    result = os.environ.get(parameter_name)
    if not result:
        raise ParameterNotFound(parameter_name)
    return result


def do_the_thing() -> None:
    traffic_page = requests.get(
        'https://lb.511ia.org/ialb/cameras/camera.jsf;jsessionid=CDRUfIHRjFD3g-KsTsIcu5xggMRZMM7pZrCqWiUt.ip-10-4-73-18?id=59169258&view=state&text=m&textOnly=false'  # noqa: E501
    )
    soup = BeautifulSoup(traffic_page.content)
    img_url = soup.find(id='cam-0-img')['src']

    message = Mail(
        from_email='keep_me_safe@me_so_safe.com',
        to_emails=get_env_variable('DESTINATION_EMAIL'),
        subject='Traffic Conditions Today',
        html_content='<img src={}>'.format(img_url)
    )
    sg = SendGridAPIClient(get_env_variable('SENDGRID_API_KEY'))

    response = sg.send(message)

    print(response.status_code)
    print(response.body)
    print(response.headers)


if "__main__" == __name__:
    do_the_thing()
