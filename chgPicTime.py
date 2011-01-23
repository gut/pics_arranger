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

MIN_ARGS = 2

import os
from imageTime import ImageTime, timeTupleToString

def chgPicTime(delta, files, quiet = False):
    """
    Apply @DELTA hours to the @FILES' exif tags
    """
    for f in files:
        img_datetime = ImageTime(f)
        old_time = timeTupleToString(img_datetime.utctime)
        if img_datetime.applyHourDelta(delta):
            new_time = timeTupleToString(img_datetime.utctime)
            if not quiet:
                print 'Changed "%s" from "%s" to "%s"' % (os.path.basename(f), old_time, new_time)
        else:
            print 'FAILED to change "%s" from "%s" to "%s"' % (os.path.basename(f), old_time, new_time)


def hintForNegativeDelta(argv):
    found_negative_number = False
    for arg in argv:
        if arg == "--":
            # he is already prepared for that
            break
        try:
            int(arg[1:])
            found_negative_number = True
        except ValueError:
            pass
    if found_negative_number:
        print 'Do you want to enter a negative number!? Type a "--" as the first argument to allow it!'
        print

if __name__ == "__main__":
    from sys import argv, exit
    from os import sep
    from optparse import OptionParser

    options = {
        # 'one_letter_option' : ['full_option_name',
            # "Help",
            # default_value],
        'q' : ['quiet',
            "Avoid showing output",
            False],
    }

    options_list = ' '.join(["[-%s --%s]" % (o, options[o][0]) for o in options])
    desc = chgPicTime.__doc__.replace('    ','')
    parser = OptionParser("%%prog %s DELTA FILE1 [FILE2 FILE3 ...] " % options_list,
            description=desc,
            version="%%prog %s" % __VERSION__)

    for o in options:
        shorter = '-' + o
        longer = '--' + options[o][0]
        if type(options[o][2]) is bool:
            parser.add_option(shorter, longer, dest=o, help=options[o][1],
                action="store_true", default=options[o][2])
        elif type(options[o][2]) is str:
            parser.add_option(shorter, longer, dest=o, help=options[o][1],
                action="store", type="string", default=options[o][2])

    # in case the user tries to enter a negative @DELTA, give him the hint for the args
    hintForNegativeDelta(argv)

    (opt, args) = parser.parse_args(argv)
    if len(args) < MIN_ARGS + 1:
        # not enough arguments
        print """ERROR: not enough arguments.
Try `%s --help' for more information""" % args[0].split(sep)[-1]
        exit(1)

    # abort if @DELTA is not a number or if it's zero
    try:
        delta = int(args[1])
        if not delta:
            raise ValueError
    except ValueError:
        print "Why run this with the change of 0 hours!?"
        exit(2)

    chgPicTime(delta, args[2:], opt.q)

