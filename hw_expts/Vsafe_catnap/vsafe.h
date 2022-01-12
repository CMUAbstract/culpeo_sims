#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0

/*#define VSAFE_ID10 2321
#define VSAFE_ID11 2322
#define VSAFE_ID12 2322
#define VSAFE_ID1 2543
#define VSAFE_ID3 2355
#define VSAFE_ID4 2405
#define VSAFE_ID6 2323
#define VSAFE_ID7 2327
#define VSAFE_ID8 2337
#define VSAFE_ID9 2356
*/
#define VSAFE_ID13 2482
#define VSAFE_ID14 3382
#define VSAFE_ID15 2326
#define VSAFE_ID16 2394
#define VSAFE_ID17 3217
#define VSAFE_ID18 2303
#define VSAFE_ID19 2329
#define VSAFE_ID20 2334
#define VSAFE_ID21 2354
#define VSAFE_ID22 2323
#define VSAFE_ID23 2324
#define VSAFE_ID24 2330
#define VSAFE_ID25 2483
#define VSAFE_ID26 3429
#define VSAFE_ID27 2326
#define VSAFE_ID28 2392
#define VSAFE_ID29 3286
#define VSAFE_ID30 2303
#define VSAFE_ID31 2325
#define VSAFE_ID32 2334
#define VSAFE_ID33 2354
#define VSAFE_ID34 2322
#define VSAFE_ID35 2329
#define VSAFE_ID36 2329
#define VSAFE_ID10 2321
#define VSAFE_ID11 2322
#define VSAFE_ID12 2322
#define VSAFE_ID1 2818
#define VSAFE_ID1 2543
#define VSAFE_ID3 2355
#define VSAFE_ID4 2405
#define VSAFE_ID6 2323
#define VSAFE_ID7 2327
#define VSAFE_ID8 2337
#define VSAFE_ID9 2356

#elif CONFIG == 1

#include "catnap_1.6_0.045"

#include "catnap_APDS_1.6"
#include "catnap_BLE_1.6"
#include "catnap_ML_1.6"

#else

#error "Config not defined"

#endif //CONFIG
#endif // Vsafe
