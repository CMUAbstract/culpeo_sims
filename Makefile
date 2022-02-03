# Makefile for calculating Vsafe values

BASELINES_PATH = ../culpeo_measurements/hw_expts/e_load_tests/expt_baselines

MEZZOS_PATH = expt_baseline_traces

RESULTS_PATH = results_disk/seiko_expts/

EXPTS_PATH = hw_expts

synthetic_vsafes:
	python3 esrs.py $(BASELINES_PATH)/expt_*
	mv grey_hat_culpeo_1.6_0.045 $(EXPTS_PATH)/Vsafe_conservative/
	mv vsafe_1.6_0.045 $(EXPTS_PATH)/Vsafe_culpeo/
	mv catnap_1.6_0.045 $(EXPTS_PATH)/Vsafe_catnap/
	mv datasheet_esr_culpeo_1.6_0.045 $(EXPTS_PATH)/Vsafe_datasheet/

mezzo_vsafes:
	rm -f *_multi_vsafes_1.6.pkl
	python3 esr_estimate.py $(MEZZOS_PATH)/ble_1kb_new_gain16.csv
	python3 esr_estimate.py $(MEZZOS_PATH)/ml_g47r3_24MHz_6seiko_caps_gain8.csv
	python3 esr_estimate.py $(MEZZOS_PATH)/apds_cont_pwrd_trace_gain8.csv \
	$(MEZZOS_PATH)/apds_6seiko_noI.csv
	python3 esr_estimate.py $(MEZZOS_PATH)/fast_g47r3_64MHz_7seiko_caps_gain16.csv \
	$(MEZZOS_PATH)/fast_ml_6seiko_caps_noI.csv
	mv conservative_*_1.6 $(EXPTS_PATH)/Vsafe_conservative/
	mv culpeo_*_1.6 $(EXPTS_PATH)/Vsafe_culpeo/
	mv catnap_*_1.6 $(EXPTS_PATH)/Vsafe_catnap/
	mv datasheet_*_1.6 $(EXPTS_PATH)/Vsafe_datasheet/
	mv *_multi_vsafes_1.6.pkl plotting_scripts/


process_synthetic:
	python3 expt_process.py $(RESULTS_PATH)/microbenchmarks_test_dir/catnap/EXPT_*
	mv expt_process_summary.pkl catnap_summary_volt_match.pkl
	python3 expt_process.py $(RESULTS_PATH)/microbenchmarks_volt_match_2ms/culpeo/EXPT_*
	mv expt_process_summary.pkl culpeo_summary_volt_match.pkl
	python3 expt_process.py $(RESULTS_PATH)/microbenchmarks_test_dir/conservative/EXPT_*
	mv expt_process_summary.pkl conservative_summary_volt_match.pkl
	python3 expt_process.py $(RESULTS_PATH)/microbenchmarks_volt_match_2ms/datasheet/EXPT_*
	mv expt_process_summary.pkl datasheet_summary_volt_match.pkl

