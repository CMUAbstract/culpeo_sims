# Makefile for calculating Vsafe values

BASELINES_PATH = ../culpeo_measurements/hw_expts/e_load_tests/expt_baselines

MEZZOS_PATH = expt_baseline_traces


synthetic_vsafes:
	python3 esrs.py $(BASELINES_PATH)/expt_*
	mv grey_hat_culpeo_1.6_0.045 hw_expts/Vsafe_conservative/
	mv vsafe_1.6_0.045 hw_expts/Vsafe_culpeo/
	mv catnap_1.6_0.045 hw_expts/Vsafe_catnap/
	mv datasheet_esr_culpeo_1.6_0.045 hw_expts/Vsafe_datasheet/

mezzo_vsafes:
	python3 esr_estimate.py $(MEZZOS_PATH)/ble_1kB_6seiko_caps_gain16.csv
	python3 esr_estimate.py $(MEZZOS_PATH)/ml_g47r3_24MHz_6seiko_caps_gain8.csv
	python3 esr_estimate.py $(MEZZOS_PATH)/apds_cont_pwrd_trace_gain8.csv \
	$(MEZZOS_PATH)/apds_6seiko_noI.csv
