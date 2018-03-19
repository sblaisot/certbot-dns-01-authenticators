# Certbot manual hook scripts for OVH hosted DNS zones

These two scripts are intended to be used to authenticate using ACME/letsencrypt
DNS-01 validation when your DNS zone is hosted by OVH service (french
  provider).

## requirements

This scripts require `ovh-python` and `dnspython`. install them with

```
$ sudo apt-get install python3-dnspython
$ sudo pip3 install ovh
```

## Configuration

Copy `ovh.conf.example` to `ovh.conf` and adjust it to suit your needs

## Usage

```
$ certbot certonly \
  -- manual \
  --manual-auth-hook /opt/le-scripts/ovh/auth.py \
  --manual-cleanup-hook /opt/le-scripts/ovh/cleanup.sh \
  -d '*.domain.tld'
```

## Known bugs / limitations

  * Server issuing the certificate should hold your private OVH API key and
    thus can have full control over your DNS zone or more. Depending of your usage,
    this should be unwanted / dangerous. Use this at your own risks.
