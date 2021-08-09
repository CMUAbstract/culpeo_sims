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
#define VSAFE_ID13 2410
#define VSAFE_ID14 2516
#define VSAFE_ID15 2227
#define VSAFE_ID16 2373
#define VSAFE_ID17 2586
#define VSAFE_ID18 2182
#define VSAFE_ID19 2288
#define VSAFE_ID20 2486
#define VSAFE_ID21 2730
#define VSAFE_ID22 2278
#define VSAFE_ID23 2465
#define VSAFE_ID24 2730
#define VSAFE_ID25 2398
#define VSAFE_ID26 2518
#define VSAFE_ID27 2212
#define VSAFE_ID28 2360
#define VSAFE_ID29 2532
#define VSAFE_ID30 2171
#define VSAFE_ID31 2275
#define VSAFE_ID32 2445
#define VSAFE_ID33 2727
#define VSAFE_ID34 2266
#define VSAFE_ID35 2453
#define VSAFE_ID36 2723
#define VSAFE_ID10 2267
#define VSAFE_ID11 2482
#define VSAFE_ID12 2805
#define VSAFE_ID1 2625
#define VSAFE_ID1 2409
#define VSAFE_ID3 2222
#define VSAFE_ID4 2362
#define VSAFE_ID6 2178
#define VSAFE_ID7 2287
#define VSAFE_ID8 2474
#define VSAFE_ID9 2856

#define VSAFE_ID_APDS 3220
#define VSAFE_ID_BLE 2501
#define VSAFE_ID_ML 2906

#elif CONFIG == 2

#error "vsafes not calculated"

#else

#error "No vsafes defined for config"

#endif
#endif

