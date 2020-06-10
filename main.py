from flask import Flask, render_template
import pynetbox
import netaddr
from flask_script import Manager

app = Flask(__name__)
nb_url = 'http://10.100.3.128:33080/'
token = '0123456789abcdef0123456789abcdef01234567'
nb = pynetbox.api(nb_url, token, threading=True)
manager = Manager(app)


def count_dev(region):
    print("region:", region)
    _result = []
    _list = nb.dcim.devices.filter(region=region)

    for dev in _list:
        _result.append(
            {
                "ip": netaddr.IPNetwork(str(dev.primary_ip)).ip,
                "model": dev.device_type.model,
                "site": dev.site,
                "vendor": dev.device_type.manufacturer.slug,
                "role": dev.device_role
            }
        )

    return _result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/netbox/<region>')
def my2(region):
    _region = nb.dcim.regions.get(slug=region)
    return render_template('regions.html', data=count_dev(region), region=_region)


@app.route('/netbox/<region>/count')
def model_count(region):
    _result = {}
    _list = nb.dcim.devices.filter(region=region)
    for dev in _list:
        _result[dev.device_type.model] = 1 + _result.get(dev.device_type.model, 0)

    return render_template('region_count_dev.html', data=_result, count=len(_list))


@app.route('/device/<ip_address>')
def my3(ip_address):
    _address = nb.ipam.ip_addresses.get(address=ip_address)
    _device = _address.interface.device
    _interface_list = nb.dcim.interfaces.filter(device_id=_address.interface.device.id)
    return render_template('ip_addresses.html', ip_address=ip_address, name=_device.name, ports=_interface_list)


@app.errorhandler(404)
def http_404_handler(error):
    return "404 Нет такой страницы", 404


if __name__ == '__main__':
    manager.run()
