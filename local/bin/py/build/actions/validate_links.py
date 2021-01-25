#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# regex search through markdown files for all substrings
# return all matches
# validate the matches to make sure they're an actual url
# write as a legit url
# loop through valid urls to ping
# return url if not a 200, 302 response
# PROFIT
# --------------------- #

import re
import ssl
from urllib.request import urlopen, Request, HTTPError
import urllib.error
from optparse import OptionParser

linkRe = r"^\[\d{0,3}\]\: (.*)"
httpRe = r"(http|https)\:\/\/(.*)"

invalid_links = []

def test_link(link):
    if (re.match(httpRe, link) is None):
        link = 'https://docs.datadoghq.com{}'.format(link)
    try:
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        headers = { 'User-Agent' : user_agent }
        req = Request(url=link, headers=headers, method='GET')
        context = ssl._create_unverified_context()
        conn = urlopen(req, context=context)
        # Check if code is not 202 nor is it 302
        if(conn.getcode() != 200 and conn.getcode() != 302):
            invalid_links.append(link)
    except HTTPError as err:
        # Check if code is 404
        print('WARNING {} {}'.format(err, link))
        invalid_links.append(link)

def search_file(file):
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.search(linkRe, line)
            if (m):
                link = m.group(1)
                test_link(link)

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [options] file')
    parser.add_option('-f', '--file',
                      help='File to format link in reference',
                      default=None)
    parser.add_option('-d', '--directory',
                      help='Directory to format link in reference for all markdown file', default=None)

    (options, args) = parser.parse_args()

    if options.file:
        search_file(options.file)
