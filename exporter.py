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
EMOTICONS = {
    'happy :)': (r':-?[)\]>]', r'=[)\]]', r'\^[_\-.]?\^', 'x\)', r'\(^_^\)'),
    'sad :(': (r':-?[(\[<]', r'=[(\[]'),
    'laugh :D': (r':[ -]?D',),
    'tongue :P': (':-?[pP]', '=[pP]',),
    'normal :-|': (r':-?\|',),
    'cool 8-)': (r'8-?\)',),
}

def build_smile_re(dsmile):
    out = {}
    for name, lsmile in dsmile.items():
        out[name] = re.compile(r'(?: %s)' % (r'| '.join(lsmile)))
        #print name, r'(?:\s%s)' % (r'|\s'.join(lsmile))

    return out

def find_smiles(text, dict_):
    """
    Find smiles in text and returns a dictionary of found smiles

    >>> find_smiles(':) ^^')
    {'happy': 1}
    >>> find_smiles(' ^^')
    {'happy': 1}
    >>> find_smiles(' :|')
    {'normal': 1}
    """
    res = {}

    re_smile = build_smile_re(dict_)

    return {name: len([1 for match in regex.findall(text) if match]) for name, regex in re_smile.items()}


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

    dict_.update({
        'tvb': len(re.findall('(?:^|[^\w\d])(tvt*b+)(?=$|[^\w\d])', text, re.IGNORECASE)),
    })

    d_smile = find_smiles(text, EMOTICONS)

    if isinstance(d_smile, dict):
        dict_.update(d_smile)

    return dict_

def export_data(fn, db, start, end):

    log.name('exporter').debug('Exporting data')
    
    ## fieldnames
    keys_ =  SMS_PROPERTIES + TEXT_PROPERTIES + SINGLE_ENTITIES_ELEM + \
             COMPLEX_ENTITIES_ELEM + ['tvb'] + EMOTICONS.keys()
    
    writer = DictWriter(open(fn, 'w'), fieldnames=keys_, delimiter=',',
                                    quotechar='"', quoting=QUOTE_ALL)

    writer.writeheader()
    log.name('exporter').debug('Preparing and saving data')
    writer.writerows([prepare_message_data(m) for m in get_data(db, start, end)])
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

    export_data(args.file_name, args.db_name, start, end)
    
    log.name('main').info('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

