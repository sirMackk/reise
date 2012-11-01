from nose.tools import *
from reise.reise import *

#New testing guide:
#To test instance methods without having to instantiate a whole class use this:
#var = object.__new__(class)
#var.instance_function(var)


def test_verify_target_input():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.168.0.13:80'), ('192.168.0.13', 80))


@raises(ValueError)
def test_verify_target_input_bad_ip_range():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.168.0.256:80'), ('192.168.0.13', 80))

@raises(ValueError)
def test_verify_target_input_bad_port():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.168.0.256:ac'), ('192.168.0.13', 80))

@raises(ValueError)
def test_verify_target_input_bad_ip_chars():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.a.0.256:27'), ('192.168.0.13', 80))

@raises(IndexError)
def test_verify_target_input_bad_ip_length():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.5.0.19.12:27'), ('192.5.0.12', 27))

@raises(IndexError)
def test_verify_target_input_bad_ip_length_port():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.5.0.19.12'), ('192.5.0.12', 27))

def test_verify_target_input_bad_ip_whitespace():
    proxy = object.__new__(reise.tcpProxy)
    assert_equal(proxy.verify_target_input('192.5.0 .12:27'), ('192.5.0.12', 27))


def test_fragment_and_sequence():
    '''Example test for the fragment_and_sequence function.
    Have to work more on this to really make sure I'm getting
    exactly what I want.
    '''
    cthread = object.__new__(reise.ClientThread)
    cthread.SIZE = 24
    packet = '''
Copyright (C) 2012  sirMackk

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.'''
    frag_pack = '001030\nCopyright (C) 2012  sir002030Mackk\n\nThis program is f003030ree ' \
    'software; you can re004030distribute it and/or\nmod005030ify it under the terms o006030f' \
    ' the GNU General Public007030 License\nas published by008030 the Free Software ' \
    'Found009030ation; either version 2\n010030of the License, or (at y011030our option) any ' \
    'later ve012030rsion.\n\nThis program is 013030distributed in the hope 014030that it ' \
    'will be useful,\n015030but WITHOUT ANY WARRANTY016030; without even the impli017030ed ' \
    'warranty of\nMERCHANTA018030BILITY or FITNESS FOR A 019030PARTICULAR PURPOSE.  '\
    'See020030 the\nGNU General Public 021030License for more details022030.\n\nYou should ' \
    'have recei023030ved a copy of the GNU Ge024030neral Public License\nalo025030ng with '\
    'this program; if026030 not, write to the Free 027030Software\nFoundation, '\
    'Inc028030., 51 Franklin Street, F029030ifth Floor, Boston, MA  03003002110-1301, USA.'

    packet_frags = []
    for i in cthread.fragment_and_sequence(packet):
        packet_frags.append(i)
    assert_equal(''.join(packet_frags), frag_pack)



