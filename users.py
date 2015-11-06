#!/usr/bin/env python
'''
users.py - validate records on a csv download of the users sheet
'''
import re, sys, csv, json
import hashlib
from validate import *
# sha256 hash of sheet
# ripemd hash of sheet
# count the number of users
# show how many are reviewed
# show how many are audited
# check that reviews and audits were done by at least reviewed users
# check all of the enrollment signatures and build a list of master and delegated addresses

debug = False

def main():
    ''' Read CSV and validate each user record, review, and audit'''
    with open(sys.argv[1], 'rb') as csvfile:
        h = hashlib.new('ripemd160')
        h.update(csvfile.read())
        ripemd160 = h.hexdigest()
        csvfile.seek(0)
        data = {'users': [], 'sha256sum': hashlib.sha256(csvfile.read()).hexdigest(), 'ripemd160': ripemd160}
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

                r = validate_review(review)
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
                                      'enrollment': valid,
                                      'addr_master':  master,
                                      'enrollment_master': attempt_match})
                user_count += 1
        data['user_count'] = user_count
        print json.dumps(data, indent=4)

if __name__ == '__main__':
    sys.exit(main())
