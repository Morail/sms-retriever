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

from message import Message

def get_data(db):

    table, conn = get_connector(db)
    s = table.select()
    rs = s.execute()

    counter = 0
    for row in rs:
        counter += 1
        yield Message(id_=row[0], text=row[1].encode('utf-8'), date_=row[2])

    log.name('data_getter').info('Retrieved {} messages from db', counter)

def prepare_data(message):
   return {
       'id': message.id,
       'text': message.text,
       'date': message.date,
       'year': message.date.year,
       'month': message.date.month,
       'day': message.date.day,
       'hour': message.date.hour,
       'minute': message.date.minute,
       'second': message.date.second,
       'number of words': len(message.text.split(' ')),
       'number of characters': len(message.text),
       'number of characters without spaces': len(message.text.replace(' ', ''))
   }

def export_data(fn, db):

    log.name('exporter').debug('Exporting data')
    
    ## fieldnames
    keys_ =  ['id', 'text', 'date', 'year', 'month', 'day', 'hour', 'minute', 'second',
             'number of words', 'number of characters', 'number of characters without spaces']
    
    writer = DictWriter(open(fn, 'w'), fieldnames=keys_, delimiter=',',
                                    quotechar='"', quoting=QUOTE_ALL)

    writer.writeheader()
    log.name('exporter').debug('Preparing and saving data')
    writer.writerows([prepare_data(m) for m in get_data(db)])
    log.name('exporter').debug('Data exported and saved into {file_name}', file_name=fn)


def create_option_parser():
    import argparse

    p = argparse.ArgumentParser(description='Exports messages to a csv file')

    ## optional parameters
    # ...
    ## positional arguments
    p.add_argument('file_name', help="csv file name", metavar="CSV_FILE")
    p.add_argument('db_name', help="database file name", metavar="DB_FILE")

    return p

def main():

    ## Twiggy logger setup
    twiggy_setup()
    log.name('main').info('-------------------- START --------------------')

    op = create_option_parser()
    args = op.parse_args()

    export_data(args.file_name, args.db_name)
    
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

