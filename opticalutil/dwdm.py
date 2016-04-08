# -*- coding: utf-8 -*-#
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


def channel_itu_to_alu (itu):
    return itu / 2.0 + 31


def channel_alu_to_itu (alu):
    return int((alu - 31) * 2)


def channel_itu_to_cisco (itu):
    cisco = -1 * itu + 61
    return int(cisco)


def channel_cisco_to_itu (cisco):
    itu = -(cisco - 61)
    return int(itu)


def channel_itu_to_huawei (itu):
    huawei = -1 * itu + 60
    return int(huawei)


def channel_huawei_to_itu (huawei):
    itu = -(huawei - 60)
    return int(itu)


def frequency_to_alu_channel (freq):
    """ Convert frequency in GHz to DWDM channel in C-band

    >>> frequency_to_alu_channel(190100)
    1.0
    >>> frequency_to_alu_channel(190150)
    1.5
    >>> frequency_to_alu_channel(197200)
    72.0
    """
    return channel_itu_to_alu(frequency_to_channel(freq))


def frequency_to_channel (freq):
    """ Convert frequency in GHz to DWDM channel in C-band

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


def alu_channel_to_frequency (channel):
    """ Convert frequency in GHz to DWDM channel in C-band

    >>> alu_channel_to_frequency(1)
    190100
    >>> alu_channel_to_frequency(1.5)
    190150
    >>> alu_channel_to_frequency(72)
    197200
    """
    return channel_to_frequency(channel_alu_to_itu(channel))


def channel_to_frequency (itu_channel):
    """ Convert frequency in GHz to DWDM channel in C-band

    >>> channel_to_frequency(0)
    193100
    >>> channel_to_frequency(-7)
    192750
    >>> channel_to_frequency(9)
    193550
    """
    # freq = 193100 + 50 * itu

    return int(193100 + 50 * itu_channel)


def wavelen_to_frequency (wavelen):
    """Convert a frequency to a wavelength
    >>> wavelen_to_frequency(1577.03)
    190100
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    c = D(299792458) # meters per second
    freq = c / D(wavelen)
    # freq = freq / D('12.5')
    # freq = freq.quantize(D('1.')) * D('12.5')
    freq = freq.quantize(D('1.'))
    return int(freq)


def frequency_to_wavelen (freq):
    """Convert a frequency to a wavelength
    >>> frequency_to_wavelen(190100)
    1577.03
    >>> frequency_to_wavelen(192000)
    1561.42
    >>> frequency_to_wavelen(193500)
    1549.32
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    hz = D(freq) # * D(1000) * D(1000) * D(1000)
    c = D(299792458) # meters per second
    l = c / hz
    #         milli     micro     nano
    l = l # * (D(1000) * D(1000) * D(1000))
    return float(l.quantize(D('.01')))

    # n=c/l


def frequency_to_wavelen_precise (freq):
    """Convert a frequency to a wavelength
    >>> frequency_to_wavelen(190100)
    1577.03
    >>> frequency_to_wavelen(192000)
    1561.42
    >>> frequency_to_wavelen(193500)
    1549.32
    """
    # l=c/n
    #    GHz        MHz       KHz         Hz
    hz = D(freq) # * D(1000) * D(1000) * D(1000)
    c = D(299792458) # meters per second
    l = c / hz
    #         milli     micro     nano
    l = l # * (D(1000) * D(1000) * D(1000))
    return float(l.quantize(D('.0001')))


def wavelen_to_alu_channel (wavelen):
    """Convert a wavelen (nm) to channel
    >>> wavelen_to_alu_channel(1570.42)
    9.0
    >>> wavelen_to_alu_channel(1528.77)
    61.0
    """
    return channel_itu_to_alu(wavelen_to_channel(wavelen))


def wavelen_to_channel (wavelen):
    return frequency_to_channel(wavelen_to_frequency(wavelen))


def alu_channel_to_wavelen (channel):
    """Convert a channel to wavelen (nm)
    >>> alu_channel_to_wavelen(1)
    1577.03
    >>> alu_channel_to_wavelen(48)
    1538.98
    >>> alu_channel_to_wavelen(31)
    1552.52
    """
    return channel_to_wavelen(channel_alu_to_itu(channel))


def channel_to_wavelen (channel):
    return frequency_to_wavelen(channel_to_frequency(channel))


__author__ = 'Christian Hopps'
__date__ = 'April 2 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
