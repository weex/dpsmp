#!/usr/bin/env python
'''
users.py - validate records on a csv download of the users sheet
'''
import pycurl
import re, sys, csv, json
import hashlib
import os.path
from validate import *
from StringIO import StringIO
# sha256 hash of sheet
# ripemd hash of sheet
# count the number of users
# show how many are reviewed
# show how many are audited
# check that reviews and audits were done by at least reviewed users
# check all of the enrollment signatures and build a list of master and delegated addresses

debug = False

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as csvfile:
            validate_review_audit(csvfile)
    else:
        glist = fetch_gspread_list(os.path.join(os.path.expanduser("~"), "dpsmp_glist.ini"))
        print("sheet, row, column")
        for name, items in glist.iteritems():
            csvfile = request_gspread_csv(items['doc'], items.get('gid', "0"))
            if csvfile:
                validate_signatures(csvfile, name)
            else:
                #print("Failed to request gspread %s" % (name))
                pass

def request_gspread_csv(key, gid="0"):
    '''
    Downloads the Google Spreadsheet with the specified key (spreadsheet
    specifier) and gid (worksheet specifier).
    '''
    buffer = StringIO()
    try:
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://docs.google.com/spreadsheets/d/%s/export?format=csv&gid=%s' % (key, gid))
        c.setopt(c.HTTPGET, 1)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        buffer.seek(0)
        if c.getinfo(c.RESPONSE_CODE) != 200:
           buffer = None
        c.close()
    except pycurl.error:
        buffer = None
    return buffer

def fetch_gspread_list(path):
    '''
    Imports the list of spreadsheets, contained in a config file at path,
    to download from Google Spreadsheets.
    '''
    from ConfigParser import ConfigParser
    glist = {}
    parser = ConfigParser()
    parser.read(path)
    for section in parser.sections():
        glist[section] = {}
        for k, v in parser.items(section):
            glist[section][k] = v
    return glist

def validate_signatures(csvfile, name):
    '''
    Checks all the cells of the File Object csvfile, on cells that have a
    bitcoin signature, check if such signature is valid.
    '''
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    # skip first row (should we?)
    try:
        reader.next()
    except StopIteration:
        pass
    # parse cells and on the ascii armored bitcoin cells, verify signature
    for rowid, row in enumerate(reader):
        for colid, col in enumerate(row):
            if parse_sig(col) and not verify_sig(col)[0]:
                print('%s, %d, %d' % (name, rowid + 2, colid + 1))

def validate_review_audit(csvfile):
    '''Read CSV and validate each user record, review, and audit'''
    data = {'users': [], 'sha256sum': hashlib.sha256(csvfile.read()).hexdigest()}
    csvfile.seek(0)
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    user_count = 0
    for row in reader:
        if 'Contact' not in row:
            handle = row[0]
            address = row[1]
            enrollment = row[2]
            review = row[3]
            audit = row[4]

            valid = False
            master = ''
            attempt = ''

            # check enrollment and that it's signed by user's master
            e = validate_enrollment(enrollment)
            if e != False:
                (valid, master) = e

            # check review, that it's signed by the active address for a user, and then
            # do the check above

            # check the audit, 

            
            
            # check signature address matches master
            regex = re.search(r"-----BEGIN SIGNATURE-----\r?\n?(\w+)", row[2])
            if regex:
                attempt = regex.group(1)
            attempt_match = False
            if attempt == master:
                attempt_match = True
            if attempt_match == False and debug:
                print  row[0] + " did not attempt to sign enrollment with master. used = " \
                        + attempt + " needed = " + master

            data['users'].append({'username': row[0],
                                         'valid': valid,
                                         'addr_master':  master,
                                         'signed_by_master': attempt_match})
            user_count += 1
    data['user_count'] = user_count
    print json.dumps(data, indent=4)

if __name__ == '__main__':
    sys.exit(main())
