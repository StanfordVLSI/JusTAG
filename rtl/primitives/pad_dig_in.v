
// This is a wrapper for a digital pad module

module pad_dig_in(
	       input fromboard,
	       output tochip
	       );

   I1025 I1025_pad_local(fromboard,GND,VDDIO,VDD,1'b1,GNDIO,tochip);
   
endmodule // pad_dig_in

