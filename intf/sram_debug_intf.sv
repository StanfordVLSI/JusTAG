`default_nettype none

interface sram_debug_intf;

	import const_pack::*;

    logic [N_mem_addr-1:0] in_addr;
    logic in_load_addr;
    logic in_load_max;
    logic read;
    logic write;

    logic [Nti*Nadc-1:0] out_data;
    logic [N_mem_addr-1:0] addr;
    logic counter_overflow;
    logic done;

    modport sram (
	    input in_addr,
	    input in_load_addr,
	    input in_load_max,
	    input read,
	    input write,
	    output out_data,
	    output addr,
	    output counter_overflow,
	    output done	
    );

    modport jtag (
	    output in_addr,
	    output in_load_addr,
	    output in_load_max,
	    output read,
	    output write,
	    input out_data,
	    input addr,
	    input counter_overflow,
	    input done	
    );

endinterface

`default_nettype wire