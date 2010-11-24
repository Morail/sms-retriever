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


import urllib2 as ul
from BeautifulSoup import BeautifulSoup
import re
from datetime import datetime


def main():
    base_url = 'http://www.rtl.it/ajaxreturn/sms_list.php'
    top = 15
    pagestart = 0
    date_format = "%d.%m.%Y %H:%M:%S"
    counter = 0

    while True:
        url = "%s?top=%d&pagestart=%d" % (base_url, top, pagestart)
        html = BeautifulSoup(ul.urlopen(url))

        if not html: break

        #list_ = html.findAll('div', id=lambda x: x and re.findall('sms_\d+', x))
        list_ = html.findAll('div', id=re.compile('sms_\d+'))

        if not len(list_): break

        for d in list_:
            id = d['id'].split('_')[-1]
            date_ = datetime.strptime(d.strong.string, date_format)
            text= ul.unquote(d.div.contents[-1])

            print id, date_, text

            counter += 1

        ## incrementing pagestart
        pagestart += top

    print 'Messages:', counter


if __name__ == "__main__":
    main()

