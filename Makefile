
TOP_NAME := template
PACK_DIR := pack
INTF_DIR := intf
$(warning Template Name:        $(TOP_NAME))
$(warning Interface Directory:  $(INTF_DIR))
$(warning Constants Directory:  $(PACK_DIR))

all: justag genesis

justag: 
	python JusTAG.py  $(INTF_DIR)/* $(PACK_DIR)/*

genesis:
	Genesis2.pl -parse -generate -top template -input  rtl/digital/template.svp \
							    rtl/primitives/cfg_ifc.svp \
						        rtl/digital/template_ifc.svp \
						        rtl/primitives/flop.svp \
						        rtl/digital/tap.svp \
						        rtl/digital/cfg_and_dbg.svp\
						        rtl/primitives/reg_file.svp 

genesis_test:
	Genesis2.pl -parse -generate -top top -input  verif/top.svp \
								verif/clocker.svp \
								verif/JTAGDriver.svp \
								verif/test.svp \
								rtl/digital/template.svp \
							    rtl/primitives/cfg_ifc.svp \
						        rtl/digital/template_ifc.svp \
						        rtl/primitives/flop.svp \
						        rtl/digital/tap.svp \
						        rtl/digital/cfg_and_dbg.svp\
						        rtl/primitives/reg_file.svp 

genesis_clean:
	@echo ""
	@echo Cleanning previous runs of Genesis
	@echo ===================================
	@if test -f "genesis_clean.cmd"; then 	\
		 ./genesis_clean.cmd;		\
	fi


clean: genesis_clean
