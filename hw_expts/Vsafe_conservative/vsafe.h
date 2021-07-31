#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0

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

#elif CONFIG == 1

#define VSAFE_ID10 2207
#define VSAFE_ID11 2319
#define VSAFE_ID12 2494
#define VSAFE_ID1 2950
#define VSAFE_ID3 2503
#define VSAFE_ID4 3036
#define VSAFE_ID6 2244
#define VSAFE_ID7 2402
#define VSAFE_ID8 2768
#define VSAFE_ID9 3675

#else

#error "Config not defined"

#endif // Vsafe
