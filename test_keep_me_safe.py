from bs4 import BeautifulSoup
import os
from python_http_client import UnauthorizedError
import unittest

from keep_me_safe import (
    # do_the_thing,
    get_image_urls,
    get_env_variable,
    build_html_content,
    send_email,
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
        self.expected_src_url = '/logos/doodles/2020/60th-anniversary-of-the-greensboro-sit-in-6753651837108277.3-l.png'  # noqa: E501

    def tearDown(self):
        try:
            del os.environ['abcdefg']
        except KeyError:
            pass

    def test_raises_parmeter_not_found_when_no_destination_email(self):
        parameter_name = 'abcdefg'

        with self.assertRaises(ParameterNotFound):
            get_env_variable(parameter_name)

    def test_gets_parameter_when_set(self):
        parameter_name = 'abcdefg'
        expected_parameter = 'test_variable'
        os.environ[parameter_name] = expected_parameter

        self.assertEqual(expected_parameter, get_env_variable(parameter_name))

    def test_returns_none_when_parameter_name_is_wrong_type(self):
        parameter_name = []
        self.assertEqual('', get_env_variable(parameter_name))

    @my_vcr.use_cassette
    def test_get_pages_reads_from_511_pages_json_file(self):
        expected_src_url = {
            'https://google.com': self.expected_src_url,
        }
        pages = ['https://google.com']
        img_id = 'hplogo'

        actual_url = get_image_urls(pages, img_id)

        self.assertEqual(expected_src_url, actual_url)

    @my_vcr.use_cassette
    def test_get_image_urls_returns_multiple_src_urls(self):
        expected_src_urls = {
            'https://google.com': self.expected_src_url
        }
        pages = ['https://google.com', 'https://google.com']
        img_id = 'hplogo'

        actual_url = get_image_urls(pages, img_id)

        self.assertEqual(expected_src_urls, actual_url)

    def test_build_html_content_returns_right_data(self):
        expected_src_url = self.expected_src_url
        expected_page = 'https://google.com'
        img_urls = {expected_page: expected_src_url}

        actual_html = build_html_content(img_urls)

        soup = BeautifulSoup(actual_html)
        self.assertEqual(expected_src_url, soup.find('img')['src'])
        self.assertEqual(expected_page, soup.find('img').parent['href'])

    @my_vcr.use_cassette
    def test_sends_email_throws_unauthorized_error_when_bad_api_key(self):
        os.environ['KEEP_ME_SAFE_EMAIL'] = 'test@example.com'
        os.environ['SENDGRID_API_KEY'] = 'test_api_key'

        with self.assertRaises(UnauthorizedError):
            send_email()


# class KeepMeSafeIntegrationTests(unittest.TestCase):

#     @vcr.use_cassette
#     def test_do_the_thing_works(self):
#         expected_status_code = 202

#         actual_response = do_the_thing()

#         self.assertEqual(expected_status_code, actual_response.status_code)
