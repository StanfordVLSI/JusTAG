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
                if tokens[name_loc] in io_list:
                    print(io_properties)
                    print(tokens[name_loc])
                    exit()
                io_list[tokens[name_loc]] = io_properties
            if (tokens[0]  == 'input') and not is_JTAG_modport:
                io_list[tokens[1].strip(',')]['ioe'] = 'out'
            if (tokens[0]  == 'output') and not is_JTAG_modport:
                io_list[tokens[1].strip(',')]['ioe'] = 'in'
            if tokens[0] == 'modport':
                is_JTAG_modport = (tokens[1] == 'jtag')


#Put all the non-array IO into a single JTAG register file
#Put all the array IO into their own JTAG register file
reg_files = {0 : {}}
max_sc_width = 0
max_sc_addr  = 0
max_tc_width = 0
max_tc_addr = 0 
io_list_strings = []
num_io_list = 0
num_reg_file = 1
num_bank_0_reg = 0
for name in io_list:
    io_list_strings.append("{{name => \'{}\', bitwidth => {}, array=>{},  direction => \'{}\',  bsr => \'yes\', orientation => \'top\'}}".format(
            name, 
            io_list[name]['width'],
            io_list[name]['array'],
            io_list[name]['ioe']))
    num_io_list += 1
    if io_list[name]['array'] == 1:
        reg_files[0][num_bank_0_reg] = {
                    "Name": "{}".format(name),
                    "pos" : '',                    
                    "Width" : io_list[name]['width'],
                    "IEO"   : io_list[name]['ioe'][0]
                    }
        num_bank_0_reg += 1
    else:
        num_bank = io_list[name]['array']
        reg_files[num_reg_file] = {"num_bank":num_bank}
        for ii in range(num_bank):
            reg_files[num_reg_file][ii] = {
                    "Name": "{}".format(name, ii),
                    "pos" : ii,
                    "Width" : io_list[name]['width'],
                    "IEO"   : io_list[name]['ioe'][0]
                    }
        num_reg_file += 1
    if max_sc_width < io_list[name]['width']:
        max_sc_width = io_list[name]['width']
reg_files[0]["num_bank"] = num_bank_0_reg

io_list_gen_str = ""
for ii in range(num_io_list):
    begin_token = '//;\t\t\t'
    end_token = ',\n'
    io_list_gen_str += begin_token + ' ' + io_list_strings[ii] + end_token
io_list_gen_str = io_list_gen_str[0:-1]

max_sc_addr = clog2(num_bank*256 + 256)
max_tc_width = 32;
max_tc_addr  = 12;

intf_regfile_gen_str = ""
intf_regfile_int_str = ""
sc_reg_file_gen_str = ""
tc_reg_file_gen_str = ""
sc_rf2rf_gen_str = ""
sc_rf2rf_int_str = ""
tc_rf2rf_gen_str = ""
tc_rf2rf_int_str = ""
cfg_bus_info_str = ""
sc_jtag_regfile_con_str = ""
tc_jtag_regfile_con_str = ""
jtag_regfile_gen_str = ""
jtag_driver_cfg_params = ""

jtag_driver_cfg_params += "parameter sc_bus_width = {};\n".format(max_sc_width)
jtag_driver_cfg_params += "parameter sc_addr_width = {};\n".format(max_sc_addr)
jtag_driver_cfg_params += "parameter tc_bus_width = {};\n".format(max_tc_width)
jtag_driver_cfg_params += "parameter tc_addr_width = {};\n".format(max_tc_addr)
for ii in range(num_reg_file):
    sc_reg_file_gen_str += '//Register Bank {}:\n'.format(ii)
    sc_reg_file_gen_str += '//;my $regfile{}_on_sysclk = generate(\'reg_file\', \'regfile{}_on_sysclk\',\n'.format(ii, ii)
    sc_reg_file_gen_str += '//;\t\t\tCfgBusPtr => $sc_jtag2rf0_ifc,\n'
    sc_reg_file_gen_str += '//;\t\t\tCfgOpcodes => $sc_cfg_ops,\n'
    sc_reg_file_gen_str += '//;\t\t\tBaseAddr => {},\n'.format(hex((ii+1)*256))
    sc_reg_file_gen_str += '//;\t\t\tRegList =>[\n'
    num_bank = reg_files[ii]["num_bank"]
    for jj in range(num_bank-1):
        reg = reg_files[ii][jj]
        if not reg["pos"] == '':
            out_str =  "{{Name => \'{}_{}\', Width=>{}, IEO=>\'{}\'}}".format(reg["Name"], reg["pos"], reg["Width"], reg["IEO"])
        else:
            out_str =  "{{Name => \'{}\', Width=>{}, IEO=>\'{}\'}}".format(reg["Name"], reg["Width"], reg["IEO"])
        sc_reg_file_gen_str += '//;\t\t\t\t\t{},\n'.format(out_str)
    reg = reg_files[ii][num_bank-1]
    if not reg["pos"] == '':
        out_str =  "{{Name => \'{}_{}\', Width=>{}, IEO=>\'{}\'}}".format(reg["Name"], reg["pos"], reg["Width"], reg["IEO"])
    else:
        out_str =  "{{Name => \'{}\', Width=>{}, IEO=>\'{}\'}}".format(reg["Name"], reg["Width"], reg["IEO"])
    sc_reg_file_gen_str += '//;\t\t\t\t\t{}\n'.format(out_str)
    sc_reg_file_gen_str += '//;\t\t\t\t]\n'
    sc_reg_file_gen_str += '//;\t\t\t);\n'
    
    sc_reg_file_gen_str += '`$regfile{}_on_sysclk->instantiate` (.Clk(ifc.Clk),\n'.format(ii)
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

cfg_bus_info_str += "//; my $sc_cfg_bus_width = $self->define_param(SYSCLK_CFG_BUS_WIDTH => {});\n".format(max_sc_width)
cfg_bus_info_str += "//; my $sc_cfg_addr_width =  $self->define_param(SYSCLK_CFG_ADDR_WIDTH => {});\n".format(max_sc_addr)
cfg_bus_info_str += "//; my $tc_cfg_bus_width =  $self->define_param(TESTCLK_CFG_BUS_WIDTH => {});\n".format(32)
cfg_bus_info_str += "//; my $tc_cfg_addr_width =  $self->define_param(TESTCLK_CFG_ADDR_WIDTH => {});\n".format(12)

insertion_strings = {}

insertion_strings['cfg_bus_info'        ] = cfg_bus_info_str
insertion_strings['io_list_gen'         ] =  io_list_gen_str
insertion_strings['intf_regfile_gen'    ] = intf_regfile_gen_str
insertion_strings['intf_regfile_int'    ] = intf_regfile_int_str
insertion_strings['sc_regfile_gen'      ] = sc_reg_file_gen_str
insertion_strings['tc_regfile_gen'      ] = tc_reg_file_gen_str
insertion_strings['sc_rf2rf_gen'        ] = sc_rf2rf_gen_str
insertion_strings['sc_rf2rf_int'        ] = sc_rf2rf_int_str
insertion_strings['tc_rf2rf_gen'        ] = tc_rf2rf_gen_str
insertion_strings['tc_rf2rf_int'        ] = tc_rf2rf_int_str
insertion_strings['sc_jtag_regfile_con' ] = sc_jtag_regfile_con_str
insertion_strings['jtag_regfile_gen'    ] = jtag_regfile_gen_str
insertion_strings['tc_jtag_regfile_con' ] = tc_jtag_regfile_con_str
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
