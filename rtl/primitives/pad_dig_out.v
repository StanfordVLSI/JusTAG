// This is a wrapper for a digital pad module

module pad_dig_out(
	       input fromchip,
	       output toboard
	       );

   
   D2I1025 D2I1025_pad_local(toboard,GND,1'b1,VDDIO,VDD,GNDIO,fromchip);

   
endmodule // pad_dig_out

