FULL_APP_PATH = ../../culpeo_tests/tools/scripts


plot_synthetic:
	python3 plot_synthetic_loads_redux.py

# Figure 11 generation
plot_synthetic_vsafes:
	python3 plot_synthetic_vsafes.py catnap_vsafe.pkl \
  culpeo_vsafe.pkl dynamic_vsafe.pkl \
  hardware_vsafe.pkl

# Figure 12 generation
plot_mezzos:
	python3 plot_mezzo_expts.py

plot_9way:
	python3 plot_9way.py results/case_study/apds_30s_clean_charge-to-full.csv results/case_study/apds_30s_clean_catnap.csv results/case_study/apds_60s_clean_culpeo.csv results/case_study/culpeo_vsafe_charge_up.csv results/case_study/catnap_vsafe_charge_up.csv

# Figure 13
plot_lost_events:
	python3 plot_periodicity.py *_sense_3s *_ble_45s.pkl combo*_mic.pkl \
  combo*_ble.pkl

# Figure 14-- I really thought this one used to look better, not sure what
# happened
plot_lost_events_sensitivity:
	python3 plot_period_sensitivity.py *_sense_*s *_ble_*s.pkl

# Figure 6 generation
plot_bg:
	python3 plot_vsafes_bg.py energy_vsafe.pkl\
  unlucky_vsafe.pkl catnap_vsafe.pkl \
