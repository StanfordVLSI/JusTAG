import sys
from math import *
import mistune, pandas

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
    file_name = tokens[-1]
   
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
    if expr:
        return eval(expr)
    else:
        return 0

def convert_dimensions(expr):
    if not str(expr) == 'nan':
        return evaluate(expr.replace('$', '').split(':')[0])+1
    else:
        return 1

def convert_default(expr):
    if not str(expr) == 'nan':
        return 0 #needs to be a binary/hex to integer conversion 
    else:
        return 0

io_list = {}      

for interface in interfaces:
    with open('intf/' + interface) as intf_f:
        intf_txt = intf_f.read()
        intf_html = mistune.markdown(intf_txt)
        io_info = pandas.read_html(intf_html)[0]
        
        num_of_io = len(io_info)

        clean_interface = interface.split('_')[0]
        io_list[clean_interface] = {}

        for ii in range(num_of_io):
            name = io_info['Name'][ii]

            convert_domains = { 'System' : 'sc', 'Test' : 'tc' }

            width   = convert_dimensions( io_info['Packed Dim'][ii])
            array   = convert_dimensions( io_info['Unpacked Dim'][ii])
            signed  =                     io_info['Signed'][ii] == 'yes'
            ieo     =                     io_info['JTAG Dir'][ii]
            default = convert_default(    io_info['Reset Val'][ii])
            domain  = convert_domains[    io_info['Clock Domain'][ii]]
            
            io_list[clean_interface][name] = {
                'signed' : signed,
                'width'  : width,
                'array'  : array,
                'ieo'    : ieo,
                'default': default,
                'domain' : domain
        }   

#Put all the non-array IO into a single JTAG register file
#Put all the array IO into their own JTAG register file
domain_sel = {
				'sc' : "",
				'tc' : ""
			 }

jtag_properties =   { 
                        'reg_files' :   { 
                                           'tc' : {0 : {'address' : hex(256), 'num_of_reg' : 1, 'registers' : {}}},
                                           'sc' : {0 : {'address' : hex(256), 'num_of_reg' : 1, 'registers' : {}}}
                                        },
                        'max_width' :   {
                                           'tc' : 0, 
                                           'sc' : 0
                                        },
                        'max_addr'  :   {
                                           'tc' : 0, 
                                           'sc' : 0
                                        },
                        'num_of_reg_files' : {
                                                'tc' : 1,   
                                                'sc' : 1
                                               },
                        'io_list'   :   io_list
                    }

output_strings = { 'io_list' : {} }

num_io_list = 0

curr_reg_file = domain_sel.copy()
curr_reg_file['tc'] = 1
curr_reg_file['sc'] = 1


for interface in jtag_properties['io_list']:
    output_strings['io_list'][interface] = []
    for name in jtag_properties['io_list'][interface]:
        curr_io_list = jtag_properties['io_list'][interface][name]

        output_strings['io_list'][interface] += [("{{name => \'{}\', "
                                                  "bitwidth => {}, "
                                                  "array=>{},  "
                                                  "direction => \'{}\',  "
                                                  "bsr => \'yes\', "
                                                  "orientation => \'top\'}}").format(
                                                  name, 
                                                  curr_io_list['width'],
                                                  curr_io_list['array'],
                                                  curr_io_list['ieo'])]

        domain = curr_io_list['domain']
        if curr_io_list['array'] == 1:
            bank_0_pos = jtag_properties['reg_files'][domain][0]['num_of_reg']

            jtag_properties['reg_files'][domain][0]['registers'][bank_0_pos] = {
                    "Name"  : "{}".format(name),
                    "pos"   : '',                    
                    "Width" : curr_io_list['width'],
                    "IEO"   : curr_io_list['ieo'][0],
                    "ifc"   : interface
                    }
            jtag_properties['reg_files'][domain][0]['num_of_reg'] += 1
        else:
            num_of_reg = curr_io_list['array']

            reg_file_pos = curr_reg_file[domain]
            jtag_properties['num_of_reg_files'][domain] += 1
            jtag_properties['reg_files'][domain][reg_file_pos]               = {}
            jtag_properties['reg_files'][domain][reg_file_pos]['registers']  = {}
            jtag_properties['reg_files'][domain][reg_file_pos]['num_of_reg'] = num_of_reg
            jtag_properties['reg_files'][domain][reg_file_pos]['address']    = hex(256 + 256*reg_file_pos)
            registers = {}
            for ii in range(num_of_reg):
                registers[ii] = {
                    "Name"  : "{}".format(name, ii),
                    "pos"   : ii,
                    "Width" : curr_io_list['width'],
                    "IEO"   : curr_io_list['ieo'][0],
                    "ifc"   : interface
                    }
            jtag_properties['reg_files'][domain][reg_file_pos]['registers']  = registers

            curr_reg_file[domain] += 1
        if jtag_properties['max_width'][domain] < curr_io_list['width']:
            jtag_properties['max_width'][domain] = curr_io_list['width']

default_or_sized = {
                        'default' : { 'tc' : 32, 'sc' : 32},
                        'scaled'  : curr_reg_file
                    }


for domain in curr_reg_file:
    jtag_properties['max_width'][domain] = default_or_sized['default'][domain]
    jtag_properties['max_addr'][domain]  = clog2(curr_reg_file[domain]*256 + 256)

output_strings['io_list_gen']      = ""
output_strings['intf_regfile_gen'] = ""
output_strings['intf_regfile_int'] = ""
output_strings['reg_file_gen'] = domain_sel.copy()
output_strings['rf2rf_int'] = domain_sel.copy()
output_strings['rf2rf_gen'] = domain_sel.copy()
output_strings['cfg_bus_info'] = domain_sel.copy()
output_strings['jtag_regfile_con'] = domain_sel.copy()
output_strings['jtag_driver_cfg_params'] = domain_sel.copy()


for domain in ['tc', 'sc']:
    output_strings['jtag_driver_cfg_params'][domain] += "parameter {}_bus_width = {};\n".format(domain, jtag_properties['max_width'][domain])
    output_strings['jtag_driver_cfg_params'][domain] += "parameter {}_addr_width = {};\n".format(domain, jtag_properties['max_addr'][domain])
    
    str_sel = {
                    'sc' : 'SYSCLK',
                    'tc' : 'TESTCLK'
                 }

    output_strings['cfg_bus_info'][domain] += "//; my ${}_cfg_bus_width = $self->define_param({}_CFG_BUS_WIDTH => {});\n".format(
    												domain, str_sel[domain], jtag_properties['max_width'][domain])
    output_strings['cfg_bus_info'][domain] += "//; my ${}_cfg_addr_width =  $self->define_param({}_CFG_ADDR_WIDTH => {});\n".format(
    												domain, str_sel[domain],tag_properties['max_addr'][domain])
exit()
clock_sel = { 'sc' : 'sysclk', 'tc' : 'tstclk'}
for domain in ['tc', 'sc']:
	clock = clock_sel[domain]
    for ii in range(jtag_properties['num_of_reg_files'][domain]):
    	output_strings['reg_file_gen'][domain] += 	(
        											 	"//{} Domain: Register Bank {}:\n"
        											 	"//;my $regfile{}_on_{} = generate(\'reg_file\', \'regfile{}_on_{}\',\n"
        											 	"//;\t\t\tCfgBusPtr => ${}_jtag2rf0_ifc,\n"
        											 	"//;\t\t\tCfgOpcodes => ${}_cfg_ops,\n"
        											 	"//;\t\t\tBaseAddr => {},\n"
        											 	"//;\t\t\tRegList =>[\n"
        										    ).format(
        										    	domain, ii,
        										    	ii, clock, ii, clock,
        										    	domain,
        										    	domain,
        										    	hex((ii+1)*256)
        										    )
      	

		num_of_reg = jtag_properties['reg_files'][domain][ii]['num_of_reg']
		registers  = jtag_properties['reg_files'][domain][ii]['registers']

        for (reg, jj) in enumate(registers)
        	end_token_sel  = { True : "\n//;\t\t\t\t]\n//;\t\t\t);\n", False : ",\n"}
            name_token_sel = { True : "{}".format(reg["Name"]),        False : "{}_{}".format(reg["Name"], reg["pos"])}

            name_token = name_token_sel[reg['pos'] == '']
           	end_token  = end_token_sel[jj == (num_of_reg-1)]
            output_strings['reg_file_gen'][domain] += '//;\t\t\t\t\t//;{{Name => \'{}\', Width=>{}, IEO=>\'{}\'}}{}'.format(name_token, reg["Width"], reg["IEO"], end_token)
        
        sc_reg_file_gen_str += '`$regfile{}_on_{}->instantiate` (.Clk(ifc.'???"Clk),\n'.format(ii, clock)
        sc_reg_file_gen_str += '\t\t\t.Reset(ifc.Reset),\n'
        if ii == 0:
            sc_reg_file_gen_str += '\t\t\t.cfgIn(`$sc_jtag2rf{}_ifc->iname`.cfgIn),\n'.format(ii)
            sc_reg_file_gen_str += '\t\t\t.cfgOut(`$sc_rf{}2rf{}_ifc->iname`.cfgOut),\n'.format(ii, ii+1)
            sc_rf2rf_gen_str    += '//; my $sc_jtag2rf{}_ifc = generate(\'cfg_ifc\', \'sc_jtag2rf{}_ifc\',\n'.format(ii,ii)
            sc_rf2rf_gen_str    += '//;\t\t\t\tDataWidth => $sc_cfg_bus_width,\n'
            sc_rf2rf_gen_str    += '//;\t\t\t\tAddrWidth => $sc_cfg_addr_width);\n'
            sc_rf2rf_int_str    += '`$sc_jtag2rf{}_ifc->instantiate`();\n'.format(ii)
            sc_jtag_regfile_con_str += '\t\t\t.sc_cfgReq(`$sc_jtag2rf{}_ifc->iname`.cfgOut),\n'.format(ii)
            tc_jtag_regfile_con_str += '\t\t\t.tc_cfgReq(`$tc_jtag2jtag_ifc->iname`.cfgOut),\n'#.format(ii)
            jtag_regfile_gen_str += '//; my $cfg_dbg = generate(\'cfg_and_dbg\', \'cfg_and_dbg\',\n'
            sc_jtag_regfile_gen_str = 'SC_CFG_BUS => \'yes\', SC_CFG_IFC_REF => $sc_jtag2rf{}_ifc'.format(ii)
            tc_jtag_regfile_gen_str = 'TC_CFG_BUS => \'yes\', TC_CFG_IFC_REF => $tc_jtag2jtag_ifc'#.format(ii)
            #tc_jtag_regfile_gen_str = 'TC_CFG_BUS => \'yes\', TC_CFG_IFC_REF => $tc_jtag2rf{}_ifc'.format(ii)
            jtag_regfile_gen_str += '//;\t\t\t{},\n'.format(sc_jtag_regfile_gen_str) 
            jtag_regfile_gen_str += '//;\t\t\t{});'.format(tc_jtag_regfile_gen_str)
            tc_rf2rf_gen_str    += '//; my $tc_jtag2jtag_ifc = generate(\'cfg_ifc\', \'tc_jtag2jtag_ifc\',\n'
            tc_rf2rf_gen_str    += '//;\t\t\t\tDataWidth => $tc_cfg_bus_width,\n'
            tc_rf2rf_gen_str    += '//;\t\t\t\tAddrWidth => $tc_cfg_addr_width);\n'
            tc_rf2rf_int_str    += '`$tc_jtag2jtag_ifc->instantiate`();\n'
        elif ii == (num_reg_file-1):
            sc_reg_file_gen_str += '\t\t\t.cfgIn(`$sc_rf{}2rf{}_ifc->iname`.cfgIn),\n'.format(ii-1, ii)
            sc_reg_file_gen_str += '\t\t\t.cfgOut(`$sc_rf{}2jtag_ifc->iname`.cfgOut),\n'.format(ii)
            sc_rf2rf_gen_str    += '//; my $sc_rf{}2jtag_ifc = clone($sc_jtag2rf{}_ifc, \'sc_rf{}2jtag_ifc\');\n'.format(ii, 0, ii)
            sc_rf2rf_gen_str    += '//; my $sc_rf{}2rf{}_ifc = clone($sc_jtag2rf{}_ifc, \'sc_rf{}2rf2_ifc\');\n'.format(ii-1,ii, 0,ii-1, ii)
            sc_rf2rf_int_str    += '`$sc_rf{}2jtag_ifc->instantiate`();\n'.format(ii)
            sc_rf2rf_int_str    += '`$sc_rf{}2rf{}_ifc->instantiate`();\n'.format(ii-1,ii)
            sc_jtag_regfile_con_str += '\t\t\t.sc_cfgRep(`$sc_rf{}2jtag_ifc->iname`.cfgIn),\n'.format(ii)
            tc_jtag_regfile_con_str += '\t\t\t.tc_cfgRep(`$tc_jtag2jtag_ifc->iname`.cfgIn),\n'#.format(ii)
        else:
            sc_reg_file_gen_str += '\t\t\t.cfgIn(`$sc_rf{}2rf{}_ifc->iname`.cfgIn),\n'.format(ii-1,ii)
            sc_reg_file_gen_str += '\t\t\t.cfgOut(`$sc_rf{}2rf{}_ifc->iname`.cfgOut),\n'.format(ii, ii+1)
            sc_rf2rf_gen_str    += '//; my $sc_rf{}2rf{}_ifc = clone($sc_jtag2rf{}_ifc, \'sc_rf{}2rf{}_ifc\');\n'.format(ii-1,ii,0,ii-1,ii)
            sc_rf2rf_int_str    += '`$sc_rf{}2rf{}_ifc->instantiate`();\n'.format(ii-1,ii)
        if ii==0: 
            for jj in range(num_bank-1):
                reg = reg_files[ii][jj]
                sc_reg_file_gen_str += '\t\t\t.{}_{}(ifc.{}),\n'.format(reg["Name"], 'd' if reg['IEO']=='i' else 'q', reg["Name"] )
            reg = reg_files[ii][num_bank-1]
            sc_reg_file_gen_str += '\t\t\t.{}_{}(ifc.{})\n'.format(reg["Name"], 'd' if reg['IEO']=='i' else 'q', reg["Name"] )
            sc_reg_file_gen_str += '\t\t\t);\n'
        else:
            intf_regfile_gen_str += '// Register Bank {} and Interface Mapping\n'.format(ii)
            for jj in range(num_bank-1):
                reg = reg_files[ii][jj]
                sc_reg_file_gen_str += '\t\t\t.{}_{}_{}(ifc.{}[{}]),\n'.format(reg["Name"],
                                                                        reg["pos"],
                                                                        'd' if reg['IEO']=='i' else 'q',
                                                                        reg["Name"],
                                                                        reg["pos"] )
     #           intf_regfile_int_str += 'wire logic [{}:0] {};\n'.format(reg["Width"]-1, reg["Name"])
                name_ = "_".join(reg["Name"].split('_')[0:-1])
                pos_  = reg["Name"].split('_')[-1]
    #            intf_regfile_gen_str += 'assign ifc.{}[{}] = {};\n'.format(name_, pos_, reg["Name"])
            reg = reg_files[ii][num_bank-1]
            sc_reg_file_gen_str += '\t\t\t.{}_{}_{}(ifc.{}[{}])\n'.format(reg["Name"],
                                                                    reg["pos"],
                                                                    'd' if reg['IEO']=='i' else 'q',
                                                                    reg["Name"],
                                                                    reg["pos"] )
            sc_reg_file_gen_str += '\t\t\t);\n'
    #        intf_regfile_int_str += 'wire logic [{}:0] {};\n'.format(reg["Width"]-1, reg["Name"])
            name_ = reg["Name"]
            pos_  = reg["pos"]
    #        intf_regfile_gen_str += 'assign ifc.{}[{}] = {};\n\n\n'.format(name_, pos_, reg["Name"])
    

insertion_strings = {}

insertion_strings['cfg_bus_info'          ] = cfg_bus_info_str
insertion_strings['io_list_gen'           ] =  io_list_gen_str
insertion_strings['intf_regfile_gen'      ] = intf_regfile_gen_str
insertion_strings['intf_regfile_int'      ] = intf_regfile_int_str
insertion_strings['sc_regfile_gen'        ] = sc_reg_file_gen_str
insertion_strings['tc_regfile_gen'        ] = tc_reg_file_gen_str
insertion_strings['sc_rf2rf_gen'          ] = sc_rf2rf_gen_str
insertion_strings['sc_rf2rf_int'          ] = sc_rf2rf_int_str
insertion_strings['tc_rf2rf_gen'          ] = tc_rf2rf_gen_str
insertion_strings['tc_rf2rf_int'          ] = tc_rf2rf_int_str
insertion_strings['sc_jtag_regfile_con'   ] = sc_jtag_regfile_con_str
insertion_strings['jtag_regfile_gen'      ] = jtag_regfile_gen_str
insertion_strings['tc_jtag_regfile_con'   ] = tc_jtag_regfile_con_str
insertion_strings['jtag_driver_cfg_params'] = jtag_driver_cfg_params

actions = {
            'INSERT' : insertion_strings
          }

with open('rtl/digital/pre_template.svp', 'r') as fin:
    with open('rtl/digital/template.svp','w') as fout:
        for line in fin:
            tokens = line.strip().split()
            if not tokens:
                print(file=fout)
                continue
            if tokens[0] == '$$':
                print(actions[tokens[1]][tokens[2]], file=fout)
            else:
                print(line, file=fout, end="")
with open('verif/pre_JTAGDriver.svp', 'r') as fin:
    with open('verif/JTAGDriver.svp', 'w') as fout:
        for line in fin:
            tokens = line.strip().split()
            if not tokens:
                print(file=fout)
                continue
            if tokens[0] == '$$':
                print(actions[tokens[1]][tokens[2]], file=fout)
            else:
                print(line, file=fout, end="")
