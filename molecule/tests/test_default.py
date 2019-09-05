import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.fixture(scope='module')
def influx_user(host):
    ansible_vars = host.ansible.get_variables()
    user = ansible_vars.get('influxdb_os_user', 'influx')
    group = ansible_vars.get('influxdb_os_group', 'influx')

    return {'user': user, 'group': group}


@pytest.mark.parametrize('pkg', [
    'podman',
    'python3-influxdb',
    'firewalld'
    # 'libselinux-python'
])
def test_influx_packages_installed(host, pkg):
    package = host.package(pkg)
    assert package.is_installed


def test_influxdb_systemd_config(host):
    data = host.file('/etc/systemd/system/influxdb-service.service')

    assert data.exists
    assert data.user == 'root'
    assert data.group == 'root'


def test_influxdb_user(host, influx_user):

    user = host.user(influx_user['user'])

    assert user.group == influx_user['group']


def test_influxdb_config(host, influx_user):

    for fname in ['/etc/influxdb',
                  '/etc/influxdb/env']:
        data = host.file(fname)

        assert data.exists
        assert data.user == influx_user['user']
        assert data.group == influx_user['group']


@pytest.mark.parametrize('srv', [
    'influxdb-service',
    'firewalld'
])
def test_influxdb_running(host, srv):
    service = host.service(srv)

    assert service.is_running
    assert service.is_enabled


def test_influx_operating(host):
    curl = host.ansible('uri', 'url=http://localhost:8086/metrics',
                        check=False)
    assert(curl['status'] == 200)

    r = host.socket('tcp://0.0.0.0:8086')
    assert(r.is_listening)
