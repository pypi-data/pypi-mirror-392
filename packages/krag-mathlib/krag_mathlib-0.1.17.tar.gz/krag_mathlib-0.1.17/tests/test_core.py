from krag_mathlib.core import add, subtract, multiply, divide, exponent, log

def test_add():
    assert add(1, 2) == 3

def test_substraction():
    assert subtract(3, 2) == 1
    
def test_multiply():
    assert multiply(4 ,5) == 20
    
def test_divide():
    assert divide(4 ,5) == 0.8

def test_exponent():
    assert exponent(4 ,5) == 1024
    
def test_log():
    assert log(8 ,2) == 3