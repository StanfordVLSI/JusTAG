module pad_io_vdd();

IOVDD iovdd_padlocal(
		     .VSS(GND) , 
		     .VDDIO(VDDIO) ,
		     .VDD(VDD) ,
		     .VSSIO(GNDIO) ) ;
   
   
endmodule // pad_io_vdd
