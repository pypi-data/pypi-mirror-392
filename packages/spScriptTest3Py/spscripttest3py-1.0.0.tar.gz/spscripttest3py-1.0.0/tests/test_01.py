from spScriptTest3Py import ScriptTest3


def test_1():
    obj = ScriptTest3()

    arg1 = "blabla"
    assert obj.for_test_only(arg1) == arg1

