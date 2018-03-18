#!/bin/bash

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

ZONE_FILE=/etc/bind/zones/db.${CERTBOT_DOMAIN}

if [ ! -f ${ZONE_FILE} ]; then
  echo "***ERROR: zone file ${ZONE_FILE} not found"
  exit 1
fi

CURRENT_DATE=$(date +%Y%m%d)
ZONE_SERIAL=$(cat ${ZONE_FILE} | grep '; serial number of this zone file$' | awk '{ print $1 }')
ZONE_SERIAL_DATE=${ZONE_SERIAL:0:8}
ZONE_SERIAL_INCREMENT=${ZONE_SERIAL:8:2}

if [ "${ZONE_SERIAL_DATE}" = "${CURRENT_DATE}" ]; then
  NEW_INCREMENT=$((${ZONE_SERIAL_INCREMENT} + 1))
  # we limit to increment 98 because we need 2 changes to first add the challenge, then cleanup
  if [ ${NEW_INCREMENT} -le 0 -o ${NEW_INCREMENT} -gt 98 ]; then
    echo "***ERROR: increment is too big to keep serial format"
    exit 1
  fi
else
  NEW_INCREMENT="01"
fi

NEW_SERIAL=$(printf "${CURRENT_DATE}%02d" ${NEW_INCREMENT})

echo "Freeze zone"
rndc freeze ${CERTBOT_DOMAIN}

echo "Update serial"
sed -i -e 's/^.*\; serial number of this zone file$/                        '${NEW_SERIAL}'      ; serial number of this zone file/' ${ZONE_FILE}

echo "Add challenge to zone file"
echo "_acme-challenge		IN	TXT	${CERTBOT_VALIDATION}" >> ${ZONE_FILE}

echo "Release zone"
rndc thaw ${CERTBOT_DOMAIN}

echo "Wait 5 seconds for repplication to masters"
sleep 5

echo "Done"
