FULL_APP_PATH = ../../culpeo_tests/tools/scripts

plot_synthetic:
	python3 plot_synthetic_loads_redux.py

plot_synthetic_vsafes:
	python3 plot_synthetic_vsafes.py energy_vsafe.pkl unlucky_vsafe.pkl \
  lucky_vsafe.pkl catnap_vsafe.pkl \
  culpeo_vsafe.pkl dynamic_vsafe.pkl
#hardware_vsafe.pkl

plot_mezzos:
	python3 plot_mezzo_expts.py 

plot_9way:
	python3 plot_9way.py results/case_study/apds_30s_clean_charge-to-full.csv results/case_study/apds_30s_clean_catnap.csv results/case_study/apds_60s_clean_culpeo.csv results/case_study/culpeo_vsafe_charge_up.csv results/case_study/catnap_vsafe_charge_up.csv

plot_lost_events:
	cp $(FULL_APP_PATH)/*_sense_3s .
	cp $(FULL_APP_PATH)/*_ble_45s.pkl .
	cp $(FULL_APP_PATH)/combo*_mic.pkl .
	cp $(FULL_APP_PATH)/combo*_ble.pkl .
	python3 plot_periodicity.py *_sense_3s *_ble_45s.pkl combo*_mic.pkl \
  combo*_ble.pkl

plot_lost_events_sensitivity:
	cp $(FULL_APP_PATH)/*_sense_*s .
	cp $(FULL_APP_PATH)/*_ble_*s.pkl .
	python3 plot_period_sensitivity.py *_sense_*s *_ble_*s.pkl


