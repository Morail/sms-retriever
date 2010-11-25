#!/usr/bin/env python

##########################################################################
#                                                                        #
#  This program is free software; you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation; version 2 of the License.               #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#  GNU General Public License for more details.                          #
#                                                                        #
##########################################################################


from twiggy import *

def twiggy_setup():
    debug_output = outputs.FileOutput("retriever.log", format=formats.line_format)
    #main_output = outputs.FileOutput("main.log", format=formats.line_format)

    addEmitters(
        # (name, min_level, filter, output),
        ("process", levels.DEBUG, None, debug_output),
        #("main", levels.ERROR, None, main_output),
    )
