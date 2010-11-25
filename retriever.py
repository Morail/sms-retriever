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


import sys
import urllib2 as ul
import logging
import re
import htmlentitydefs

from datetime import datetime
from BeautifulSoup import BeautifulSoup


class Retriever(object):
    
    def __init__(self, url, mpp=1, df='%y/%m/%d', regex='.'):
        self.top = mpp
        self.date_format = df
        self.counter, self.pagestart = 0, 0
        self.base_url = url
        self.messages = {}
        self.regex = regex


    def process(self):
    
        while True:
            url = "%s?top=%d&pagestart=%d" % (self.base_url, 
                                              self.top, self.pagestart)
            
            html = BeautifulSoup(ul.urlopen(url))
    
            ## break while loop
            if not html:
                logging.debug('Nothing returned from the given url, stopping this process')
                break
    
            list_ = html.findAll('div', id=re.compile(self.regex))
    
            if not len(list_):
                logging.debug('No more messages found, stopping this process')
                break
    
            for d in list_:
                id = d['id'].split('_')[-1]

                if not id or id in messages:
                    continue

                date_ = datetime.strptime(d.strong.string, self.date_format)
                text= unescape(d.div.contents[-1])
    
                self.messages[id] = (text, date_)

                ## updating message counter
                self.counter += 1
    
            ## incrementing pagestart
            self.pagestart += self.top
    
        logging.info('Messages: %d' % (self.counter,))


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

def main():

    logging.basicConfig(#filename="sms-retriever.log",
                                stream=sys.stderr,
                                level=logging.DEBUG)

    logging.info('START')
    
    url = 'http://www.rtl.it/ajaxreturn/sms_list.php'
    df = '%d.%m.%Y %H:%M:%S'
    regex = 'sms_\d+'
    
    r = Retriever(url=url, mpp=15, regex=regex, df=df)
    r.process()

    logging.info('STOP')

if __name__ == "__main__":
    main()

