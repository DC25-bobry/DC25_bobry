# pytest automatically discovers tests based on naming conventions:
# 1. test files should be named either `test_*.py` or `*_test.py`
# 2. Test functions should start with `test_`
# 3. Test classes should start with `Test` and should not have an __init__ method
# following these conventions ensures pytest will find and run all your tests correctly

def test_sanity():
    assert True
