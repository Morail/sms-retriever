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
from sqlalchemy.orm import sessionmaker, mapper
import re

from collector import get_connector
from csv import DictWriter, QUOTE_ALL

from message import Message

## GLOBAL VARS
SMS_PROPERTIES = ['id', 'text', 'date', 'year', 'month', 'day', 'hour', 'minute', 'second']
TEXT_PROPERTIES = ['number of words', 'number of characters', 'number of characters without spaces']
SINGLE_ENTITIES_ELEM = ['k', 'x', 'w', '!', '?', '+', ',', '.']
COMPLEX_ENTITIES_ELEM = ['tt', 'nn', 'RTL', '1', '6', '102', 'xk', 'xke', 'cn']
EMOTICONS = [':)', ':*', ':(', ':p']

def get_data(db, start, end):

    messages, conn = get_connector(db)
    
    ## configure Session class with desired options
    Session = sessionmaker()   
    session = Session(bind=conn)
    
    q = session.query(Message)
    
    ## time range filter
    if start:
        q = q.filter(messages.c.date >= start)
    if end:
        q = q.filter(messages.c.date <= end)
     
    ## querying
    for msg in q.all():
        yield msg
        
    log.name('data_getter').info('Retrieved {} messages from db', q.count())
    
    ## Closing the session
    session.close()

def prepare_message_data(msg):

    ## TODO
    #    tvb
    #    tvt***b
    #    Emoticon: :) :* :( :p

    id_, text, date_ = msg.id, msg.clean_text, msg.date   
    
    dict_ = {
        'id': id_,
        'text': text,
        'date': date_,
        'year': date_.year,
        'month': date_.month,
        'day': date_.day,
        'hour': date_.hour,
        'minute': date_.minute,
        'second': date_.second,
        'number of words': len(text.split(' ')),
        'number of characters': len(text),
        'number of characters without spaces': len(text.replace(' ', ''))
    }

    for c in SINGLE_ENTITIES_ELEM:
        dict_.update({c: text.count(c)})

    for elem in COMPLEX_ENTITIES_ELEM:
        dict_.update({
            elem: len(re.findall('(?:^|[^\w\d])(%s)(?=$|[^\w\d])' % (elem,), text, re.I))
        })

#    dict_.update{
#        'tvb': re.findall('(tvb)', text, re.IGNORECASE),
#        'tvt*b': re.findall('(tvt*b)', text, re.IGNORECASE)
#    }

    return dict_

def export_data(fn, messages):

    log.name('exporter').debug('Exporting data')
    
    ## fieldnames
    keys_ =  SMS_PROPERTIES + TEXT_PROPERTIES + SINGLE_ENTITIES_ELEM + \
             COMPLEX_ENTITIES_ELEM + ['tvb', 'tvt*b'] #+ EMOTICONS
    
    writer = DictWriter(open(fn, 'w'), fieldnames=keys_, delimiter=',',
                                    quotechar='"', quoting=QUOTE_ALL)

    writer.writeheader()
    log.name('exporter').debug('Preparing and saving data')
    writer.writerows([prepare_message_data(m) for m in messages])
    log.name('exporter').debug('Data exported and saved into {file_name}', file_name=fn)


def create_option_parser():
    import argparse

    p = argparse.ArgumentParser(description='Exports messages to a csv file')

    ## optional parameters
    p.add_argument('-s', '--start', metavar="YYYY/MM/DD-h:m:s", help="Date lower bound", default=None)
    p.add_argument('-e', '--end', default=None, metavar="YYYY/MM/DD-h:m:s", help="Date upper bound")
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

    df = '%Y/%m/%d-%H:%M:%S'

    start = dt.strptime(args.start, df) if args.start else None
    end = dt.strptime(args.end, df) if args.end else None

    messages = get_data(args.db_name, start, end)
    export_data(args.file_name, messages)
    
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

