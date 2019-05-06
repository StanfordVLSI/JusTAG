`default_nettype none

interface acore_debug_intf import const_pack::*; (
);

	// inputs to analog core
	logic en_v2t;
	logic en_pi_arb;											// enable arbiters in PI delay chain
	logic en_ext_pi_ctl_cdr;  									// enable external PI control  
	logic [Npi-1:0] ext_pi_ctl_cdr; 							// external PI control 
	logic en_ext_pi_ctl_offset;									// enable external PI control offset 
	logic [Npi-1:0] ext_pi_ctl_offset [Nout-1:0];				// external PI offset control 
	logic en_ext_v2t_ctl;										// enable external V2T currnet control
	logic [Nv2t-1:0] ext_v2t_ctl [Nti-1:0];   					// external V2T current control
	logic en_ext_mismatch_ctl;									// enable external PI mismatch control
	logic [Nunit-1:0] ext_mismatch_ctl [Nout-1:0]; 				// external PI mismatch control
	logic en_ext_pfd_offset;									// enable external pfd offset 
	logic [Nadc-1:0] ext_pfd_offset [Nti-1:0]; 					// external PFD offset
	logic en_skew_cal;											// enable internal PI mismatch cal
	logic en_v2t_cal;											// enable internal skew cal
	logic en_mismatch_cal;										// enable internal V2T current cal
	logic en_pfd_cal;											// enable internal PFD offset cal
	logic [Nrange-1:0] Navg_adc; 								// number of samples for averaging adc output
	logic [Nrange-1:0] Nbin_adc; 								// bin size for measuring histogram
	logic [Nrange-1:0] DZ_hist_adc; 							// size of deadzone of PFD offset cal loop
	logic [2:0] DZ_v2t_cal; 									// size of deadzone of PFD offset cal loop
	logic [$clog2(Nout)-1:0] init [Nti-1:0]; 					// inital values for V2T_clockgen (div4)
	logic en_mdll;

	// outputs from analog core
	logic signed [Nadc-1:0] adcout[Nti-1:0];					// adc output
	logic signed [Nadc-1:0] adcout_avg[Nti-1:0];				// averaged adc output
	logic signed [Nadc+2**Nrange-1:0] adcout_sum[Nti-1:0];		// averaged adc output
	logic [2**Nrange-1:0] adcout_hist_center [Nti-1:0]; 		// histogram of center bin (for average adc output)
	logic [2**Nrange-1:0] adcout_hist_side [Nti-1:0]; 			// histogram of side bins (=(hist_left+hist_right)/2)
	logic signed [Nadc-1:0] adcout_pfd_offset [Nti-1:0];		// estimated value of pfd offset

	modport acore (
		// inputs to analog core
		input en_v2t,
		input en_pi_arb,							
		input en_ext_pi_ctl_cdr,					
		input ext_pi_ctl_cdr, 					
		input en_ext_pi_ctl_offset,		
		input ext_pi_ctl_offset,		
		input en_ext_v2t_ctl,			
		input ext_v2t_ctl,   			
		input en_ext_mismatch_ctl,		
		input ext_mismatch_ctl,	
		input en_ext_pfd_offset,			
		input ext_pfd_offset, 			
		input en_skew_cal,									
		input en_v2t_cal,								
		input en_mismatch_cal,								
		input en_pfd_cal,						
		input Navg_adc, 						
		input Nbin_adc,					
		input DZ_hist_adc, 					
		input DZ_v2t_cal,			
		input init,		
		input en_mdll,

		// outputs from analog core
		output adcout,			
		output adcout_avg,		
		output adcout_sum,
		output adcout_hist_center,
		output adcout_hist_side,	
		output adcout_pfd_offset
	);

	modport jtag (
		// outputs to analog core
		output en_v2t,
		output en_pi_arb,							
		output en_ext_pi_ctl_cdr,					
		output ext_pi_ctl_cdr, 					
		output en_ext_pi_ctl_offset,		
		output ext_pi_ctl_offset,		
		output en_ext_v2t_ctl,			
		output ext_v2t_ctl,   			
		output en_ext_mismatch_ctl,		
		output ext_mismatch_ctl,	
		output en_ext_pfd_offset,			
		output ext_pfd_offset, 			
		output en_skew_cal,									
		output en_v2t_cal,								
		output en_mismatch_cal,								
		output en_pfd_cal,						
		output Navg_adc, 						
		output Nbin_adc,					
		output DZ_hist_adc, 					
		output DZ_v2t_cal,			
		output init,		
		output en_mdll,

		// inputs from analog core
		input adcout,			
		input adcout_avg,		
		input adcout_sum,
		input adcout_hist_center,
		input adcout_hist_side,	
		input adcout_pfd_offset
	);

endinterface

`default_nettype wire