#!/usr/bin/env python
'''
users.py - validate records on a csv download of the users sheet
'''
import re, sys, csv

# sha256 hash of sheet
# ripemd hash of sheet
# count the number of users
# show how many are reviewed
# show how many are audited
# check that reviews and audits were done by at least reviewed users

def validate():
    ''' Read CSV and validate each user record, review, and audit'''
    with open('Users - Sheet1.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        user_count = 0
        for row in reader:
            if 'Contact' not in row:
                user_count += 1
                master = ''
                attempt = ''

                # sift enrollment signature
                regex = re.search(r"Master signing address:\s+(\w+)", row[2])
                if regex:
                    master = regex.group(1)

                # check signature address matches master
                regex = re.search(r"-----BEGIN SIGNATURE-----\r?\n?(\w+)", row[2])
                if regex:
                    attempt = regex.group(1)
                attempt_match = False
                if attempt == master:
                    attempt_match = True
                if attempt_match == False:
                    print  row[0] + " did not attempt to sign enrollment with master. used = " \
                            + attempt + " needed = " + master
                print row[0] + ',' + master + ',' + str(attempt_match)
        print "Number of users: " + str(user_count)

if __name__ == '__main__':
    sys.exit(validate())
