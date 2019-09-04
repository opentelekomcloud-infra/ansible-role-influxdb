import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


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


def test_influxdb_user(host):
    user = host.user('influx')

    assert user.group == 'influx'


def test_influxdb_config(host):
    for fname in ['/etc/influxdb',
                  '/etc/influxdb/env']:
        data = host.file(fname)

        assert data.exists
        assert data.user == 'influx'
        assert data.group == 'influx'


@pytest.mark.parametrize('srv', [
    'influxdb-service',
    'firewalld'
])
def test_influxdb_running(host, srv):
    service = host.service(srv)

    assert service.is_running
    assert service.is_enabled
