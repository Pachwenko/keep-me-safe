import json
import os
from python_http_client import UnauthorizedError
import unittest

from keep_me_safe import (
    do_the_thing,
    get_image_urls,
    get_env_variable,
    ParameterNotFound
)
import vcr

my_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)


class TestKeepMeSafe(unittest.TestCase):

    def setUp(self):
        pass

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
        expected_url = (
            '/logos/doodles/2020/60th-anniversary-of-the-greensboro-sit-in-6753651837108277.3-l.png',
        )
        pages = ['https://google.com']
        with open('511_pages.json', 'w+') as f:
            f.write(json.dumps(pages))
        img_id = 'hplogo'

        actual_url = get_image_urls(pages, img_id)

        self.assertEqual(expected_url, actual_url)

    @my_vcr.use_cassette
    def test_get_image_urls_returns_multiple_src_urls(self):
        expected_url = (
            '/logos/doodles/2020/60th-anniversary-of-the-greensboro-sit-in-6753651837108277.3-l.png',
            '/logos/doodles/2020/60th-anniversary-of-the-greensboro-sit-in-6753651837108277.3-l.png',
        )
        pages = ['https://google.com', 'https://google.com']
        with open('511_pages.json', 'w+') as f:
            f.write(json.dumps(pages))
        img_id = 'hplogo'
        actual_url = get_image_urls(pages, img_id)
        self.assertEqual(expected_url, actual_url)

    @my_vcr.use_cassette
    def test_sends_email_throws_unauthorized_error_when_bad_api_key(self):
        os.environ['DESTINATION_EMAIL'] = 'test@example.com'
        os.environ['SENDGRID_API_KEY'] = 'test_api_key'
        with self.assertRaises(UnauthorizedError):
            do_the_thing()
