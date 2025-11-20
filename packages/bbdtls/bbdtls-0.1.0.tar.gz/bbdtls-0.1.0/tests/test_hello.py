import pytest
from bbdtls.hello import hello

# Test the hello function
def test_hello():
    assert hello("Tom") == "Hello, Tom!"
