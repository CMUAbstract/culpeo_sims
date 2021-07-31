#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0

#define VSAFE_ID10 2363
#define VSAFE_ID11 2364
#define VSAFE_ID12 2365
#define VSAFE_ID1 2735
#define VSAFE_ID3 2437
#define VSAFE_ID4 2505
#define VSAFE_ID6 2370
#define VSAFE_ID7 2376
#define VSAFE_ID8 2388
#define VSAFE_ID9 2406

#elif CONFIG == 1

#define VSAFE_ID10 2108
#define VSAFE_ID11 2110
#define VSAFE_ID12 2111
#define VSAFE_ID1 2500
#define VSAFE_ID3 2187
#define VSAFE_ID4 2261
#define VSAFE_ID6 2117
#define VSAFE_ID7 2123
#define VSAFE_ID8 2136
#define VSAFE_ID9 2155

#else

#error "Config not defined"
#endif //CONFIG

#endif // Vsafe
