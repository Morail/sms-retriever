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


from datetime import datetime as dt
from twiggy import log
from twiggy_setup import twiggy_setup
from sqlalchemy import *

from collector import get_connector


def main():

    ## Twiggy logger setup
    twiggy_setup()
    log.name('main').info('-------------------- START --------------------')

    table, conn = get_connector()
    s = table.select()
    rs = s.execute()

    for row in rs:
        print row
    
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

