import os

from moto.ses import ses_backend
from bs4 import BeautifulSoup
from moto import mock_ses
from python_http_client import UnauthorizedError
import unittest

from keep_me_safe import (
    do_the_thing,
    get_image_data,
    get_env_variable,
    get_pages,
    build_html_content,
    sendgrid_email,
    ses_email,
    ParameterNotFound
)
import vcr

my_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)


class KeepMeSafeUnitTests(unittest.TestCase):

    def setUp(self):
        self.expected_src_url = 'http://205.221.66.10/axis/DMTV20.jpg'
        self.parameter_name = 'abcdefg'

    def tearDown(self):
        try:
            del os.environ[self.parameter_name]
        except KeyError:
            pass

    def test_raises_parmeter_not_found_when_no_destination_email(self):
        with self.assertRaises(ParameterNotFound):
            get_env_variable(self.parameter_name)

    def test_gets_parameter_when_set(self):
        expected_parameter = 'test_variable'
        os.environ[self.parameter_name] = expected_parameter

        actual_parameter = get_env_variable(self.parameter_name)

        self.assertEqual(expected_parameter, actual_parameter)

    def test_returns_empty_string_when_parameter_name_is_wrong_type(self):
        parameter_name = []
        self.assertEqual('', get_env_variable(parameter_name))

    @my_vcr.use_cassette
    def test_get_image_data_returns_multiple_src_urls(self):
        expected_src_urls = {
            'https://google.com': {
                'src': '/images/branding/googlelogo/1x/googlelogo_white_background_color_272x92dp.png',
                'title': 'Google'
            }
        }
        pages = ['https://google.com', 'https://google.com']
        img_id = 'hplogo'

        actual_urls = get_image_data(pages, img_id)

        self.assertEqual(expected_src_urls, actual_urls)

    @my_vcr.use_cassette
    def test_get_image_data_returns_correct_data(self):
        pages = get_pages()
        expected_data = {
            pages[0]: {
                'src': self.expected_src_url,
                'title': 'Iowa Department of Transportation Traveler Information - Low Bandwidth Web - Camera - DM - I-35/80 @ Hwy 141 (20)'  # noqa: E501
            }
        }

        actual_data = get_image_data([pages[0]])

        self.assertEqual(expected_data[pages[0]]['src'], actual_data[pages[0]]['src'])
        self.assertEqual(expected_data[pages[0]]['title'], actual_data[pages[0]]['title'])

    def test_build_html_content_returns_right_data(self):
        expected_src_url = self.expected_src_url
        expected_page = 'https://google.com'
        expected_title = 'Google'
        img_data = {
            expected_page: {
                'src': expected_src_url,
                'title': expected_title
                }
        }

        actual_html = build_html_content(img_data)
        soup = BeautifulSoup(actual_html)
        actual_src_url = soup.find('img')['src']
        actual_title = soup.find('h2').getText()
        actual_page = soup.find('img').parent['href']

        self.assertEqual(expected_src_url, actual_src_url)
        self.assertEqual(expected_page, actual_page)
        self.assertEqual(expected_title, actual_title)

    @my_vcr.use_cassette
    def test_sendgrid_email_throws_unauthorized_error_when_bad_api_key(self):
        os.environ['KEEP_ME_SAFE_RECIPIENT_EMAIL'] = 'test1@example.com'
        os.environ['KEEP_ME_SAFE_SENDER_EMAIL'] = 'test2@example.com'
        os.environ['SENDGRID_API_KEY'] = 'test_api_key'

        with self.assertRaises(UnauthorizedError):
            sendgrid_email()

    @mock_ses
    def test_ses_send_email(self):
        os.environ['KEEP_ME_SAFE_RECIPIENT_EMAIL'] = 'test1@example.com'
        os.environ['KEEP_ME_SAFE_SENDER_EMAIL'] = 'test2@example.com'
        ses_email('<p>Hello SES</p>')

    @mock_ses
    def test_do_the_thing_with_verified_email(self):
        ses_backend.verify_domain('example.com')
        ses_backend.verify_email_address('test2@example.com')
        os.environ['KEEP_ME_SAFE_RECIPIENT_EMAIL'] = 'test1@example.com'
        os.environ['KEEP_ME_SAFE_SENDER_EMAIL'] = 'test2@example.com'
        expected_status_code = 200

        response = do_the_thing()
        actual_status_code = response['ResponseMetadata']['HTTPStatusCode']

        self.assertEqual(expected_status_code, actual_status_code)

    @mock_ses
    def test_do_the_thing_throws_exception_on_missing_environment_variable(self):
        os.environ['KEEP_ME_SAFE_RECIPIENT_EMAIL'] = 'test1@example.com'

        with self.assertRaises(ParameterNotFound):
            do_the_thing('<p>Hello SES</p>')
