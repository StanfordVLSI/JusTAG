
// This is a wrapper for an analog pad module

module pad_ana_in(
	       input fromboard,
	       output tochip
	       );

   A1825 A1825_pad_local(toboard,VDDIO,VDD,GNDIO,GND,fromchip);
   
endmodule // pad_dig_in

