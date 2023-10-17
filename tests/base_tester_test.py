import pytest
from base_tester import BasePytestTester

# pylint: disable=unused-variable


def test_init_subclass_valid_msg_id():
    some_string = "some_string"

    class ValidSubclass(BasePytestTester):
        MSG_ID = some_string

    assert ValidSubclass.MSG_ID == some_string


def test_init_subclass_no_msg_id():
    with pytest.raises(TypeError):

        class NoMsgIDSubclass(BasePytestTester):
            pass


@pytest.mark.parametrize("msg_id", [123, None, ""], ids=lambda x: f"msg_id={x}")
def test_init_subclass_invalid_msg_id_type(msg_id):
    with pytest.raises(TypeError):

        class Subclass(BasePytestTester):
            MSG_ID = msg_id
