from nose.tools import *
from reise.reise import *

#New testing guide:
#To test instance methods without having to instantiate a whole class use this:
#var = object.__new__(class)
#var.instance_function(var)


def test_verify_target_input():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.168.0.13:80'), ('192.168.0.13', 80))


@raises(ValueError)
def test_verify_target_input_bad_ip_range():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.168.0.256:80'), ('192.168.0.13', 80))

@raises(ValueError)
def test_verify_target_input_bad_port():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.168.0.256:ac'), ('192.168.0.13', 80))

@raises(ValueError)
def test_verify_target_input_bad_ip_chars():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.a.0.256:27'), ('192.168.0.13', 80))

@raises(IndexError)
def test_verify_target_input_bad_ip_length():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.5.0.19.12:27'), ('192.5.0.12', 27))

@raises(IndexError)
def test_verify_target_input_bad_ip_length_port():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.5.0.19.12'), ('192.5.0.12', 27))

def test_verify_target_input_bad_ip_whitespace():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy._verify_target_input('192.5.0 .12:27'), ('192.5.0.12', 27))


