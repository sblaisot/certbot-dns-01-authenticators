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
import json
from config import *

pp = pprint.PrettyPrinter(indent=4)

certbot_domain = os.environ.get("CERTBOT_DOMAIN")
try:
    certbot_domain
except NameError:
    print("CERTBOT_DOMAIN environment variable is missing, exiting")
    exit(1)

certbot_validation = os.environ.get("CERTBOT_VALIDATION")
try:
    certbot_validation
except NameError:
    print("CERTBOT_VALIDATION environment variable is missing, exiting")
    exit(1)

if livedns_sharing_id == None:
    sharing_param = ""
else:
    sharing_param = "?sharing_id=" + livedns_sharing_id

headers = {
    'X-Api-Key': livedns_apikey,
}

top_domain = certbot_domain
sub_domain = ""

while top_domain.count('.') > 1:
    index = top_domain.find('.')
    sub_domain = sub_domain + top_domain[:index]
    top_domain = top_domain[(index+1):]



response = requests.get(livedns_api + "domains" + sharing_param, headers=headers)

if (response.ok):
    domains = response.json()
else:
    response.raise_for_status()
    exit(1)

domain_index = next((index for (index, d) in enumerate(domains) if d["fqdn"] == top_domain), None)

if domain_index == None:
    # domain not found
    print("The requested domain " + certbot_domain + " was not found in this gandi account")
    exit(1)

domain_records_href = domains[domain_index]["domain_records_href"]

rrset_name = "_acme-challenge"
if len(sub_domain):
    rrset_name = rrset_name + "." + sub_domain

response = requests.get(domain_records_href + "/" + rrset_name + sharing_param, headers=headers)

if (response.ok):
    domains = response.json()
    if len(domains) == 0:
        print("Existing _acme-challenge record not found, exiting")
        exit(1)
    if domains[0]["rrset_type"] != "TXT":
        print("Existing _acme-challenge record doesn't seems to be an acme challenge, exiting")
else:
    print("Failed to look for existing _acme-challenge record")
    response.raise_for_status()
    exit(1)

response = requests.delete(domain_records_href + "/" + rrset_name + "/TXT" + sharing_param, headers=headers)

if (response.ok):
    print("all good, entry deleted")
    #pp.pprint(response.content)
else:
    print("something went wrong")
    pp.pprint(response.content)
    response.raise_for_status()
    exit(1)
