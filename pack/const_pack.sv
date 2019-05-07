`ifndef __CONST_PACK_SV__
`define __CONST_PACK_SV__

package const_pack;

	localparam integer Nti = 16;
	localparam integer Nadc = 8;		// ADC bits
	localparam integer Npi = 9;    		// PI control bits / UI
	localparam integer Nunit = 32;		// number of delay units in each delay chain
	localparam integer Nout = 4;		// number of PI output clock phases
	localparam integer Nv2t = 4;		// number of PI output clock phases
	localparam integer Nrange = 4;
	localparam integer N_mem_addr = 10; // number of bits in SRAM address
endpackage

`endif // `ifndef __CONST_PACK_SV__
