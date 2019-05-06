// This is a wrapper for an analog pad module

module pad_ana_out(
	       input fromchip,
	       output toboard
	       );

   A1825 A1825_pad_local(toboard,VDDIO,VDD,GNDIO,GND,fromchip);

endmodule // pad_dig_out

