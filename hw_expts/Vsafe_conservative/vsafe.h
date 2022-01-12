#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0
/*
#define VSAFE_ID10 2462
#define VSAFE_ID11 2573
#define VSAFE_ID12 2749
#define VSAFE_ID1 3192
#define VSAFE_ID3 2755
#define VSAFE_ID4 3287
#define VSAFE_ID6 2498
#define VSAFE_ID7 2656
#define VSAFE_ID8 3022
#define VSAFE_ID9 3931
*/
#define VSAFE_ID13 3181
#define VSAFE_ID14 17972
#define VSAFE_ID15 2788
#define VSAFE_ID16 3325
#define VSAFE_ID17 20439
#define VSAFE_ID18 2537
#define VSAFE_ID19 2687
#define VSAFE_ID20 3020
#define VSAFE_ID21 3807
#define VSAFE_ID22 2499
#define VSAFE_ID23 2598
#define VSAFE_ID24 2749
#define VSAFE_ID25 3177
#define VSAFE_ID26 17792
#define VSAFE_ID27 2786
#define VSAFE_ID28 3306
#define VSAFE_ID29 21148
#define VSAFE_ID30 2535
#define VSAFE_ID31 2683
#define VSAFE_ID32 3007
#define VSAFE_ID33 3718
#define VSAFE_ID34 2498
#define VSAFE_ID35 2594
#define VSAFE_ID36 2741
#define VSAFE_ID10 2462
#define VSAFE_ID11 2573
#define VSAFE_ID12 2749
#define VSAFE_ID1 3374
#define VSAFE_ID1 3192
#define VSAFE_ID3 2755
#define VSAFE_ID4 3287
#define VSAFE_ID6 2498
#define VSAFE_ID7 2656
#define VSAFE_ID8 3022
#define VSAFE_ID9 3931

#elif CONFIG == 1

#include "grey_hat_culpeo_1.6_0.045"

#include "conservative_APDS_1.6"
#include "conservative_BLE_1.6"
#include "conservative_ML_1.6"

#else

#error "Config not defined"
#endif //CONFIG

#endif // Vsafe
