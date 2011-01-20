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

import os, datetime, time

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
        self.time = _epochToDatetime(seconds_from_epoch)
        self.time_type = _TYPE_SYSTEM

        # now trying with exif
        try:
            # most trustful time tag
            self.time = self.exif['Exif.Photo.DateTimeOriginal']
            self.time_type = _TYPE_ORIGINAL
            return  # best time that we can get!
        except IndexError:
            pass

        try:
            # this is just system time... when we have it
            self.time = self.exif['Exif.Image.DateTime']
            self.time_type = _TYPE_DATETIME
        except IndexError:
            pass

    def applyHourDelta(self, hours_delta):
        seconds_delta = hours_delta * 60 * 60
        new_time_epoch = _datetimeToEpoch(self.time) + seconds_delta
        new_time_datetime = _epochToDatetime(new_time_epoch)

        # always apply on the most trustful time tag
        self.exif['Exif.Photo.DateTimeOriginal'] = new_time_datetime
        # redefine this variable
        self.time = self.exif['Exif.Photo.DateTimeOriginal']
        # and save
        self.exif.writeMetadata()
        return True

def _epochToDatetime(epoch):
    t = time.localtime(epoch)
    return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_sec)

def _datetimeToEpoch(date_time):
    return time.mktime(date_time.timetuple())

