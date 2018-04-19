# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# April 2 2015, Christian Hopps <chopps@gmail.com>
#
# Copyright (c) 2015-2016, Deutsche Telekom AG.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import absolute_import, division, unicode_literals, print_function, nested_scopes

from decimal import Decimal as D


def channel_itu_to_alu(itu):
    return itu / 2.0 + 31


def channel_alu_to_itu(alu):
    return int((alu - 31) * 2)


def channel_itu_to_cisco(itu):
    cisco = -1 * itu + 61
    return int(cisco)


def channel_cisco_to_itu(cisco):
    itu = -(cisco - 61)
    return int(itu)


def channel_itu_to_huawei(itu):
    huawei = -1 * itu + 60
    return int(huawei)


def channel_huawei_to_itu(huawei):
    itu = -(huawei - 60)
    return int(itu)


def frequency_to_alu_channel(freq):
    """ Convert frequency in GHz to ALU DWDM channel in C-band

    >>> frequency_to_alu_channel(190100)
    1.0
    >>> frequency_to_alu_channel(190150)
    1.5
    >>> frequency_to_alu_channel(197200)
    72.0
    """
    return channel_itu_to_alu(frequency_to_channel(freq))


def frequency_to_channel(freq):
    """ Convert frequency in GHz to ITU DWDM channel in C-band

    >>> frequency_to_channel(193100)
    0
    >>> frequency_to_channel(192750)
    -7
    >>> frequency_to_channel(193550)
    9
    """
    # freq = 193100 + 50 * itu

    itu_channel = (freq - 193100) / 50
    assert itu_channel == int(itu_channel)
    return int(itu_channel)


def alu_channel_to_frequency(channel):
    """ Convert frequency in GHz to ALU DWDM channel in C-band

    >>> alu_channel_to_frequency(1)
    190100
    >>> alu_channel_to_frequency(1.5)
    190150
    >>> alu_channel_to_frequency(72)
    197200
    """
    return channel_to_frequency(channel_alu_to_itu(channel))


def channel_to_frequency(itu_channel):
    """ Convert frequency in GHz to ITU DWDM channel in C-band

    >>> channel_to_frequency(0)
    193100
    >>> channel_to_frequency(-7)
    192750
    >>> channel_to_frequency(9)
    193550
    """
    # freq = 193100 + 50 * itu

    return int(193100 + 50 * itu_channel)


def wavelen_to_frequency(wavelen):
    """Convert a wavelength to a frequency
    >>> wavelen_to_frequency(1577.03)
    190100
    >>> wavelen_to_frequency(1561.42)
    192000
    >>> wavelen_to_frequency(1549.32)
    193500
    >>> wavelen_to_frequency(1548.91)
    193550
    >>> wavelen_to_frequency(1548.71)
    193575
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    c = D(299792458)  # meters per second
    freq = c / D(wavelen)
    # Old way that works, but is 100 we want more precise
    # freq = freq / 100
    # freq = freq.quantize(D('1.')) * 100
    # This may be a better way to support 25, 50, 100 stepping
    # freq = int(freq)
    # freq = ((freq + 4) // 5) * 5
    # return freq
    # This way however gives the best result for 12.5, 25., 50, or 100 stepping
    freq = freq / D('12.5')
    freq = freq.quantize(D('1.')) * D('12.5')
    return int(freq)


def frequency_to_wavelen(freq):
    """Convert a frequency to a wavelength
    >>> frequency_to_wavelen(190100)
    1577.03
    >>> frequency_to_wavelen(192000)
    1561.42
    >>> frequency_to_wavelen(193500)
    1549.32
    >>> frequency_to_wavelen(193550)
    1548.91
    >>> frequency_to_wavelen(193575)
    1548.71
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    hz = D(freq)  # * D(1000) * D(1000) * D(1000)
    c = D(299792458)  # meters per second
    l = c / hz
    #         milli     micro     nano
    l = l  # * (D(1000) * D(1000) * D(1000))
    return float(l.quantize(D('.01')))

    # n=c/l


def frequency_to_wavelen_precise(freq):
    """Convert a frequency to a wavelength with no rounding
    >>> frequency_to_wavelen_precise(190100)
    1577.025
    >>> frequency_to_wavelen_precise(192000)
    1561.4191
    >>> frequency_to_wavelen_precise(193500)
    1549.315
    >>> frequency_to_wavelen_precise(193100)
    1552.5244
    >>> frequency_to_wavelen_precise(193025)
    1553.1276
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    hz = D(freq)  # * D(1000) * D(1000) * D(1000)
    c = D(299792458)  # meters per second
    l = c / hz
    #         milli     micro     nano
    l = l  # * (D(1000) * D(1000) * D(1000))
    return float(l.quantize(D('.0001')))


def wavelen_to_alu_channel(wavelen):
    """Convert a wavelen (nm) to ALU channel
    >>> wavelen_to_alu_channel(1570.42)
    9.0
    >>> wavelen_to_alu_channel(1528.77)
    61.0
    """
    return channel_itu_to_alu(wavelen_to_channel(wavelen))


def wavelen_to_channel(wavelen):
    return frequency_to_channel(wavelen_to_frequency(wavelen))


def alu_channel_to_wavelen(channel):
    """Convert an ALU channel to wavelen (nm)
    >>> alu_channel_to_wavelen(1)
    1577.03
    >>> alu_channel_to_wavelen(48)
    1538.98
    >>> alu_channel_to_wavelen(31)
    1552.52
    """
    return channel_to_wavelen(channel_alu_to_itu(channel))


def channel_to_wavelen(channel):
    return frequency_to_wavelen(channel_to_frequency(channel))


__author__ = 'Christian Hopps'
__date__ = 'April 2 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
