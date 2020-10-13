import sys
import os
import os.path
from math import *
import mistune, pandas

from justag import write_reg_pack, write_json_file


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
        if 'h' in expr:
            return int(expr.split('h')[1], 16)
        elif 'b' in expr:
            return int(expr.split('b')[1], 2)
        elif 'd' in expr:
            return int(expr.split('d')[1], 10)
        else:
            return int(float(expr))
    else:
        return 0

def jtag_directory():
    return os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))

def main():
    # get the top-level folder location
    JUSTAG_HOME = jtag_directory()

    const_packs = set()
    interfaces  = set()
    consts      = {} 


    ID_code       = sys.argv[1]
    list_of_files = sys.argv[3:]

    sort_files = {
                    'reg'  : interfaces,
                    'all' : const_packs
                 }

    for dir_file_name in list_of_files:
        tokens    = dir_file_name.strip().split('/')
        directory = tokens[-2]
        file_name, *file_exts = tokens[-1].split('.')
        if not len(file_exts) == 1:
            continue
        if file_exts[0] == 'md':
            interfaces = interfaces | {dir_file_name}
        elif file_exts[0] == 'sv':
            const_packs = const_packs | {dir_file_name}

    current_dir = os.getcwd()
    os.chdir(JUSTAG_HOME) 
    #Modify the Genesis code to take constant parameters and remove this
    for const_pack in const_packs:
        with open(const_pack) as f:
            for line in f:
                line = line.split(';')[0]
                tokens = line.strip().split()
                
                if not tokens:
                    continue
                
                if (tokens[0] == 'localparam') and (tokens[1] == 'integer'):
                    consts[tokens[2]] = int(tokens[4])

    for const in consts:
        exec(str(const) + ' = ' + str(consts[const]), globals())

    io_list = {}      

    for interface in interfaces:
        with open(interface) as intf_f:
            intf_txt = intf_f.read()
            intf_html = mistune.markdown(intf_txt)
            io_info = pandas.read_html(intf_html)[0]
            
            num_of_io = len(io_info)

            interface_wo_path = interface.split('/')[-1]

            clean_interface = interface_wo_path.split('_')[0]
            io_list[clean_interface] = {}

            for ii in range(num_of_io):
                name = io_info['Name'][ii]

                convert_domains = { 'System' : 'sc', 'Test' : 'tc' }

                width   = convert_dimensions( io_info['Packed Dim'][ii])
                array   = convert_dimensions( io_info['Unpacked Dim'][ii])
                signed  =                     int(io_info['Signed?'][ii] == 'yes')
                ieo     =                     io_info['JTAG Dir'][ii]
                default = []
                if not str(io_info['Reset Val'][ii]) == 'nan':
                    default_tokens = str(io_info['Reset Val'][ii]).split('&')
                else:
                    default_tokens = ['nan']

                num_of_default = len(default_tokens)
                assert(num_of_default <= array)

                for tok in default_tokens:
                    default += [convert_default(tok)]

                for jj in range(num_of_default, array, 1):
               	    default += [default[num_of_default-1]]

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
                                               'tc' : {0 : {'address' : 4096, 'num_of_reg' : 0, 'registers' : {}}},
                                               'sc' : {0 : {'address' : 4096, 'num_of_reg' : 0, 'registers' : {}}}
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

    size_pack_reg = int(sys.argv[2])
    curr_reg_file = domain_sel.copy()
    curr_reg_file['tc'] = 1 
    curr_reg_file['sc'] = 1  
    output_strings['io_list'] = ""

    for interface in jtag_properties['io_list']:

        for name in jtag_properties['io_list'][interface]:
            curr_io_list = jtag_properties['io_list'][interface][name]
            begin_token = '//;\t\t\t'
            end_token = ',\n'
            output_strings['io_list'] +=  begin_token +\
                                            ("{{name => \'{}\', "
                                            "bitwidth => {}, "
                                            "array=>{},  "
                                            "direction => \'{}\',  "
                                            "bsr => \'yes\', "
                                            "signed =>{}, "
                                            "orientation => \'top\'}}").format(
                                            name, 
                                            curr_io_list['width'],
                                            curr_io_list['array'],
                                            curr_io_list['ieo'],
                                            curr_io_list['signed']) +\
                                            end_token

            domain = curr_io_list['domain']
            if curr_io_list['array'] == 1:
                bank_0_pos = jtag_properties['reg_files'][domain][0]['num_of_reg']
                jtag_properties['reg_files'][domain][0]['address'] = 4096
                jtag_properties['reg_files'][domain][0]['registers'][bank_0_pos] = {
                        "Name"  : "{}".format(name),
                        "pos"   : '',                    
                        "Width" : curr_io_list['width'],
                        "IEO"   : curr_io_list['ieo'][0],
                        "ifc"   : interface,
                        "Default" : curr_io_list['default'][0]
                        }
                jtag_properties['reg_files'][domain][0]['num_of_reg'] += 1
            else:
                num_of_reg = curr_io_list['array']

                reg_file_pos = curr_reg_file[domain]
                jtag_properties['num_of_reg_files'][domain] += 1
                jtag_properties['reg_files'][domain][reg_file_pos]               = {}
                jtag_properties['reg_files'][domain][reg_file_pos]['registers']  = {}
                jtag_properties['reg_files'][domain][reg_file_pos]['num_of_reg'] = num_of_reg
                jtag_properties['reg_files'][domain][reg_file_pos]['address']    = 4096 + (size_pack_reg-1)*256+ 256*reg_file_pos
                registers = {}
                for ii in range(num_of_reg):
                    registers[ii] = {
                        "Name"  : "{}".format(name),
                        "pos"   : ii,
                        "Width" : curr_io_list['width'],
                        "IEO"   : curr_io_list['ieo'][0],
                        "ifc"   : interface,
                        "Default" : curr_io_list['default'][ii]
                        }
                jtag_properties['reg_files'][domain][reg_file_pos]['registers']  = registers

                curr_reg_file[domain] += 1
            if jtag_properties['max_width'][domain] < curr_io_list['width']:
                jtag_properties['max_width'][domain] = curr_io_list['width']
    output_strings['io_list'] = output_strings['io_list'][0:-1]
    default_or_sized = {
                            'default' : { 'tc' : 32, 'sc' : 32},
                            'scaled'  : curr_reg_file
                        }


    for domain in curr_reg_file:
        jtag_properties['max_width'][domain] = default_or_sized['default'][domain]
        jtag_properties['max_addr'][domain]  = clog2((size_pack_reg-1)*256+curr_reg_file[domain]*256 + 4096)

    # write register map to a SystemVerilog package
    write_reg_pack(current_dir, jtag_properties)

    # write register information to a JSON format
    write_json_file(current_dir, jtag_properties)

    os.chdir(JUSTAG_HOME)
    output_strings['reg_file_gen'] = domain_sel.copy()
    output_strings['rf2rf_int'] = domain_sel.copy()
    output_strings['rf2rf_gen'] = domain_sel.copy()
    output_strings['cfg_bus_info'] = domain_sel.copy()
    output_strings['jtag_regfile_con'] = domain_sel.copy()
    output_strings['jtag_driver_cfg_params'] = domain_sel.copy()
    output_strings['jtag_regfile_gen'] = ""


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
        												domain, str_sel[domain], jtag_properties['max_addr'][domain])

    clock_sel = { 'sc' : 'sysclk', 'tc' : 'tstclk'}
    domain_end_token_sel = { 'tc' : ');\n', 'sc' : ',\n' }

    output_strings['jtag_regfile_gen'] += '//; my $cfg_dbg = generate(\'cfg_and_dbg\', \'cfg_and_dbg\',\n'
    for domain in ['sc', 'tc']:
        clock = clock_sel[domain]
        jtag_regfile_gen_str = '{}_CFG_BUS => \'yes\', {}_CFG_IFC_REF => ${}_jtag2rf0_ifc'.format(domain.upper(), domain.upper(), domain)
        output_strings['jtag_regfile_gen'] += '//;\t\t\t{}{}'.format(jtag_regfile_gen_str, domain_end_token_sel[domain])
        for ii in range(jtag_properties['num_of_reg_files'][domain]):
            addr_val = hex(jtag_properties['reg_files'][domain][ii]['address'])
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
            										    	addr_val #hex(4096) if ii==0 else hex((ii+1)*256 + 4096)
            										    )
          	
            num_of_reg = jtag_properties['reg_files'][domain][ii]['num_of_reg']
            assert(num_of_reg <= 128 if ii==0 else 64), 'Register Overflow for Bank[{}] on {}_CLK'.format(ii, domain.upper())
            
            registers  = jtag_properties['reg_files'][domain][ii]['registers']

            for jj, kk in enumerate(registers):
                reg = registers[kk]
                
                end_token_sel  = { True : "\n//;\t\t\t\t]\n//;\t\t\t);\n", False : ",\n"}
                name_token_sel = { True : "{}".format(reg["Name"]),        False : "{}_{}".format(reg["Name"], reg["pos"])}
                name_token = name_token_sel[reg['pos'] == '']
                end_token  = end_token_sel[jj == (num_of_reg-1)]
                reg_string_sel = { 'i' : 
                                            (
                                              "//;\t\t\t\t\t{{"
                                              "Name  =>\'{}\', "
                                              "Width => {}, "
                                              "IEO   =>\'{}\'"
                                              "}}{}"
                                             ).format(
                                               name_token,
                                               reg["Width"],
                                               reg["IEO"],
                                               end_token
                                             ),
                                   'o' :
                                             ( 
                                               "//;\t\t\t\t\t{{"
                                               "Name  =>\'{}\', "
                                               "Width => {}, "
                                               "IEO   =>\'{}\',"
                                               "Default => {}"
                                               "}}{}"
                                             ).format(
                                               name_token,
                                               reg["Width"],
                                               reg["IEO"],
                                               reg["Default"],
                                               end_token
                                             )
                                 }
                 
                 
                output_strings['reg_file_gen'][domain] += reg_string_sel[reg["IEO"]]
                 
            regfile_clk_sel = { 'sc' : 'Clk', 'tc' : 'tck'}
            regfile_reset_sel = { 'sc' : 'ifc.Reset', 'tc' : 'test_logic_reset'}
            output_strings['reg_file_gen'][domain] += '`$regfile{}_on_{}->instantiate` (\n\t\t\t.Clk(ifc.{}),\n'.format(ii, clock, regfile_clk_sel[domain])
            output_strings['reg_file_gen'][domain] += '\t\t\t.Reset({}),\n'.format(regfile_reset_sel[domain])

            num_of_reg_files = jtag_properties['num_of_reg_files'][domain]
            rf_gen_sel = { 0 : 'jtag', 1 : 'rf0',num_of_reg_files-1: 'rf{}'.format(num_of_reg_files-1), num_of_reg_files : 'jtag'}
            rf_cfg_sel =    { 
                            0 : {
                                    0 : 'jtag', 
                                    1 :'rf0',
                                    num_of_reg_files-1: 'rf{}'.format(num_of_reg_files-2), 
                                    num_of_reg_files : 'rf{}'.format(num_of_reg_files-1)
                                },
                            1 : { 
                                    0 : 'rf0', 
                                    1 : 'rf1',
                                    num_of_reg_files-1: 'rf{}'.format(num_of_reg_files-1), 
                                    num_of_reg_files : 'jtag'
                                }
                            }
            rf2rf_gel_sel = {0 : 'generate(\'cfg_ifc\'', num_of_reg_files-1: 'clone(${}_jtag2rf0_ifc'.format(domain)}
            jrf_con = {0 : { 0 : 'q', num_of_reg_files-1 : 'p'}, 1 : { 0 : 'Out', num_of_reg_files-1 : 'In'}}

            if (ii==0) or (ii == (num_of_reg_files-1)):
                end_token_sel = {0: ',\n', num_of_reg_files-1:');\n'}
                output_strings['reg_file_gen'][domain] += '\t\t\t.cfgIn(`${}_{}2{}_ifc->iname`.cfgIn),\n'.format(
                    domain,
                    rf_cfg_sel[0][ii],
                    rf_cfg_sel[0][ii+1])
                output_strings['reg_file_gen'][domain] += '\t\t\t.cfgOut(`${}_{}2{}_ifc->iname`.cfgOut),\n'.format(
                    domain,
                    rf_cfg_sel[1][ii],
                    rf_cfg_sel[1][ii+1])
                output_strings['rf2rf_gen'][domain] += '//; my ${}_{}2{}_ifc = {}, \'{}_{}2{}_ifc\'{}'.format(
                    domain,
                    rf_gen_sel[ii],
                    rf_gen_sel[ii+1],
                    rf2rf_gel_sel[ii], 
                    domain,
                    rf_gen_sel[ii],
                    rf_gen_sel[ii+1],
                    end_token_sel[ii])
                output_strings['rf2rf_int'][domain] += '`${}_{}2{}_ifc->instantiate`();\n'.format(
                    domain,
                    rf_gen_sel[ii],
                    rf_gen_sel[ii+1])
                output_strings['jtag_regfile_con'][domain] += '\t\t\t.{}_cfgRe{}(`${}_{}2{}_ifc->iname`.cfg{}),\n'.format(
                    domain, 
                    jrf_con[0][ii],
                    domain,
                    rf_gen_sel[ii],
                    rf_gen_sel[ii+1],
                    jrf_con[1][ii])
            if ii == 0:
                output_strings['rf2rf_gen'][domain] += '//;\t\t\t\tDataWidth => ${}_cfg_bus_width,\n'.format(domain)
                output_strings['rf2rf_gen'][domain] += '//;\t\t\t\tAddrWidth => ${}_cfg_addr_width);\n'.format(domain)
            else:
                if not ii == (num_of_reg_files-1):
                    output_strings['reg_file_gen'][domain] += '\t\t\t.cfgIn(`${}_rf{}2rf{}_ifc->iname`.cfgIn),\n'.format(domain, ii-1,ii)
                    output_strings['reg_file_gen'][domain] += '\t\t\t.cfgOut(`${}_rf{}2rf{}_ifc->iname`.cfgOut),\n'.format(domain, ii, ii+1)
                output_strings['rf2rf_gen'][domain]    += '//; my ${}_rf{}2rf{}_ifc = clone(${}_jtag2rf{}_ifc, \'{}_rf{}2rf{}_ifc\');\n'.format(
                    domain, ii-1, ii, domain, 0, domain, ii-1, ii)
                output_strings['rf2rf_int'][domain]    += '`${}_rf{}2rf{}_ifc->instantiate`();\n'.format(domain, ii-1,ii)
            for jj, kk in enumerate(registers):
                reg = registers[kk]
                
                end_token_sel      = { True : "\n\t\t\t);\n", False : ",\n"}
                name_token_sel    = { True : "{}".format(reg["Name"]),        False : "{}_{}".format(reg["Name"], reg["pos"])}
                ifc_name_token_sel = { True : "{}".format(reg["Name"]),        False : "{}[{}]".format(reg["Name"], reg["pos"])}

                name_token = name_token_sel[reg['pos'] == '']
                ifc_name_token = ifc_name_token_sel[reg['pos'] == '']
                end_token  = end_token_sel[jj == (num_of_reg-1)]

                output_strings['reg_file_gen'][domain] += '\t\t\t.{}_{}(ifc.{}){}'.format(name_token, 'd' if reg['IEO']=='i' else 'q', ifc_name_token, end_token)


    insertion_strings = {}

    for domain in ['sc', 'tc']:
        insertion_strings[domain + '_cfg_bus_info'       ] = output_strings['cfg_bus_info'][domain]
        insertion_strings[domain + '_regfile_gen'        ] = output_strings['reg_file_gen'][domain]
        insertion_strings[domain + '_rf2rf_gen'          ] = output_strings['rf2rf_gen'][domain]
        insertion_strings[domain + '_rf2rf_int'          ] = output_strings['rf2rf_int'][domain]
        insertion_strings[domain + '_jtag_regfile_con'   ] = output_strings['jtag_regfile_con'][domain]
        insertion_strings[domain + '_jtag_driver_cfg_params'] = output_strings['jtag_driver_cfg_params'][domain]

    insertion_strings['io_list_gen'           ] = output_strings['io_list']
    insertion_strings['jtag_regfile_gen'      ] = output_strings['jtag_regfile_gen']
    
    
    output_strings['idcode'] = '//; my $IDCODE = {};\n'.format(ID_code)
    insertion_strings['idcode'               ] = output_strings['idcode']

    actions = {
                'INSERT' : insertion_strings
              }

    with open('rtl/digital/pre_jtag.svp', 'r') as fin:
        with open('rtl/digital/raw_jtag.svp','w') as fout:
            for line in fin:
                tokens = line.strip().split()
                if not tokens:
                    print(file=fout)
                    continue
                if tokens[0] == '$$':
                    print(actions[tokens[1]][tokens[2]], file=fout)
                else:
                    print(line, file=fout, end="")

    with open('rtl/digital/pre_tap.svp', 'r') as fin:
        with open('rtl/digital/tap.svp', 'w') as fout:
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


if __name__ == "__main__":
    main()
