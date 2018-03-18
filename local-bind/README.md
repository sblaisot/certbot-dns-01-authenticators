# Certbot manual hook scripts for local bind zone files

These two scripts are intended to be used to authenticate using ACME/letsencrypt
DNS-01 validation when you use a bind DNS server with zone files on the same
server than the one requesting the certificate.

## Configuration

Copy `config.sh.example` to `config.sh` and adjust it to suit your needs

## Usage

```
$ certbot certonly \
  -- manual \
  --manual-auth-hook /opt/le-scripts/local-bind/auth.sh \
  --manual-cleanup-hook /opt/le-scripts/local-bind/cleanup.sh \
  -d '*.domain.tld'
```

## Known bugs / limitations

  * This scripts expects to find all zone files in the same directory and
    with the same filename format (configurable)
  * The zone file must contain the serial alone on its line with a comment
    allowing this script to find it. For example you can use a definition
    in the form:

```
@       IN      SOA     ns.domain.tld. hostmaster.domain.tld. (
                        2018031603      ; serial number of this zone file
                        6H              ; slave refresh (1 day)
                        15M             ; slave retry time in case of a problem (2 hours)
                        4W              ; slave expiration time (4 weeks)
                        1H )            ; minimum caching time in case of failed lookups (1 hour)
```
