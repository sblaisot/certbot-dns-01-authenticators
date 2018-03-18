# Certbot manual hook scripts for Gandi's LiveDNS zones

These two scripts are intended to be used to authenticate using ACME/letsencrypt
DNS-01 validation when your DNS zone is hosted by Gandi's LiveDNS service (french
  provider).

## Configuration

Copy `config.py.example` to `config.py` and adjust it to suit your needs

## Usage

```
$ certbot certonly \
  -- manual \
  --manual-auth-hook /opt/le-scripts/gandi-livedns/auth.py \
  --manual-cleanup-hook /opt/le-scripts/gandi-livedns/cleanup.sh \
  -d '*.domain.tld'
```

## Known bugs / limitations

  * Server issuing the certificate should hold your private Gandi API key and
    thus can have full control over your DNS zone. Depending of your usage, this
    should be unwanted / dangerous. Use this at your own risks.
