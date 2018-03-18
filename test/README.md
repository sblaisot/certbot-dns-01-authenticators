# Certbot manual hook scripts for testing

These two scripts are intended to be used as a test / demonstration of certbot manual hooks for DNS-01 validation.

They simply print the environment variable certbot give them and exit.

## Configuration

No configuration required

## Usage

```
$ certbot certonly \
  -- manual \
  --manual-auth-hook /opt/le-scripts/test/auth.sh \
  --manual-cleanup-hook /opt/le-scripts/test/cleanup.sh \
  -d '*.domain.tld'
```
