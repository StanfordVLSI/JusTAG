import os.path

def comment(contents, tab_count=1, tab_str='    '):
    tab = tab_str*tab_count
    return f'{tab}// {contents}\n'

def intparam(name, value, comment=None, tab_count=1, tab_str='    '):
    tab = tab_str*tab_count

    retval = ''
    retval += f'{tab}localparam integer {name} = {value};'
    if comment is not None:
        retval +=  f' // {comment}'
    retval += '\n'

    return retval

def arrparam(name, values, comment=None, tab_count=1, tab_str='    '):
    name = name + f' [{len(values)}]'
    value = "'{" + ", ".join([str(value) for value in values]) + "}"
    
    return intparam(name, value, comment=comment, tab_count=tab_count, tab_str=tab_str)

def write_reg_pack(dir_name, jtag_properties, pack_name='jtag_reg_pack'):
    file_name = os.path.join(dir_name, f'{pack_name}.sv')

    with open(file_name, 'w') as f:
        f.write(f'package {pack_name};\n')

        for domain in ['tc', 'sc']:
            f.write(comment(f'Domain: {domain}'))

            for ii in range(jtag_properties['reg_files'][domain][0]['num_of_reg']):
                name = jtag_properties['reg_files'][domain][0]['registers'][ii]['Name']
                address = ii*4 + 4096

                if jtag_properties['reg_files'][domain][0]['registers'][ii]['IEO'] == 'o':
                    writeable = True
                else:
                    writeable = False

                f.write(intparam(name, address, f'Writeable: {writeable}'))

            f.write('')

            for ii in range(1, jtag_properties['num_of_reg_files'][domain]):
                base_name = jtag_properties['reg_files'][domain][ii]['registers'][0]['Name']
                num_of_reg = jtag_properties['reg_files'][domain][ii]['num_of_reg']

                base_addr_val = jtag_properties['reg_files'][domain][ii]['address']
                if jtag_properties['reg_files'][domain][ii]['registers'][0]['IEO'] == 'o':
                    writeable = True
                else:
                    writeable = False

                addresses = [jj*4 + base_addr_val for jj in range(num_of_reg)]

                f.write(arrparam(base_name, addresses, f'Writeable: {writeable}'))


            f.write('\n')

        f.write('endpackage\n')
