# -*- coding: utf-8 eval: (yapf-mode 1) -*-
#
# January 21 2015, Christian Hopps <chopps@gmail.com>
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
from functools import total_ordering
from decimal import Context, Decimal, ROUND_HALF_EVEN

#
# dB = 10log(P1mw/P2mw)     -- ratio comparing 2 power values
# dBm = 10 * log10(Pmw/1mw) -- absolute power value in dBm
# Pmw = mW * 10^(PdBm/10)   -- absolute value in milliwatts
#
# dBm/10 = log10(Pmw/1mw)
# 10^(dBm/10) = Pmw/1mw
# 1mw * 10^(dBm/10) = Pmw
#

D = Decimal
PPREC = 6
SIXPLACES = Decimal(10) ** -6
pcontext = Context(rounding=ROUND_HALF_EVEN, Emin=-10000000, Emax=10000000)


def mwatt2db(mwatt):
    db = D(10, pcontext) * D(mwatt).log10(pcontext)
    db = db.quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)
    return db


def db2mwatt(db):
    rv = Decimal(10 ** (db / 10), pcontext)
    rv = rv.quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)
    return rv


def combiner(thrupower, tappower, thrupct, firsttap):
    assert thrupct >= D(.5)

    # First tap
    tappower = Power.from_mwatt((tappower - Gain(.5)).mwatt() * firsttap)

    wthruout = (thrupower - Gain(.5)).mwatt() * thrupct
    wtapout = (tappower - Gain(.5)).mwatt() * D((1 - thrupct) / 2)

    return Power.from_mwatt(wthruout + wtapout)


class Decibel(object):
    @classmethod
    def from_factor(cls, gain_factor, context=pcontext):
        """Create a Decibel object give the gain factor.
        >>> Decibel.from_factor(1)
        Decibel('0.000000')
        >>> Decibel.from_factor(3)
        Decibel('4.771213')
        """
        return cls(mwatt2db(gain_factor))

    @classmethod
    def from_10ths_db(cls, inval):
        """
        >>> dB = Decibel.from_10ths_db(22)
        >>> str(dB)
        '2.20'
        >>> dB = Decibel.from_10ths_db(None)
        >>> str(dB)
        '*'
        """
        if inval is None:
            dB = None
        else:
            dB = Decibel(inval).dB / D(10)
        return cls(dB)

    @classmethod
    def from_100ths_db(cls, inval):
        """
        >>> dB = Decibel.from_100ths_db(202)
        >>> str(dB)
        '2.02'
        >>> dB = Decibel.from_10ths_db(None)
        >>> str(dB)
        '*'
        """
        if inval is None:
            dB = None
        else:
            dB = D(inval) / D(100)
        return cls(dB)

    def __init__(self, dB):
        if dB is None:
            self.dB = None
        else:
            try:
                dB = dB.replace('dB', '')
            except AttributeError:
                pass
            if isinstance(dB, Decibel):
                self.dB = dB.dB
            else:
                self.dB = Decimal(dB).quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)

    def __repr__(self):
        return "Decibel('{}')".format(self.dB)

    def __float__(self):
        return float(self.dB)

    def __str__(self):  # pylint: disable=W0222
        """
        >>> str(Decibel(0))
        '0.00'
        >>> str(Decibel(3.141596))
        '3.14'
        >>> str(Decibel(-3.999))
        '-4.00'
        >>> str(Decibel(None))
        '*'
        """
        if self.dB is None:
            return "*"
        else:
            return "{:.2f}".format(self.dB)

    def __neg__(self):  # pylint: disable=W0222
        """
        >>> str(-Decibel(1))
        '-1.00'
        >>> str(-Decibel(-1))
        '1.00'
        """
        if self.dB is None:
            return Decibel(None)
        return Decibel(self.dB.__neg__())

    def __mul__(self, other):  # pylint: disable=W0222
        """
        >>> Decibel(.5) * 20
        Decibel('10.000000')
        """
        if self.dB is None or other is None:
            return Decibel(None)
        if hasattr(other, "dB") and other.dB is None:
            return Decibel(None)
        return Decibel(self.dB * other)

    __rmul__ = __mul__

    def gain_factor(self):
        """Convert gain value to mwatt for multiplying
        >>> Decibel(0).gain_factor()
        Decimal('1.000000')
        >>> Decibel(13).gain_factor()
        Decimal('19.952623')
        """
        #
        # Gain: x dB = 10 * log10(multiplier)
        # 10 ^ (x dB / 10) = 10^(log10(multiplier))
        # 10 ^ (x dB / 10) = multiplier
        #
        rv = Decimal(10 ** (self.dB / 10), pcontext)
        rv = rv.quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)
        return rv

    mwatt_ratio = gain_factor

    def ase(self, nf, for_osnr=False):
        """Calculate ASE generated by amplification

        >>> Gain(23).ase(5.5)
        Power('-3.461412')
        """
        # Pase = hv(G -1) * NF * B0
        if not for_osnr:
            B0 = D('5.00e+12')  # all c-band (for .5nm)
        else:
            B0 = D('1.25e+10')  # @0.1nm resolution
        v = D('1.93e+14')  # speed of light
        h = D('6.63e-34')  # planck's constant
        nf = db2mwatt(nf)  # convert noise figure from dB to mwatts
        ase_watts = nf * B0 * h * v * (self.mwatt_ratio() - 1)
        return Power.from_mwatt(ase_watts * 1000)

    def osnr(self, nf, powerin):
        """Calculate OSNR for .1nm signal

        >>> Gain(16).osnr(7.9, Power(-20))
        Decibel('30.170675')
        """

        # Psig = Pin * G
        # Pase = hv(G - 1) * NF * B0.1nm
        # OSNR = Psig / Pase
        psig = powerin + self
        pase = self.ase(nf, True)
        return psig - pase


Decibal = Decibel  # Not 100% backward compat -- doesn't derive from Decimal
Gain = Decibel


@total_ordering
class Power(object):
    """Optical power value act's mostly like a float"""

    @classmethod
    def from_xml(cls, entry, xpath=None):
        if entry is not None and xpath is not None:
            entry = entry.find(xpath)
        if entry is None:
            return Power(None)
        try:
            return Power(entry.text)
        except ValueError:
            return Power(None)

    @classmethod
    def from_10uwatt(cls, mwatt):
        return cls.from_mwatt(D(mwatt) / 10000)

    @classmethod
    def from_10ths_dbm(cls, inval):
        dB = D(inval) / D(10)
        return cls(dB)

    from_10ths_db = from_10ths_dbm

    @classmethod
    def from_100ths_dbm(cls, inval):
        dB = D(inval) / D(100)
        return cls(dB)

    from_100ths_db = from_100ths_dbm

    @classmethod
    def from_mwatt(cls, mwatt):
        """
        >>> Power.from_mwatt(D(0))
        Power(None)
        >>> Power.from_mwatt(2)
        Power('3.010300')
        >>> Power.from_mwatt(1)
        Power('0.000000')
        >>> Power.from_mwatt(.5)
        Power('-3.010300')
        """
        if mwatt is None:
            return cls(None)
        if not mwatt:
            return cls(None)
        try:
            # Try and convert to float first to catch '0.00' case
            if not float(mwatt):
                return cls(None)
        except ValueError:
            pass

        dBm = D(10, pcontext) * D(mwatt).log10(pcontext)
        dBm = dBm.quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)
        return cls(dBm)

    def __init__(self, dBm, context=pcontext):  # pylint: disable=W0222
        """
        >>> Power(20).mwatt()
        Decimal('100.000000')
        >>> Power(10).mwatt()
        Decimal('10.000000')
        >>> Power(3).mwatt()
        Decimal('1.995262')
        >>> Power(1).mwatt()
        Decimal('1.258925')
        >>> Power(0).mwatt()
        Decimal('1.000000')
        >>> Power(None).mwatt()
        0
        >>> Power('None').mwatt()
        0
        """
        if dBm is None or dBm == "None":
            self.dBm = None
        else:
            try:
                if dBm.endswith('dBm'):
                    dBm = dBm.replace('dBm', '')
            except AttributeError:
                pass
            if isinstance(dBm, Power):
                self.dBm = dBm.dBm
            else:
                self.dBm = Decimal(dBm, context).quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)

    def mwatt(self):
        if self.dBm is None:
            return 0
        # XXX get context from us not global
        rv = Decimal(10 ** (self.dBm / 10), pcontext)
        rv = rv.quantize(SIXPLACES, rounding=ROUND_HALF_EVEN)
        return rv

    def __format__(self, format_spec):  # pylint: disable=W0221
        if self.dBm is None:
            # XXX really want to format this.
            return "*null*"
        return self.dBm.__format__(format_spec)

    def __bool__(self):
        return self.dBm is not None

    def __nonzero__(self):
        return self.dBm is not None

    def __add__(self, gain):  # pylint: disable=W0221
        """
        >>> Power(0) + Gain(1)
        Power('1.000000')
        """
        if hasattr(gain, "dBm"):
            raise TypeError("unsupported operand type(s) for +: 'Power' and 'Power'")
        else:
            return self.add_gain(gain)

    def __sub__(self, power_or_gain):  # pylint: disable=W0221
        """
        >>> Power(0) - Gain(1)
        Power('-1.000000')
        >>> Power(0) - Power(2)
        Decibel('-2.000000')
        >>> Power(3) - Power(0)
        Decibel('3.000000')
        """
        try:
            dBm = power_or_gain.dBm
            return Gain(self.dBm - dBm)
        except AttributeError:
            return self.add_gain(-power_or_gain)

    def __lt__(self, other):
        """
        >>> Power(0) > Power(.1)
        False
        >>> Power(.1) > Power(0)
        True
        >>> Power(0) < Power(.1)
        True
        >>> Power(.1) < Power(0)
        False
        >>> Power(0) == Power(0)
        True
        >>> Power(.1) == Power(.1)
        True
        >>> Power(0) != Power(None)
        True
        >>> Power(0) == Power(None)
        False
        >>> Power(None) == Power(None)
        True
        >>> Power(None) >= Power(-50)
        False
        >>> Power(None) < Power(-50)
        True
        >>> Power(None) <= Power(-50)
        True
        """
        mwatt = self.mwatt()
        try:
            return mwatt < other.mwatt()
        except AttributeError:
            return mwatt < Power(D(other)).mwatt()

    def __eq__(self, other):
        mwatt = self.mwatt()
        try:
            return mwatt == other.mwatt()
        except AttributeError:
            return mwatt == Power(D(other)).mwatt()

    def __mult__(self, multiplier):
        return Power.from_mwatt(self.mwatt() * multiplier)

    def __repr__(self):
        """
        >>> Power(0)
        Power('0.000000')
        """
        if self.dBm is None:
            return "Power(None)"
        return "Power('{}')".format(str(self.dBm))

    def __str__(self):
        """
        >>> str(Power(0))
        '0.00'
        """
        if self.dBm is None:
            return "*"
        else:
            return "{:.2f}".format(self.dBm)

    def __truediv__(self, other):  # pylint: disable=W0221
        return self.__div__(other)

    def __floordiv__(self, other):  # pylint: disable=W0221
        return self.__div__(other)

    def __div__(self, divisor):
        """
        >>> Power(0) / 16 / 6
        Power('-19.822712')
        >>> Power(0) / 10
        Power('-10.000000')
        >>> Power(0) / 8
        Power('-9.030900')
        >>> Power(0) / 6
        Power('-7.781513')
        >>> Power(0) / 4
        Power('-6.020600')
        >>> Power(0) / 2
        Power('-3.010300')
        >>> Power(3) / 2
        Power('-0.010301')
        """
        return Power.from_mwatt(self.mwatt() / divisor)

    def __mul__(self, unused):  # pylint: disable=W0221
        raise TypeError("Cannot multiply power values")

    def __or__(self, other):
        """
        # Check str() here it's very different
        >>> Power(0) | Power(0)
        Power('3.010300')
        """
        return Power.from_mwatt(self.mwatt() + other.mwatt())

    def add_gain(self, gain):
        # XXX hmm not sure about adding None to power.
        if self.dBm is None or gain is None:
            return Power(None)
        return Power(self.dBm + gain.dB)

    def get_delta(self, other):
        if self.dBm is None or other is None:
            return Gain(None)
        return Gain(other.dBm - self.dBm)


__author__ = 'Christian Hopps'
__date__ = 'January 21 2015'
__version__ = '1.0'
__docformat__ = "restructuredtext en"
