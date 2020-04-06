import pynetbox
import netaddr
from flask import Flask, render_template

app = Flask(__name__)

nb_url = 'http://10.100.3.128:33080/'
token = '0123456789abcdef0123456789abcdef01234567'

nb = pynetbox.api(nb_url, token, threading=True)
# spisok = nb.dcim.devices.all()[:10]
# spisok = nb.dcim.devices.filter(region='ku')


def count_dev(region):
    print("region:", region)
    _result = []
    _list = nb.dcim.devices.filter(region=region)

    for dev in _list:
        # _result.append(_list.format(dev.primary_ip, dev.device_type.model, dev.site, dev.device_type.manufacturer.slug))
        # _result.append([dev.primary_ip, dev.device_type.model, dev.site, dev.device_type.manufacturer.slug])
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




@app.route('/netbox/<region>')
def my2(region):
    _region = nb.dcim.regions.get(slug=region)
    return render_template('netbox.html', data=count_dev(region), region_name=_region.name)

@app.route('/device/<ip_address>')
def my3(ip_address):
    _address = nb.ipam.ip_addresses.get(address=ip_address)
    _device = _address.interface.device
    _interface_list = nb.dcim.interfaces.filter(device_id=_address.interface.device.id)    
    return render_template('ip_addresses.html', ip_address=ip_address, name=_device.name, ports=_interface_list)


# @app.route('/device/<ip_address>/<port>')
# def my4(ip_address, port):
    # return render_template('ports.html')
    #   dev_id = _address.interface.device.id
    # _port_id = 


@app.errorhandler(404)
def http_404_handler(error):
    return "404 Еще не готово", 404

    
if __name__ == '__main__':
    app.run()
