import os.path
import json

class Register:
    def __init__(self, name, addresses, writeable):
        self.name = name
        self.addresses = addresses
        self.writeable = writeable

    def is_array_reg(self):
        return isinstance(self.addresses, list)

    def to_dict(self):
        return {
            'name': self.name,
            'addresses': self.addresses,
            'writeable': self.writeable
        }

    def __str__(self):
        return f'{self.name} @ {str(self.addresses)}'

    @staticmethod
    def from_dict(d):
        return Register(
            name=d['name'],
            addresses=d['addresses'],
            writeable=d['writeable']
        )

def read_json_file(dir_name, file_name='reg_list.json'):
    d = json.load(open(os.path.join(dir_name, file_name), 'r'))
    return from_dict(d)

def from_dict(lis):
    return [Register.from_dict(d) for d in lis]

def write_json_file(dir_name, jtag_properties, file_name='reg_list.json'):
    d = to_dict(jtag_properties)
    json.dump(d, open(os.path.join(dir_name, file_name), 'w'))

def to_dict(jtag_properties):
    return [reg.to_dict() for reg in to_reg_list(jtag_properties)]

def to_reg_list(jtag_properties):
    reg_list = []

    for domain in ['tc', 'sc']:
        for ii in range(jtag_properties['reg_files'][domain][0]['num_of_reg']):
            name = jtag_properties['reg_files'][domain][0]['registers'][ii]['Name']
            address = ii*4 + 4096

            if jtag_properties['reg_files'][domain][0]['registers'][ii]['IEO'] == 'o':
                writeable = True
            else:
                writeable = False

            reg_list.append(Register(name=name, addresses=address, writeable=writeable))

        for ii in range(1, jtag_properties['num_of_reg_files'][domain]):
            base_name = jtag_properties['reg_files'][domain][ii]['registers'][0]['Name']
            num_of_reg = jtag_properties['reg_files'][domain][ii]['num_of_reg']

            if jtag_properties['reg_files'][domain][ii]['registers'][0]['IEO'] == 'o':
                writeable = True
            else:
                writeable = False

            addresses = [jj*4 + 4096 + 256 + 256*ii for jj in range(num_of_reg)]

            reg_list.append(Register(name=base_name, addresses=addresses, writeable=writeable))

    return reg_list
