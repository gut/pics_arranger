#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (C) 2011 - Gustavo Serra Scalet <gsscalet@gmail.com>

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
__VERSION__ = 0.1

MIN_ARGS = 0

from imageTime import *


def getAmmountOfDigits(size):
    "Gets how much decimal digits we need to represent the whole series of size @SIZE"
    from math import ceil, log
    return int(ceil(log(size, 10)))  # log of base 10 in the length

def renomPicsByDate(write = False, script = False, verbose = False, directory = '.'):
    """
    Check every picture timestamp (based on the exif) of the directory
    @DIRECTORY and rename (if --write mode) all of them by their chronological order.
    Also can generate the set of mv commands if --shell-script mode is used.
    Default @DIRECTORY: .
    """
    from glob import glob
    from os import path,rename

    if not path.isdir(directory):
        from sys import exit
        print "Enter a valid directory name"
        exit(2)

    if script:
        print "#!/bin/sh"
        print

    images_and_keys = []
    for f in glob(path.join(directory, "*.[Jj][Pp][Gg]")):
        if verbose:
            print "# Analysing %s" % f
        image = ImageTime(f)
        images_and_keys.append((image.utctime, image.filepath))

    images_and_keys.sort(key=lambda tup : tup[0])  # sort by the first element of the tuple
    series_format = "%0" + repr(getAmmountOfDigits(len(images_and_keys))) + "d.jpg"

    for n, f in enumerate(images_and_keys):
        new_filepath = path.join(directory, series_format % (n + 1))  # starts at number 1
        if verbose:
            print "# Time: %s" % timeTupleToString(f[0]),

        if script:
            print 'mv "%s" "%s"' % (f[1], new_filepath)
        else:  # don't print this line if on --shell-script mode
            print "%s => %s" % (f[1], new_filepath)

        if write:
            rename(f[1], new_filepath)

    # feedback
    if write:
        print "# Changes were written to disk"
    elif not script:
        print "#  (use the --write option to write the changes)"
        print "#  !!! Remember to back up your files before writing !!!"

if __name__ == "__main__":
    from sys import argv, exit
    from os import sep
    from optparse import OptionParser

    options = {
        # 'one_letter_option' : ['full_option_name',
            # "Help",
            # default_value],
        'v' : ['verbose',
            "Shows more info about the process",
            False],
        's' : ['shell-script',
            "Generate a shell-script with the mv's commands",
            False],
        'w' : ['write',
            "Write changes to files",
            False],
    }

    options_list = ' '.join(["[-%s --%s]" % (o, options[o][0]) for o in options])
    desc = renomPicsByDate.__doc__.replace('    ','')
    parser = OptionParser("%%prog %s [DIRECTORY]" % options_list,
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

    (opt, args) = parser.parse_args(argv)
    if len(args) < MIN_ARGS + 1:
        # not enough arguments
        print """ERROR: not enough arguments.
Try `%s --help' for more information""" % args[0].split(sep)[-1]
        exit(1)

    if len(args) == 2:  # optional directory
        renomPicsByDate(opt.w, opt.s, opt.v, args[1])
    else:
        renomPicsByDate(opt.w, opt.s, opt.v)

