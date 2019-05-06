import sys
from math import *

const_packs = {}
interfaces  = {} 
consts      = {} 

list_of_files = sys.argv[1:]

sort_files = {
                'intf': interfaces,
                'pack': const_packs
             }

for dir_file_name in list_of_files:
    tokens    = dir_file_name.strip().split('/')
    directory = tokens[0]
    file_name = tokens[1]
   
    sort_files[directory][file_name] = []


#Modify the Genesis code to take constant parameters and remove this
for const_pack in const_packs:
    with open('pack/' + const_pack) as f:
        for line in f:
            line = line.split(';')[0]
            tokens = line.strip().split()
            
            if not tokens:
                continue
            
            if tokens[0] == 'localparam':
                consts[tokens[2]] = int(tokens[4])
                exec(str(tokens[2]) + ' = ' + str(tokens[4]))
def clog2(val):
    return ceil(log2(val))

def evaluate(expr):
    return eval(expr)

io_list = {}        
        
for interface in interfaces:
    with open('intf/' + interface) as f:
        is_JTAG_modport = False
        for line in f:
            io_properties = {}
            line = line.split(';')[0]
            tokens = line.strip().split()
            if not tokens:
                continue 
            if tokens[0] == 'logic':
                is_signed = (tokens[1] == 'signed')
                io_properties['signed'] = is_signed
                io_properties['width'] = 1
                io_properties['array'] = 1

                tokens = tokens[1+is_signed:]
                tokens = "".join(tokens).replace('[',' [').replace(']','] ').split()
                width_locations = ['[' in token for token in tokens]
                name_loc = width_locations.index(False)
                for ii in range(len(tokens)):
                    width_loc = width_locations[ii]
                    token     = tokens[ii]
                    if width_loc:
                        bounds = token.replace('[','').replace(']','').replace('$','').split(':')
                        if ii < name_loc:
                            io_properties['width'] = evaluate(bounds[0]) + 1
                        elif ii > name_loc:
                            io_properties['array'] = evaluate(bounds[0]) + 1
                io_list[tokens[name_loc]] = io_properties
            if (tokens[0]  == 'input') and not is_JTAG_modport:
                io_list[tokens[1].strip(',')]['ioe'] = 'in'
            if (tokens[0]  == 'output') and not is_JTAG_modport:
                io_list[tokens[1].strip(',')]['ioe'] = 'out'
            if tokens[0] == 'modport':
                is_JTAG_modport = (tokens[1] == 'jtag')


io_list_strings = []
num_io_list = 0
for name in io_list:
    if io_list[name]['array'] == 1:
        io_list_strings.append("{{name => \'{}\', width => {},  direction => \'{}\',  bsr => \'yes\', orientation => \'top\'}}".format(
            name, 
            io_list[name]['width'],
            io_list[name]['ioe']))
        num_io_list += 1
    else:
        for ii in range(io_list[name]['array']):
            io_list_strings.append( "{{name => \'{}\', width => {},  direction => \'{}\',  bsr => \'yes\', orientation => \'top\'}}".format(
                "{}_{}".format(name, str(ii)), 
                io_list[name]['width'],
                io_list[name]['ioe']))
            num_io_list += 1


for ii in range(num_io_list):
    end_token = ',\n'
    print(io_list_strings[ii], end=end_token)

