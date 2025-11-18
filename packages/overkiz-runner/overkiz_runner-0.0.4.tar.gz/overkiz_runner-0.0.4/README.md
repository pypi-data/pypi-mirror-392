[![PyPI - Version](https://img.shields.io/pypi/v/overkiz-runner)](https://pypi.org/project/overkiz-runner/) [![Docker Image Version](https://img.shields.io/docker/v/jaesivsm/overkiz-runner)](https://hub.docker.com/r/jaesivsm/overkiz-runner/tags)

# Overkiz Runner

## Example configuration

```json
{
    "credentials": [
        {
            "username": "<login to your atlantic account>",
            "password": "<password to your atlantic account>",
            "servertype": "ATLANTIC_COZYTOUCH"
        }
    ]
}
```

## Running it

For the next few bits of code, we'll suppose you have a working configuration above in `~/.config/overkiz.json`.

### ... with python:

```shell
pip install overkiz-runner
python -m overkiz_runner
```

### ... with docker:

```shell
 docker run -v /home/jaes/.config/:/etc/overkiz/:ro overkiz-runner:main
```
