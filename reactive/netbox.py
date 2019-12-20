#!/usr/bin/env python

from charmhelpers.contrib.ansible import apply_playbook
from charmhelpers.contrib.charmsupport import nrpe
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import open_port
from charmhelpers.core.hookenv import status_set
from charms.layer.nagios import install_nagios_plugin_from_file
from charms.reactive.decorators import hook
from charms.reactive.decorators import when
from charms.reactive.decorators import when_not
from charms.reactive.flags import clear_flag
from charms.reactive.flags import register_trigger
from charms.reactive.flags import set_flag

register_trigger(when='config.changed', clear_flag='netbox.configured')
register_trigger(when='config.changed.check_docker_params',
                 clear_flag='netbox.nrpe.configured')
register_trigger(when='db.master.changed', clear_flag='netbox.configured')


@when_not('db.connected')
@when_not('netbox.db.requested')
def missing_pgsql():
    status_set('blocked', 'missing postgresql relation')


@when('db.connected')
@when_not('netbox.db.created')
def request_db(pgsql):
    status_set('maintenance', 'setting up postgresql db')
    pgsql.set_database('netbox')
    status_set('active', 'ready')
    set_flag('netbox.db.created')


@when('netbox.db.created')
@when('db.connected')
@when_not('db.master.available')
def waiting_on_pgsql_master():
    status_set('waiting', 'waiting on postgresql master to become available')


@when('netbox.db.created')
@when('db.master.available')
@when_not('netbox.configured')
def configure_netbox():
    status_set('maintenance', 'configuring netbox')
    apply_playbook(playbook='ansible/playbook.yaml')
    open_port(80)
    status_set('active', 'ready')
    set_flag('netbox.configured')


@when('netbox.configured')
@when('nrpe-external-master.available')
@when_not('netbox.nrpe.configured')
def configure_nrpe_checks():
    install_nagios_plugin_from_file(
        source_file_path='/opt/netbox-docker/checks/check_docker',
        plugin_name='check_docker')
    containers = ['netbox', 'netbox-worker', 'nginx', 'redis']
    nrpe_setup = nrpe.NRPE(hostname=nrpe.get_nagios_hostname(), primary=True)
    nrpe_setup.add_check(
        shortname='check_http_netbox',
        description='Check netbox web server',
        check_cmd='{check_path} -H localhost -p 80'.format(
            check_path='/usr/lib/nagios/plugins/check_http')
    )
    for container in containers:
        nrpe_setup.add_check(
            shortname='check_docker_{container}'.format(container=container),
            description='Check netbox {container} container'.format(
                container=container),
            check_cmd='{check_path} --containers {container} {params}'.format(
                check_path='/usr/lib/nagios/plugins/check_docker',
                container=container,
                params=config('check_docker_params')
            )
        )
    nrpe_setup.write()
    set_flag('netbox.nrpe.configured')


@when('target.available')
@when('netbox.configured')
@when('config.set.metrics_enabled')
@when_not('netbox.prometheus.configured')
def configure_prometheus(target):
    target.configure(port=80)
    set_flag('netbox.prometheus.configured')


@hook('upgrade-charm')
def upgrade_charm():
    clear_flag('netbox.configured')
    clear_flag('netbox.nrpe.configured')
