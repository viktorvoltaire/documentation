#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# regex search through markdown files for all substrings
# Return all matches
# Validate the matches to make sure they're an actual url
# Write as a legit url
# Loop through valid urls to ping
# Return url if not a 200, 302 response
# PROFIT
# --------------------- #

import re
import ssl
from urllib.request import urlopen, Request, HTTPError
import urllib.error
from optparse import OptionParser

# regex search through markdown files for all substrings

linkRe = r"^\[\d{0,3}\]\: (.*)" # urls that start with a number in brackets
httpRe = r"(http|https)\:\/\/(.*)" # urls that start with an http/https protocol

invalid_links = [] # list of links that are invalid

def test_link(link): # test link
    if (re.match(httpRe, link) is None):
        link = 'https://docs.datadoghq.com{}'.format(link) # if it matches the number format, append the string to the docs url
    try: # prep to create request headers
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        headers = { 'User-Agent' : user_agent }
        req = Request(url=link, headers=headers, method='GET')
        context = ssl._create_unverified_context()
        conn = urlopen(req, context=context)
        # Check if code is not 200 or 302. If it's not, put it in list of invalid links.
        if(conn.getcode() != 200 and conn.getcode() != 302):
            invalid_links.append(link)
    except HTTPError as err:
        # Bad connection or invalid link, return warning.
        print('WARNING {} {}'.format(err, link))
        invalid_links.append(link)

def search_file(file): # Pass file, search it.
    with open(file, 'r', encoding='utf-8') as f: # Open stream for the file.
        for line in f: # Loop through every line in file.
            m = re.search(linkRe, line) # Check each line if it matches with above regex.
            if (m): # If it matches the regex pattern, test the link (make GET requests).
                link = m.group(1)
                test_link(link)

if __name__ == '__main__': # When you run the file, this passes the parameters to it.
    parser = OptionParser(usage='usage: %prog [options] file')
    parser.add_option('-f', '--file',
                      help='File to format link in reference',
                      default=None)
    parser.add_option('-d', '--directory',
                      help='Directory to format link in reference for all markdown file', default=None)

    (options, args) = parser.parse_args()

    if options.file: # If you pass any parameters, run the script.
        search_file(options.file)
