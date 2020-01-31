import os
import pytest

from keep_me_safe import get_env_variable, ParameterNotFound


class TestKeepMeSafe:

    def test_raises_parmeter_not_found_when_no_destination_email(self):
        parameter_name = 'abcdefg'
        with pytest.raises(ParameterNotFound):
            get_env_variable(parameter_name)

    def test_gets_parameter_when_set(self):
        parameter_name = 'abcdefg'
        expected_parameter = 'test_variable'
        os.environ[parameter_name] = expected_parameter
        assert expected_parameter == get_env_variable(parameter_name)

    def test_returns_none_when_parameter_name_is_wrong_type(self):
        parameter_name = []
        assert None is get_env_variable(parameter_name)
        parameter_name = {}
        assert None is get_env_variable(parameter_name)
        parameter_name = 1
        assert None is get_env_variable(parameter_name)
