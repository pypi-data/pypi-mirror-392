# certbot-dns-sprintbox

Certbot DNS-01 plugin for managing TXT records via Sprintbox control panel.

An authenticator plugin for [certbot](https://certbot.eff.org/) to support [Let's Encrypt](https://letsencrypt.org/) 
DNS challenges (dns-01) for domains managed by the nameservers of [sprintbox.ru](https://sprintbox.ru).


## Requirements

Sprintbox account settings must allow programmatic login with TOTP-based 2FA only (it is optional, but highly recommended):

- Enable TOTP 2FA and use its secret in `dns_sprintbox_totp_secret`.
- Disable all other login confirmations (email/SMS codes, IP checks).

You can review/change these settings at Sprintbox: https://cp.sprintbox.ru/security/auth-access

Script unchecks `save_device`

## Installation

```bash
sudo pip install certbot-dns-sprintbox
```

## Credentials file

Create an INI file (e.g. `sprintbox.ini`) with:

```ini
dns_sprintbox_username = YOUR_LOGIN
dns_sprintbox_password = YOUR_PASSWORD
dns_sprintbox_totp_secret = YOUR_TOTP_SECRET
```

## Usage with Certbot

```bash
certbot certonly \
  --authenticator dns-sprintbox \
  --dns-sprintbox-credentials /path/to/sprintbox.ini \
  --dns-sprintbox-propagation-seconds 120 \
  -d example.com
```

## SWAG

To use this plugin with [docker-swag](https://github.com/linuxserver/docker-swag) you need to follow their [guide](https://github.com/linuxserver/docker-swag?tab=readme-ov-file#certbot-plugins)

Add the following environment variables to your container:

```
DOCKER_MODS=linuxserver/mods:universal-package-install
INSTALL_PIP_PACKAGES=certbot-dns-sprintbox
```

Then modify `/config/dns-conf/sprintbox.ini` and provide credentials


## Removal
```
   sudo pip uninstall certbot-dns-sprintbox
```
