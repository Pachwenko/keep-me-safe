from bs4 import BeautifulSoup
import os
import requests

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
destination_email = os.environ.get('KEEP_ME_SAFE_EMAIL')

traffic_page = requests.get('https://lb.511ia.org/ialb/cameras/camera.jsf;jsessionid=CDRUfIHRjFD3g-KsTsIcu5xggMRZMM7pZrCqWiUt.ip-10-4-73-18?id=59169258&view=state&text=m&textOnly=false')
soup = BeautifulSoup(traffic_page.content)
img_url = soup.find(id='cam-0-img')['src']

message = Mail(
    from_email='keep_me_safe@me_so_safe.com',
    to_emails=destination_email,
    subject='Traffic Conditions Today',
    html_content='<img src={}>'.format(img_url)
)
sg = SendGridAPIClient(SENDGRID_API_KEY)

response = sg.send(message)

print(response.status_code)
print(response.body)
print(response.headers)