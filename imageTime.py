#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (C) 2010 - Gustavo Serra Scalet <gsscalet@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__AUTHOR__ = "Gustavo Serra Scalet <gsscalet@gmail.com>"
__VERSION__ = 0.2

try:
    import pyexiv2
except ImportError:
    from sys import exit
    print "Library not found!"
    print "Install pyexiv2 (tip: on ubuntu the package is python-pyexiv2)"
    exit(1)

import os, datetime, calendar, time

# some constraints
_TYPE_SYSTEM = 0
_TYPE_ORIGINAL = 1
_TYPE_DATETIME = 2

class ImageTime:
    """Get some time for the image.
    Primarily, the system file modified time.
    If a pyexiv2.Image object is given, the time is improved with the tags"""

    def __init__(self, filepath):
        # get from system modified time
        self.filepath = filepath  # important info. Save it
        self.exif = pyexiv2.Image(filepath)
        self.exif.readMetadata()

        seconds_from_epoch = os.path.getmtime(filepath)
        self.utctime = _epochToTimeTuple(seconds_from_epoch)
        self.time_type = _TYPE_SYSTEM

        # now trying with exif
        try:
            # most trustful time tag
            self.utctime = self.exif['Exif.Photo.DateTimeOriginal'].utctimetuple()
            self.time_type = _TYPE_ORIGINAL
            return  # best time that we can get!
        except IndexError:
            pass

        try:
            # this is just system time... when we have it
            self.utctime = self.exif['Exif.Image.DateTime'].utctimetuple()
            self.time_type = _TYPE_DATETIME
        except IndexError:
            pass

    def applyHourDelta(self, hours_delta):
        seconds_delta = hours_delta * 60 * 60
        new_time_epoch = _timeTupleToEpoch(self.utctime) + seconds_delta
        new_time_datetime = _epochToTimeTuple(new_time_epoch)

        # always apply on the most trustful time tag
        self.exif['Exif.Photo.DateTimeOriginal'] = datetime.datetime(*new_time_datetime[0:6])
        # redefine this variable
        self.utctime = self.exif['Exif.Photo.DateTimeOriginal'].utctimetuple()
        # and save
        self.exif.writeMetadata()
        return True

# this was very useful: http://www.saltycrane.com/blog/2008/11/python-datetime-time-conversions/
def _epochToTimeTuple(epoch):
    return time.gmtime(epoch)
def _timeTupleToEpoch(time_tuple):
    return calendar.timegm(time_tuple)

def timeTupleToString(time_tuple):
    return "%(year)04d:%(mon)02d:%(mday)02d %(hour)02d:%(min)02d:%(sec)02d" % {
        'year' : time_tuple.tm_year,
        'mon' : time_tuple.tm_mon,
        'mday' : time_tuple.tm_mday,
        'hour' : time_tuple.tm_hour,
        'min' : time_tuple.tm_min,
        'sec' : time_tuple.tm_sec,
    }

