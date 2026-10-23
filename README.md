# Paramiko SSH & SCP Tutorial

![Python](https://img.shields.io/badge/Python-v^3.12-blue.svg?logo=python&longCache=true&logoColor=white&colorB=5e81ac&style=flat-square&colorA=4c566a)
![Paramiko](https://img.shields.io/badge/Paramiko-v^5.1-blue.svg?longCache=true&logo=python&style=flat-square&logoColor=white&colorB=5e81ac&colorA=4c566a)
![SCP](https://img.shields.io/badge/SCP-v^0.15-blue.svg?longCache=true&logo=python&style=flat-square&logoColor=white&colorB=5e81ac&colorA=4c566a)
![GitHub Last Commit](https://img.shields.io/github/last-commit/google/skia.svg?style=flat-square&colorA=4c566a&colorB=a3be8c&logo=GitHub)
[![GitHub Issues](https://img.shields.io/github/issues/hackersandslackers/paramiko-tutorial.svg?style=flat-square&colorA=4c566a&logo=GitHub&colorB=ebcb8b)](https://github.com/hackersandslackers/paramiko-tutorial/issues)
[![GitHub Stars](https://img.shields.io/github/stars/hackersandslackers/paramiko-tutorial.svg?style=flat-square&colorA=4c566a&logo=GitHub&colorB=ebcb8b)](https://github.com/hackersandslackers/paramiko-tutorial/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/hackersandslackers/paramiko-tutorial.svg?style=flat-square&colorA=4c566a&logo=GitHub&colorB=ebcb8b)](https://github.com/hackersandslackers/paramiko-tutorial/network)

![Paramiko Tutorial](./.github/paramiko@2x.jpg)

Source code for the accompanying tutorial found here: https://hackersandslackers.com/ssh-scp-in-python-with-paramiko/

## Getting Started


### Installation

```shell
$ git clone https://github.com/hackersandslackers/paramiko-tutorial.git
$ cd paramiko-tutorial
$ make install
$ make run
```

### Configuration

Replace the values in **.env.example** with your values and rename this file to **.env**:

* `ENVIRONMENT`: Contextual environment the script is being on.
* `SSH_REMOTE_HOST`: IP address (or URL) of remote host to SSH into.
* `SSH_USERNAME`: Username for connecting to remote host.
* `SSH_PASSWORD` _(optional)_: Password of user SSHing into remote host via basic auth.
* `SSH_KEY_FILEPATH`: /path/to/local/sshkey
* `SCP_DESTINATION_FOLDER` _(optional)_: Remote directory to serve as destination for file uploads.

*Remember to never commit secrets saved in .env files to Github.*

-----

**Hackers and Slackers** tutorials are free of charge. If you found this tutorial helpful, a [small donation](https://www.buymeacoffee.com/hackersslackers) would be greatly appreciated to keep us in business. All proceeds go towards coffee, and all coffee goes towards more content.

## Security and supported setup

Use Python 3.12 or newer (CI exercises 3.12 and 3.14), uv 0.13.4 or newer,
and Poetry 2.5.1. Install uv from its official distribution, then run
`uv tool install poetry==2.5.1 --with poetry-plugin-export==1.10.1` and
`poetry sync`. The committed Poetry lock is the dependency source of truth.
Do not use an outdated system pip to bootstrap downloads; pip must be at least
26.2.2 for the October 2026 CA trust-store update.

SSH connections now reject unknown or changed host keys. Before running against
a device, independently verify its host-key fingerprint with the administrator
and provision the verified key in your user's `~/.ssh/known_hosts`. Do not trust
an unverified `ssh-keyscan` result. NETCONF on a nonstandard port needs the
corresponding `[hostname]:port` entry as well. No automatic key enrollment or
host-key bypass is provided. Existing deployments without verified keys will
fail closed until the operator provisions them.

Tests use mocks only and do not contact hosts or change device configuration.
Run `poetry run pytest` before using this tutorial. No live device compatibility
or deployment is claimed by these offline checks.

Creating RemoteClient no longer invokes ssh-copy-id or any shell command. Provision
authorized SSH credentials separately through your normal administrator-approved
process. `requirements.txt` is a hash-bearing export of the same lock; regenerate
with `poetry export -f requirements.txt --output requirements.txt` after updates.
`make install` uses uv to avoid bootstrapping through an outdated pip CA bundle.
