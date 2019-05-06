package top;
use strict;
use vars qw($VERSION @ISA @EXPORT @EXPORT_OK);

use Exporter;
use FileHandle;
use Env; # Make environment variables available


use Genesis2::Manager 1.00;
use Genesis2::UniqueModule 1.00;

@ISA = qw(Exporter Genesis2::UniqueModule);
@EXPORT = qw();
@EXPORT_OK = qw();
$VERSION = '1.0';
sub get_SrcSuffix {Genesis2::UniqueModule::private_to_me(); return ".vp";};
sub get_OutfileSuffix {Genesis2::UniqueModule::private_to_me(); return ".v"};
############################### Module Starts Here ###########################


  sub to_verilog{ 
      # START PRE-GENERATED TO_VERILOG PREFIX CODE >>>
      my $self = shift;
      
      print STDERR "$self->{BaseModuleName}->to_verilog: Start user code\n" 
	  if $self->{Debug} & 8;
      # <<< END PRE-GENERATED TO_VERILOG PREFIX CODE
	$self->SUPER::to_verilog('/afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/verif/top.vp');
# START USER CODE FROM /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/verif/top.vp PARSED INTO PACKAGE >>>
# line 1 "/afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/verif/top.vp"
print { $self->{OutfileHandle} } '/*************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ** From Perforce:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' **';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ** $Id: //Smart_design/ChipGen/moduleTest/Primitives/top.vp#5 $';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ** $DateTime: 2010/03/25 11:23:45 $';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ** $Change: 8474 $';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ** $Author: shacham $';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' *************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '/* *****************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * File: top.vp';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Author: Ofer Shacham';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Description:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * simple top that instantiate the test and the dut';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' *';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Change bar:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * -----------';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Date          Author   Description';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Mar 19, 2010  shacham  initial version';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' *  ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ****************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '/*******************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Generation Control Definitions';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ******************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } "$self->{LineComment} ----- Start Include Of /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/src/analog/analog_defs.vph -----\n"; 
# START USER CODE FROM /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/src/analog/analog_defs.vph PARSED INTO PACKAGE >>>
# line 1 "/afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/src/analog/analog_defs.vph"
print { $self->{OutfileHandle} } '/* *****************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * File: analog_defs.vph';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Author: Ofer Shacham';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Description:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Definitions for analog signals for simulation and for synthesis';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * It contains definitions for $input_real, $output_real, $wire_real and ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * a macro $parameter_real($name, $value)';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * REQUIRED GENESIS PARAMETERS:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ----------------------------';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * * GenMode - Generation Mode. Can be \'Sim\', \'GateSim\', or \'Synth\'';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Change bar:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * -----------';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Date          Author   Description';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Mar 31, 2010  shacham  init version  --  ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * ****************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
 # declare the macros
 my ($mode, $input_real, $output_real, $wire_real);
 if(defined $self->get_parent()){
   $mode = $self->get_top_param('GenMode');
 }else{
  $mode = parameter(Name=>'GenMode', Val=>'Sim', List=>['Sim', 'GateSim', 'Synth'], 
		       Doc=>"Generation Mode. Can be 'Sim', 'GateSim', or 'Synth'");
 }

 # declare the macros
 my ($input_real, $output_real, $wire_real);

 if ($mode =~ m/^Synth$/i){
 	$input_real = 'input';
 	$output_real = 'output'; 
 	$wire_real = 'wire';
	sub parameter_real($$){ #let's be stricked and allow exactly two inputs
		my ($name, $value) = @_;
		return "parameter $name = 0";
	}
 } else{
 	$input_real = 'input real';
 	$output_real = 'output real'; 
 	$wire_real = 'real';
	sub parameter_real($$){ #let's be stricked and allow exactly two inputs
		my ($name, $value) = @_;
		return "parameter real $name = $value";
	}
 }
# <<< END USER CODE FROM /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/src/analog/analog_defs.vph PARSED INTO PACKAGE


print { $self->{OutfileHandle} } "$self->{LineComment} ----- End Include Of /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/src/analog/analog_defs.vph -----\n"; 
# line 30 "/afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/verif/top.vp"
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '/*******************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Simulation Control Definitions';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ******************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
 my $max_cyc      = parameter(Name=>'MaxCycles', Val=>100000, Min=>1, Step=>1, 
			         Doc=>'Max number of simulation cycles');
 my $design_name  = parameter(Name=>'DesignName', Val=>'template', 
				 Doc=>'This is a generic top, so what is the design name to use?');
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '/*******************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' * Module top:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ******************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } 'module '; print { $self->{OutfileHandle} } mname; print { $self->{OutfileHandle} } '();';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   logic Clk;';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   logic Reset;';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   /****************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * Instantiate clocks';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * *************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
     my $clocker_obj = generate('clocker', 'clocker', CLK_PERIOD=>10, RST_PERIOD=>20);
print { $self->{OutfileHandle} } '    '; print { $self->{OutfileHandle} } $clocker_obj->instantiate; print { $self->{OutfileHandle} } ' (.Clk(Clk), .Reset(Reset));';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   // timer:';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   initial begin';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '      repeat('; print { $self->{OutfileHandle} } $max_cyc; print { $self->{OutfileHandle} } ') @(posedge Clk);';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '      $display("\\n%0t\\tERROR: The '; print { $self->{OutfileHandle} } $max_cyc; print { $self->{OutfileHandle} } ' cycles marker has passed!",$time);';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '      $finish(2);';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   end';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   /****************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * Instantiate DUT interface and DUT';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * *************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
    # We use generate_base when there is for sure just one of X
    my $dut_obj = generate('phy_top', 'dut', DesignName => $design_name);
    my $dut_ifc_path = $dut_obj->get_param('IfcPtr');
    my $dut_ifc = clone($dut_ifc_path, 'dut_ifc');
print { $self->{OutfileHandle} } '   '; print { $self->{OutfileHandle} } $dut_ifc->instantiate; print { $self->{OutfileHandle} } ' (.Clk(Clk), .Reset(Reset));';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   '; print { $self->{OutfileHandle} } $dut_obj->instantiate; print { $self->{OutfileHandle} } ' (.ifc('; print { $self->{OutfileHandle} } $dut_ifc->iname(); print { $self->{OutfileHandle} } ') );';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '   /****************************************************************************';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * Instantiate Test';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '    * **************************************************************************/';print { $self->{OutfileHandle} } "\n"; 
     my $tst_obj = generate('test', 'tst');
print { $self->{OutfileHandle} } '    '; print { $self->{OutfileHandle} } $tst_obj->instantiate; print { $self->{OutfileHandle} } ' (.ifc('; print { $self->{OutfileHandle} } $dut_ifc->iname(); print { $self->{OutfileHandle} } '));';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } '      ';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } 'endmodule';print { $self->{OutfileHandle} } "\n"; 
print { $self->{OutfileHandle} } ' ';print { $self->{OutfileHandle} } "\n"; 
# <<< END USER CODE FROM /afs/ir.stanford.edu/users/j/i/jingpu/tmp/src-template/verif/top.vp PARSED INTO PACKAGE


      # START PRE-GENERATED TO_VERILOG SUFFIX CODE >>>
      print STDERR "$self->{BaseModuleName}->to_verilog: Done with user code\n" 
	  if $self->{Debug} & 8;

      #
      # clean up code comes here...
      #
      # <<< END PRE-GENERATED TO_VERILOG SUFFIX CODE
  }
