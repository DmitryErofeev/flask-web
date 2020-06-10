from flask import Flask, render_template
import pynetbox
import netaddr
import os
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__ﬁle__))

app = Flask(__name__)

app.conﬁg['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'test1.db')
app.conﬁg['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.conﬁg['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['MAIL_SERVER'] = '127.0.0.1'
# app.config['MAIL_PORT'] = 1025
# # app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
# app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <nyam@nyamnyam.com>'
# app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')


nb_url = 'http://10.100.3.128:33080/'
token = '0123456789abcdef0123456789abcdef01234567'

db = SQLAlchemy(app)
nb = pynetbox.api(nb_url, token, threading=True)
manager = Manager(app)
migrate = Migrate(app, db)
# mail = Mail(app)
# создаем комманду db для миграции
manager.add_command('db', MigrateCommand)


# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role')

#     def __repr__(self):
#         return '<Your role: %r>' % self.name


# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     nickname = db.Column(db.String(64))

#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

#     animals = db.relationship('Animal', backref='owner')

#     def __repr__(self):
#         return 'User: id:{}, username:{},role_id:{}, nickname:{}'.format(self.id, self.username, self.role_id, self.nickname)


# class Animal(db.Model):
#     __tablename__ = 'animals'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(140))
#     nickname = db.Column(db.String(140))
#     type_of_animal = db.Column(db.String(100))

#     owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#     def __repr__(self):
#         return 'Animal id:{}, Animal name:{}, Animal nickname:{}, type_of_animal:{}'.format(self.id, self.name, self.nickname, self.type_of_animal)


# def send_email(to, subject, template, **kwargs):
#     msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
#                   sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
#     msg.body = render_template(template + '.txt', **kwargs)
#     msg.html = render_template(template + '.html', **kwargs)
#     mail.send(msg)


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
