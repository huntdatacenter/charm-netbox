# NetBox

![GitHub Action CI badge](https://github.com/huntdatacenter/charm-netbox/workflows/ci/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This charm deploys [NetBox][netbox-docs] and its required components Redis and Nginx in Docker containers.
It is based on the upstream [netbox-docker][netbox-docker-github] project, but uses an external persistent database.

## Usage

This charm requires a relation to a PostgreSQL database, for example [postgresql][postgresql-charm] charm:

```
juju deploy cs:~huntdatacenter/netbox
juju deploy postgresql
juju add-relation netbox:db postgresql:db
```

You can find the IP of the service with:

```
juju status netbox
```

The default superuser account has the following details:

- Username: `admin`
- Email: `admin@example.com`

The password of the superuser can be retrieved with:

```
juju ssh netbox/0 sudo cat /opt/netbox-docker/secrets/superuser_password
```

## Monitoring

This charm can be monitored by Nagios with the [nrpe][nrpe-charm] subordinate charm.
Additional NRPE checks for the Docker containers are done by the [check_docker][check-docker-github] Nagios plugin.
The [check_docker][check-docker-github] parameters can be edited with the `check_docker_params` configuration option.

```
juju deploy nrpe
juju relate netbox nrpe
```

## Metrics

NetBox supports exposing native Prometheus metrics from the application out of the box.
This endpoint can be disabled by setting the `metrics_enabled` configuration option to false.
See the [NetBox Prometheus][netbox-prometheus] docs for more information.

```
juju relate netbox:target prometheus:target
```

## Development

Here are some helpful commands to get started with development and testing:

```
$ make help
lint                 Run linter
build                Build charm
deploy               Deploy charm
upgrade              Upgrade charm
force-upgrade        Force upgrade charm
test-bionic-base     Test Bionic base bundle
test-bionic-nrpe     Test Bionic nrpe bundle
test-bionic-replica  Test Bionic replica bundle
push                 Push charm to stable channel
clean                Clean .tox and build
help                 Show this help
```

## Further information

### Links

- [NetBox documentation][netbox-docs]
- [NetBox GitHub repository][netbox-github]
- [NetBox Docker GitHub repository][netbox-docker-github]
- [check_docker GitHub repository][netbox-docker-github]

[netbox-docs]: https://netbox.readthedocs.io/en/stable/
[netbox-prometheus]: https://netbox.readthedocs.io/en/stable/additional-features/prometheus-metrics/
[netbox-github]: https://github.com/netbox-community/netbox
[netbox-docker-github]: https://github.com/netbox-community/netbox-docker
[postgresql-charm]: https://jaas.ai/postgresql
[nrpe-charm]: https://jaas.ai/nrpe
[check-docker-github]: https://github.com/timdaman/check_docker
