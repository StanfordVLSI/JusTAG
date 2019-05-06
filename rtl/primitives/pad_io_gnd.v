module pad_io_gnd();

IOVSS iovss_padlocal(
		     .VSS(GND) , 
		     .VDDIO(VDDIO) ,
		     .VDD(VDD) ,
		     .VSSIO(GNDIO) ) ;
   
   
endmodule // pad_io_gnd
