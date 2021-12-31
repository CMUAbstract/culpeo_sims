// Should be auto-generated by python script based on cap bank esr at different
// frequencies and booster
// efficiency curves
#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0
// Min voltage 1.8
#error "vsafes not calculated"
#elif CONFIG == 1
// Min voltage 1.6
#include "datasheet_esr_culpeo_1.6_0.045"

#define VSAFE_ID_APDS 2505
#define VSAFE_ID_BLE 2289
#define VSAFE_ID_ML 2532

#else

#error "No vsafes defined for config"

#endif
#endif

