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
    frag_pack = '1#30#\nCopyright (C) 2012  sir2#30#Mackk\n\nThis program is f3#30#ree ' \
    'software; you can re4#30#distribute it and/or\nmod5#30#ify it under the terms o6#30#f' \
    ' the GNU General Public7#30# License\nas published by8#30# the Free Software ' \
    'Found9#30#ation; either version 2\n10#30#of the License, or (at y11#30#our option) any ' \
    'later ve12#30#rsion.\n\nThis program is 13#30#distributed in the hope 14#30#that it ' \
    'will be useful,\n15#30#but WITHOUT ANY WARRANTY16#30#; without even the impli17#30#ed ' \
    'warranty of\nMERCHANTA18#30#BILITY or FITNESS FOR A 19#30#PARTICULAR PURPOSE.  '\
    'See20#30# the\nGNU General Public 21#30#License for more details22#30#.\n\nYou should ' \
    'have recei23#30#ved a copy of the GNU Ge24#30#neral Public License\nalo25#30#ng with '\
    'this program; if26#30# not, write to the Free 27#30#Software\nFoundation, '\
    'Inc28#30#., 51 Franklin Street, F29#30#ifth Floor, Boston, MA  30#30#02110-1301, USA.'

    packet_frags = []
    for i in cthread.fragment_and_sequence(packet):
        packet_frags.append(i)
    assert_equal(''.join(packet_frags), frag_pack)



