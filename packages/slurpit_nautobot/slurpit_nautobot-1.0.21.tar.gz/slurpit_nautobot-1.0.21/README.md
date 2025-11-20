# Support & Community
If you need help, Join our Discord server: https://slurpit.io/discord
or e-mail us on: support@slurpit.io

# Nautobot Discovery Plugin
[Nautobot](https://github.com/nautobot/nautobot) plugin to automatically discover your network with [Slurp'it](https://slurpit.io).

## Compatibility

|    Nautobot Version    | Plugin Version |
|------------------------|----------------|
|    >= Nautobot 2.2.x   |    >= 0.8.x    |
|    >= Nautobot 2.3.x   |    >= 1.0.x    |

## Installation

The App/Plugin is available as a Python package in [pypi](https://pypi.org/project/slurpit_nautobot/) and can be installed with pip  

```
pip install slurpit_nautobot
```
Enable the App in nautobot_config.py:
```
PLUGINS = ['slurpit_nautobot']
```

Run nautobot-server post_upgrade, This command will ensure that any necessary post-installation tasks are run.
```
nautobot-server post_upgrade
```

Restart the WSGI Service and add `slurpit_nautobot` to your requirements.txt
```
sudo systemctl restart nautobot nautobot-worker
```

See [Nautobot Documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/installation/app-install) for details

## SSoT Integration

Slurp'it can also be used as a Data Source through Nautobot's SSoT feature. To enable this:

1. Install the SSoT plugin:
```
pip install "nautobot_ssot[slurpit]"
```

2. Add the SSoT configuration to nautobot_config.py:
```python
PLUGINS = ["nautobot_ssot"]

PLUGINS_CONFIG = {
    "nautobot_ssot": {
        "enable_slurpit": os.getenv("NAUTOBOT_SSOT_ENABLE_SLURPIT"),
    }
}
```

## Getting started
On our [getting started page](https://slurpit.io/getting-started/) you can take an Online Course to understand how the plugin works, or play with the plugin in a simulated network in our Sandbox.

## Changelog
Changelog can be found here: https://slurpit.io/knowledge-base/nautobot-plugin-changelog

## Training videos
We made a series of videos on how to use Slurp'it and Nautobot.
https://slurpit.io/online-courses/