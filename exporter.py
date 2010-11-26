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
from csv import DictWriter, QUOTE_ALL


def get_data():

    table, conn = get_connector('sms.db')
    s = table.select()
    rs = s.execute()

    for row in rs:
        yield row

def prepare_data(row):
    dict_ = {
        'id': row[0],
        'text': row[1].encode("utf-8"),
        'date': row[2],
        'year': row[2].year,
        'month': row[2].month,
        'day': row[2].day,
        'hour': row[2].hour,
        'minute': row[2].minute,
        'second': row[2].second,
        'number of words': len(row[1].split(' ')),
        'number of characters': len(row[1])
    }

    return dict_

def export_data():

    keys_ = ['id', 'text', 'date', 'year', 'month', 'day', 'hour', 'minute', 'second',
             'number of words', 'number of characters']
    csv_writer = DictWriter(open('test.csv', 'w'),
                                    fieldnames = keys_, delimiter=',',
                                    quotechar='"', quoting=QUOTE_ALL
                                )

    csv_writer.writeheader()
    csv_writer.writerows([prepare_data(row) for row in get_data()])


def main():

    ## Twiggy logger setup
    twiggy_setup()
    log.name('main').info('-------------------- START --------------------')

    export_data()
    
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

