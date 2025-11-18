from __future__ import annotations
import unittest, types
import pyquoks.data, pyquoks.utils


class TestCase(unittest.TestCase, pyquoks.utils._HasRequiredAttributes):
    """
    Class for performing unit testing

    **Required attributes**::

        _MODULE_NAME = __name__

    Attributes:
        _MODULE_NAME: Name of the testing module
    """

    _REQUIRED_ATTRIBUTES = {
        "_MODULE_NAME"
    }

    _MODULE_NAME: str

    def __init__(self, *args, **kwargs) -> None:
        self._check_attributes()

        super().__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls) -> None:
        cls._logger = pyquoks.data.LoggerService(
            filename=__name__,
        )

    def _get_func_name(self, func_name: str) -> str:
        return f"{self._MODULE_NAME}.{func_name}"

    def assert_equal(
            self,
            func_name: str,
            test_data: object,
            test_expected: object,
    ) -> None:
        self._logger.info(
            msg=(
                f"{self._get_func_name(func_name)}:\n"
                f"Data: {test_data}\n"
                f"Expected: {test_expected}\n"
            ),
        )

        try:
            self.assertEqual(
                first=test_data,
                second=test_expected,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True,
            )

    def assert_type(
            self,
            func_name: str,
            test_data: object,
            test_type: type | types.UnionType,
    ) -> None:
        self._logger.info(
            msg=(
                f"{self._get_func_name(func_name)}:\n"
                f"Type: {type(test_data).__name__}\n"
                f"Expected: {test_type.__name__}\n"
            ),
        )

        try:
            self.assertIsInstance(
                obj=test_data,
                cls=test_type,
            )
        except Exception as exception:
            self._logger.log_error(
                exception=exception,
                raise_again=True,
            )
