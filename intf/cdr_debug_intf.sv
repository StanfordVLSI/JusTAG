`default_nettype none

interface cdr_debug_intf;

	import const_pack::*;

	logic sel_ext_pi;
	logic [Npi-1:0] pi_ctl_ext;
	logic sel_ext_pd_offset;
	logic signed [Nadc-1:0] pd_offset_ext;

	modport cdr (
		input sel_ext_pi,
		input pi_ctl_ext,
		input sel_ext_pd_offset,
		input pd_offset_ext
	);

	modport jtag (
		output sel_ext_pi,
		output pi_ctl_ext,
		output sel_ext_pd_offset,
		output pd_offset_ext
	);

endinterface

`default_nettype wire