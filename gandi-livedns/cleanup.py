#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pprint
import requests
import os
import sys
from config import *

pp = pprint.PrettyPrinter(indent=4)

certbot_domain = os.environ.get("CERTBOT_DOMAIN")
try:
    certbot_domain
except NameError:
    print("CERTBOT_DOMAIN environment variable is missing, exiting")
    sys.exit(1)

certbot_validation = os.environ.get("CERTBOT_VALIDATION")
try:
    certbot_validation
except NameError:
    print("CERTBOT_VALIDATION environment variable is missing, exiting")
    sys.exit(1)

if livedns_sharing_id is None:
    sharing_param = ''
else:
    sharing_param = '?sharing_id={}'.format(livedns_sharing_id)

headers = {
    'X-Api-Key': livedns_apikey,
}

response = requests.get('{}domains{}'.format(livedns_api, sharing_param),
                        headers=headers)

if (response.ok):
    domains = response.json()
else:
    response.raise_for_status()
    sys.exit(1)

domain_index = next((index for (index, d) in enumerate(domains) if d["fqdn"] == certbot_domain), None)

if domain_index is None:
    # domain not found
    print('The requested domain {} was not found in this gandi account'
          .format(certbot_domain))
    sys.exit(1)

domain_records_href = domains[domain_index]["domain_records_href"]

response = requests.get('{}/_acme-challenge/TXT{}'
                        .format(domain_records_href, sharing_param),
                        headers=headers)

if response.status_code == 404:
    print('No _acme-challenge TXT record found.')
    print('Nothing to cleanup, exiting')
    sys.exit(0)

if not response.ok:
    print('Failed to look for existing _acme-challenge record')
    response.raise_for_status()
    sys.exit(1)

existing_record = response.json()
if '"{}"'.format(certbot_validation) not in existing_record['rrset_values']:
    print('Validation token not in _acme-challenge TXT record found.')
    print('Nothing to cleanup, exiting')
    sys.exit(0)

# pp.pprint(existing_record)
if len(existing_record.get('rrset_values', [])) > 1:
    newrecord = existing_record
    newrecord['rrset_values'].remove('"{}"'.format(certbot_validation))
    # print(newrecord)
    response = requests.put('{}/_acme-challenge/TXT{}'
                            .format(domain_records_href, sharing_param),
                            headers=headers, json=newrecord)
else:
    # Need to completely remove record
    response = requests.delete('{}/_acme-challenge/TXT{}'
                               .format(domain_records_href, sharing_param),
                               headers=headers)

if (response.ok):
    print("all good, entry deleted")
    # pp.pprint(response.content)
else:
    print("something went wrong")
    pp.pprint(response.content)
    response.raise_for_status()
    sys.exit(1)
