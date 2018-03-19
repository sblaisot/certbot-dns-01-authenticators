# Various certbot manual-hook scripts

This repository contains various scripts to be used as manual-hook with certbot.

These scripts are in charge of adding an entry to your domain DNS for letsencrypt
validation pusposes and to cleanup this entry after validation.

## Scripts

The following scripts are included in this repository:

  * [`test`](test): scripts for testing purposes only, it doesn't validate anything but instead prints the various environment variable certbot passes to him.
  * [`local-bind`](local-bind): To manage DNS zones when the bind zone file is directly accessible on the same machine (server being DNS master and web server simultaneously)
  * [`gandi-livedns`](gandi-livedns): To be used when your DNS provider is gandi (only for domains migrated to Gandi's liveDNS service)
  * [`ovh`](ovh): To be used when your DNS provider is OVH.

## Installation

First, clone this repository into `/opt/le-scripts`

```
$ sudo git clone https://github.com/sblaisot/certbot-dns-01-authenticators.git /opt/le-scripts
```

Then, adjust configuration of the script you need based on your exact DNS architecture.

Refer to the `README.md` file in each script subdirectory for instructions on how to
configure and use it.

## Usage

Usage is usually in the form:

```
$ certbot certonly \
    --manual \
    --manual-auth-hook /path/to/auth-script \
​​    --manual-cleanup-hook /path/to/cleanup-script \
    -d '*.domain.tld'
```

for details, refer to the `README.md` file in each script subdirectory.

## License

These scripts and programs are distributed under the GNU GPL V3 licence or any later version.
