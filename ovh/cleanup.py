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
import ovh
import os


pp = pprint.PrettyPrinter(indent=4)

certbot_domain = os.environ.get('CERTBOT_DOMAIN')
try:
    certbot_domain
except NameError:
    print('***ERROR: CERTBOT_DOMAIN environment variable is missing, exiting')
    exit(1)

certbot_validation = os.environ.get('CERTBOT_VALIDATION')
try:
    certbot_validation
except NameError:
    print('***ERROR: CERTBOT_VALIDATION environment variable missing, exiting')
    exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))
config_file = script_dir + "/ovh.conf"

if not os.path.exists(config_file):
    print('***ERROR: config file not found')
    exit(1)

# Instanciate an OVH Client.
# Credentials are in ovh.conf file
client = ovh.Client(config_file=config_file)

# Look for requested domain
result = client.get('/domain/zone/')

if certbot_domain not in result:
    print('***ERROR: The requested domain {} was not found in this ovh account'
          .format(certbot_domain))
    exit(1)

# Look for existing _acme-challenge record
result = client.get('/domain/zone/' + certbot_domain + '/record',
                    fieldType='TXT',
                    subDomain='_acme-challenge',
                    )

if len(result) == 0:
    print('***ERROR: Existing _acme-challenge record not found, exiting')
    exit(1)

record_id = result[0]

result = client.delete('/domain/zone/{}/record/{}'
                       .format(certbot_domain, str(record_id)))

if result is not None:
    print('***ERROR: something went wrong when removing DNS record')
    pp.pprint(result)
    exit(1)


result = client.post('/domain/zone/{}/refresh'.format(certbot_domain))

if result is not None:
    print('***ERROR: something went wrong when refreshing DNS zone')
    pp.pprint(result)
    exit(1)
else:
    print('All good, DNS record deleted')
