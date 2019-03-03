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
import dns.resolver
import os
import time
import string

wait_timeout = 180  # timeour in seconds
wait_loop_step = 2  # seconds between 2 checks

pp = pprint.PrettyPrinter(indent=4)

certbot_domain = os.environ.get("CERTBOT_DOMAIN")
try:
    certbot_domain
except NameError:
    print("***ERROR: CERTBOT_DOMAIN environment variable is missing, exiting")
    exit(1)

certbot_validation = os.environ.get("CERTBOT_VALIDATION").strip()
try:
    certbot_validation
except NameError:
    print('***ERROR: CERTBOT_VALIDATION environment variable missing, exiting')
    exit(1)

script_dir = os.path.dirname(os.path.realpath(__file__))
config_file = '{}/ovh.conf'.format(script_dir)

if not os.path.exists(config_file):
    print("***ERROR: config file not found")
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

result = client.get('/domain/zone/{}'.format(certbot_domain))

domain_nameservers = result['nameServers']

# Get IPs of zone DNS servers

local_resolver = dns.resolver.Resolver()
IP_nameservers = []
for nameserver in domain_nameservers:
    myAnswers = local_resolver.query(nameserver, "A")
    for rdata in myAnswers:
        IP_nameservers.append(str(rdata))
    myAnswers = local_resolver.query(nameserver, "AAAA")
    for rdata in myAnswers:
        IP_nameservers.append(str(rdata))

# Look for existing _acme-challenge record
result = client.get('/domain/zone/{}/record'.format(certbot_domain),
                    fieldType='TXT',
                    subDomain='_acme-challenge',
                    )

# This cript can be run multiple time on the same domain :
# domain.tld and *.domain.tld is the most obvious use case
# There will be 2 TXT record for the same key, which is OK
# but we need to be sure we check the one we adde dwith the
# right certbot_validation of this run.
for recordid in result:
    record = client.get('/domain/zone/{}/record/{}'.format(certbot_domain,
                    recordid), fieldType='TXT', subDomain='_acme-challenge')
    if record['target'] == certbot_validation:
        print("***ERROR: Existing _acme-challenge record found, exiting")
        exit(1)

result = client.post('/domain/zone/' + certbot_domain + '/record',
                     fieldType='TXT',
                     subDomain='_acme-challenge',
                     target=certbot_validation,
                     ttl=300,
                     )

try:
    result['id']
except:
    print("***ERROR: something went wrong when creating DNS record")
    pp.pprint(result)
    exit(1)

result = client.post('/domain/zone/' + certbot_domain + '/refresh')

if result is None:
    print("All good, DNS record created")
else:
    print("***ERROR: something went wrong when refreshing DNS zone")
    pp.pprint(result)
    exit(1)

# Now we loop requesting the zone DNS servers
# waiting for the record to be available
myResolver = dns.resolver.Resolver(configure=False)
myResolver.nameservers = IP_nameservers

elapsed = 0

print("Waiting for record to be available on DNS servers")

recordfound=False
while elapsed < wait_timeout and not recordfound:
    try:
        print("querrying DNS")
        myAnswers = myResolver.query('_acme-challenge.{}'
                                     .format(certbot_domain), "TXT")
        # As we can have multiple challenges for a single domain, check
        # for the specific one we added
        for rdata in myAnswers:
            for txt in rdata.strings:
                txtclean=txt.decode("ascii").strip()
                if txtclean == certbot_validation:
                    recordfound=True
    except dns.exception.DNSException as e:
        pass
    time.sleep(wait_loop_step)
    elapsed += wait_loop_step
    if not elapsed % 10:
        print(str(elapsed) + " seconds elapsed, still waiting...")

if elapsed >= wait_timeout:
    print('***ERROR: DNS record still not available on DNS servers '
          'after waiting for {} seconds'.format(str(elapsed)))
    exit(1)
else:
    print("DNS record available on DNS server")
