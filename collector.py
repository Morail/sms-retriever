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


import urllib2
import re
import htmlentitydefs

from datetime import datetime as dt
from BeautifulSoup import BeautifulSoup
from twiggy import log
from twiggy_setup import twiggy_setup
from sqlalchemy import *

from message import Message

class Retriever(object):
    
    def __init__(self, url, mpp=1, df='%y/%m/%d', regex='.', db=None):
        self.top = mpp
        self.date_format = df
        self.counter, self.page_start = 0, 0
        self.base_url = url
        self.messages = []
        self.re = regex
        self._log = log.name('process')

        ## database
        events, self.connection = get_connector(db)
        self.insert = events.insert()


    def process(self):
    
        while True:
            url = "%s?top=%d&pagestart=%d" % (self.base_url, self.top,
                                              self.page_start)

            self._log.debug('reading from url {url}', url=url)

            try:
                html = BeautifulSoup(urllib2.urlopen(url))
            except urllib2.HTTPError:
                self._log.error('Cannot connect to the web page')
                return
    
            ## break while loop
            if not html:
                self._log.fields(Messages=self.counter).debug('Nothing returned from the given url, stopping this process')
                break
    
            list_ = html.findAll('div', id=re.compile(self.re))
    
            if not len(list_):
                self._log.fields(Messages=self.counter).debug('Nothing returned from the given url, stopping this process')
                break
    
            for d in list_:
                id = d['id'].split('_')[-1]

                if not id or id in self.messages:
                    continue

                date_ = dt.strptime(d.strong.string, self.date_format)
                text= unescape(d.div.contents[-1])
                    
                self.messages.append(Message(id,text, date_))

                ## updating message counter
                self.counter += 1
    
            ## incrementing pagestart
            self.page_start += self.top
    
        self._log.info('Messages found: {}', self.counter)


    def save(self):

        ## no sms to be saved
        if not self.counter:
            return

        counter = 0
        for m in self.messages:
            data = {'id': m.id, 'text': m.text, 'date': m.date}
            try:
                self.connection.execute(self.insert, data)
                counter += 1
            except:
                ## id duplicated
                pass

        self._log.info('Saved {} messages into the database', counter)


def get_connector(db_name):
    engine = create_engine('sqlite:///' + db_name)
    metadata = MetaData()
    metadata.bind = engine

    table = Table('messages', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('text', String()),
                   Column('date', DateTime)
            )

    metadata.create_all(engine) # create the table

    conn = engine.connect()

    return (table, conn)

## Thanks to: http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def create_option_parser():
    import argparse

    p = argparse.ArgumentParser(description='Retrieves sms from a website')

    ## optional parameters
    p.add_argument('-u', '--url', metavar="URL", help="web URL", default="http://www.rtl.it/ajaxreturn/sms_list.php")
    p.add_argument('-d', '--date-format', help='parsed date format (default: %(default)s)', default='%d.%m.%Y %H:%M:%S')
    p.add_argument('-m', '--messages-per-page', help='number of sms per page for pagination (default: %(default)s)',
                   type=int, default=15)
    p.add_argument('-r', '--regex', help='regex used to identify div containing sms (default: %(default)s)', default='sms_\d+')
    ## positional arguments
    p.add_argument('db_name', help="database file name", metavar="DB_FILE")

    return p

def main():

    ## Twiggy logger setup
    twiggy_setup()
    log.name('main').debug('-------------------- START --------------------')

    op = create_option_parser()
    args = op.parse_args()

    url = args.url
    df = args.date_format
    regex = args.regex
    db_name = args.db_name
    mpp = args.messages_per_page
    
    r = Retriever(url=url, mpp=mpp, regex=regex, df=df, db=db_name)
    r.process()
    r.save()
    log.name('main').debug('-------------------- STOP --------------------')

if __name__ == "__main__":
    main()

