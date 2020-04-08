
TOP_NAME := template
PACK_DIR := pack
INTF_DIR := intf
$(warning Template Name:        $(TOP_NAME))
$(warning Interface Directory:  $(INTF_DIR))
$(warning Constants Directory:  $(PACK_DIR))

default: justag genesis

all: justag genesis genesis_test

justag: 
	python JusTAG.py  $(INTF_DIR)/* $(PACK_DIR)/*

genesis:
	Genesis2.pl -parse -generate -top template -input  justag/rtl/digital/template.svp \
							    justag/rtl/primitives/cfg_ifc.svp \
						        justag/rtl/digital/template_ifc.svp \
						        justag/rtl/primitives/flop.svp \
						        justag/rtl/digital/tap.svp \
						        justag/rtl/digital/cfg_and_dbg.svp\
						        justag/rtl/primitives/reg_file.svp 

genesis_test: 
	Genesis2.pl -parse -generate -top top -input justag/verif/test.svp \
								justag/verif/top.svp \
								justag/verif/clocker.svp \
								justag/verif/JTAGDriver.svp \
								justag/verif/test.svp \
								justag/rtl/digital/template.svp \
							    justag/rtl/primitives/cfg_ifc.svp \
						        justag/rtl/digital/template_ifc.svp \
						        justag/rtl/primitives/flop.svp \
						        justag/rtl/digital/tap.svp \
						        justag/rtl/digital/cfg_and_dbg.svp\
						        justag/rtl/primitives/reg_file.svp 

genesis_clean:
	@echo ""
	@echo Cleanning previous runs of Genesis
	@echo ===================================
	@if test -f "genesis_clean.cmd"; then 	\
		 ./genesis_clean.cmd;		\
	fi


clean: genesis_clean
