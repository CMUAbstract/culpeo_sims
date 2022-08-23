#include <msp430.h>
#include <stdint.h>
#include <stdio.h>

#include "uart.h"
#include "loadProfiling.h"

//#define VSAFE 2381
//#define TLOAD 296

/* Not true anymore
#if VSAFE > VHIGH
#error "Vsafe must be less than Vhigh"
#endif
*/
//#define RUN_ONBOARD


void clockSetup();
void chargingRoutine();
void dischargingRoutine();
void measure_min_adc();
void measure_vcap_adc();
void mcu_delayms( uint16_t ms );
void mcu_delayus( uint16_t us );
void activateLoad( size_t level, uint16_t ms);
void generateInterrupt( uint16_t, uint16_t );

uint16_t adc_reading = 0;	
uint16_t sampleCount = 0;


//#define DO_INTERRUPT_TEST
int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;               // Stop WDT
	  PM5CTL0 &= ~LOCKLPM5;                   // Disable the GPIO power-on default high-impedance mode
	  clockSetup();
    while(1) {
      P1OU
    
    // Switches as inputs
    P5DIR &= ~(BIT5 + BIT6);
    P5REN |= (BIT5 + BIT6);
    P5OUT |= (BIT5 + BIT6);
    P5IFG &= ~(BIT5 + BIT6);
    P5IE |=  (BIT5 + BIT6);                            // P5.6 interrupt enable
    P5IES |= (BIT5 + BIT6);                            // P5.6 interrupt on falling edge	

#ifdef DO_INTERRUPT_TEST
    while(1){
      // Wait for Button Press on P5.6
      __bis_SR_register(LPM3_bits+GIE);
    
      sampleCount = 0;
     
      generateInterrupt( 100, 10000 );  
    }

#else
	// Configure GPIO
    P1OUT |= BIT0;                         // Clear P1.0 output latch for a defined power-on state
    P1DIR |= BIT0;                          // Set P1.0 to output direction

    P2OUT &= ~(BIT5 + BIT6);
    P2DIR |= (BIT5 + BIT6);
	
	// Bit1 Control pin for Input Power -- connected to relay
  // Bit2 = start atomic block
  // Bit3 = stop atomic block
	P4OUT &= ~(BIT1 + BIT2 + BIT3);
	P4DIR |= (BIT1 + BIT2 + BIT3);
	
	// Control pin for Output Booster
	P7OUT &= ~BIT0;
	P7DIR |= BIT0;

	// Control pin for Load -- connected to relay
	P8OUT &= ~BIT1;
	P8DIR |= BIT1;
   
	// Output SMCLK on P3.4	
	/*
  P3SEL1 |= BIT4;
	P3SEL0 |= BIT4;
	P3DIR |= BIT4;
  */
  
  // P3.7-3 is connected to specific load currents
  // P3.3 will be used for discharging
  P3OUT &= ~(BIT3 + BIT4 + BIT5 + BIT6 + BIT7);
  P3DIR |= (BIT3 + BIT4 + BIT5 + BIT6 + BIT7);

	PM5CTL0 &= ~LOCKLPM5;                   // Disable the GPIO power-on default high-impedance mode
                                            // to activate previously configured port settings

	// Switches as inputs
	P5DIR &= ~(BIT5 + BIT6);
	P5REN |= (BIT5 + BIT6);
	P5OUT |= (BIT5 + BIT6);
	P5IFG &= ~(BIT5 + BIT6);
	P5IE |=  (BIT5 + BIT6);                            // P5.6 interrupt enable
	P5IES |= (BIT5 + BIT6);                            // P5.6 interrupt on falling edge	
	
	clockSetup();
	
	uart_init();
  int repeat_flag = 0;
		
  mcu_delayms(5000);
    while(1)
    {
		// Initially, all pins are set to LOW
		  P5IFG &= ~BIT6;
      if (repeat_flag < REPEAT_COUNT) {
        repeat_flag++;
        P5IFG |= BIT6;
      }
		// Wait for Button Press on P5.6
      __bis_SR_register(LPM3_bits+GIE);
      uart_write("Start!\r\n");	
      
      // Start Charging
      P4OUT |= BIT1;
      chargingRoutine();
      
      // Disable Charging and enable OP Booster
#ifndef CONT_CHARGING
      P4OUT &= ~BIT1;
#endif
		  P7OUT |= BIT0;

		mcu_delayms( 300 );
#ifdef TEST_EXTERNAL
    P2OUT |= BIT5; // Flip SIP
#endif

#ifdef MEAS_MIN
    P7OUT |= BIT1;
    P7DIR |= BIT1;
    mcu_delayms(300);
    P7OUT &= ~BIT1;
    mcu_delayms(100);
#endif
    // Discharge down to Vsafe
#ifdef USE_VSAFE
    dischargingRoutine(); // Only removed for now
#endif
    P2OUT |= BIT6; // Start bit
    // P2.5 is for enabling the sip switch, this lets the booster rebound
    // before we turn on power to anything external
#ifdef TEST_EXTERNAL
    //P2OUT |= BIT5;
    //mcu_delayms(2000);
    mcu_delayms(10);
    while(P6IN & BIT2); 
    P2OUT &= ~BIT5;
#endif
    // Tap out load profile here
    P4OUT |= BIT2;
    P4OUT &= ~BIT2;
    for (int i = 0; i < LOAD_SIZE; i++) {
      activateLoad(loads[i],times[i]); // turns on and then off a given load 
    }
#ifdef MEAS_MIN
    mcu_delayms(50);
    P4OUT |= BIT2;
    P4OUT &= ~BIT2;
    measure_min_adc(); 
    P4OUT |= BIT2;
    P4OUT &= ~BIT2;
#endif
    P4OUT |= BIT3;
    P4OUT &= ~BIT3;
#ifdef CONT_CHARGING
    chargingRoutine();
#endif
    P2OUT &= ~BIT6;
		mcu_delayms( 50 );
    // Put this signal down
//#ifdef MEAS_MIN
    // Added to get reasonable Vfinal calculation
    mcu_delayms(1000);
//#endif
		// Disable Load and OP Booster
		P7OUT &= ~BIT0; 
#ifdef USE_VSAFE
		mcu_delayms( 3000 ); // Delay so we always catch the start with the saleae
#endif
    uart_write("Done");
#ifdef TEST_EXTERNAL
    // Disable sip switch
    P2OUT &= ~BIT5;
#endif
	}
#endif
}

void __attribute__ ((interrupt(PORT5_VECTOR))) port_5 (void) {
    switch(__even_in_range(P5IV, P5IV__P5IFG7))
    {
		case P5IV__NONE:    break;          // Vector  0:  No interrupt
		case P5IV__P5IFG0:  break;          // Vector  2:  P7.0 interrupt flag
		case P5IV__P5IFG1:                  // Vector  4:  P7.1 interrupt flag
			break;
		case P5IV__P5IFG2:  		    // Vector  6:  P7.2 interrupt flag
			break;
		case P5IV__P5IFG3:  		    // Vector  8:  P7.3 interrupt flag
			break;
		case P5IV__P5IFG4:  	            // Vector  10:  P7.4 interrupt flag
			break;
		case P5IV__P5IFG5:  
			P5IFG &= ~BIT5;
			__bic_SR_register_on_exit(LPM3_bits | GIE);
			break;          // Vector  12:  P7.5 interrupt flag
		case P5IV__P5IFG6:  
			__bic_SR_register_on_exit(LPM3_bits | GIE);
			P5IFG &= ~BIT6;
			break;          // Vector  14:  P7.6 interrupt flag
		case P5IV__P5IFG7:  // Vector  16:  P7.7 interrupt flag
			break;
		default: break;
	}
}

void clockSetup(){
	
	CSCTL0_H = CSKEY_H; 							// Unlock CS registers
	CSCTL1 = DCOFSEL_0; 							// Initial Clock Frequency Reset 

	CSCTL2 = SELA__VLOCLK | SELS__DCOCLK | SELM__DCOCLK; // Set Clock Sources ACLK = VLO & SMCLK = MCLK = DCO
	
	// As per datasheet, div/4 for preventing out of spec operation. Refer to example codes.
	CSCTL3 = DIVA__4 | DIVS__4 | DIVM__4; 
	CSCTL1 = DCOFSEL_4 | DCORSEL; 	// Frequency = 16MHz

	__delay_cycles(60);

	// Set Dividers to 1
	CSCTL3 = DIVA__1 | DIVS__1 | DIVM__1;

	// Turn on VLO
	CSCTL4 &= ~VLOOFF;	
	CSCTL0_H = 0;
}

void chargingRoutine(){
	
	uart_write("ADC Reading: ");
	char str[100];
  adc_reading = 0x00;
	sprintf( str, "%d V\r\n", adc_reading );
	uart_write( str );
	
	//Configure P1.2 for ADC
	P1SEL1 |= BIT2;
	P1SEL0 |= BIT2;

	ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
#if VREF < 3
  while(REFCTL0 & REFGENBUSY);            // If ref generator busy, WAIT
  REFCTL0 |= REFVSEL_2 | REFON;           // Select internal ref = 2.5V
                                            // Internal Reference ON
#endif
	ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
	ADC12CTL1 = ADC12SHP;                   // Use sampling timer
	ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
#if VREF < 3
	ADC12MCTL0 = ADC12INCH_2 | ADC12VRSEL_1; // A2 ADC input select; VR=VeRef buff
#else
	ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vdd
#endif
	ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt
#if VREF < 3
  while(!(REFCTL0 & REFGENRDY)); // Settle
#endif
	__delay_cycles(10000);

	while( adc_reading < VHIGH ){
		// ======== Configure ADC ========
		// Take single sample when timer triggers and compare with threshold

		ADC12IFGR0 &= ~ADC12IFG0;
		ADC12CTL1 |= ADC12SHP | ADC12SHS_0 | ADC12CONSEQ_0 ;      // Use ADC12SC to trigger and single-channel
		ADC12CTL0 |= (ADC12ON + ADC12ENC + ADC12SC); 			// Trigger ADC conversion

		while(!(ADC12IFGR0 & ADC12IFG0)); // Wait till conversion over
		adc_reading = ADC12MEM0; 					// Read ADC value

		ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC

		 uart_write("ADC Reading:");
		 sprintf( str, "%d V\r\n", adc_reading );
		 uart_write( str );
		mcu_delayms(10);	

	}
	adc_reading = 0;
  uart_write("exit charge!");
}


void measure_min_adc() {
  //Configure P1.4 for ADC
  P1SEL1 |= BIT4;
  P1SEL0 |= BIT4;

  ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
#if MIN_VREF < 3
  while(REFCTL0 & REFGENBUSY);
  REFCTL0 |= REFVSEL_2 | REFON;           // Select internal ref = 2.5V
  P4OUT |= BIT2;
  P4OUT &= ~BIT2;
#endif
  ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
  ADC12CTL1 = ADC12SHP;                   // Use sampling timer
  ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
#if MIN_VREF < 3
  ADC12MCTL0 = ADC12VRSEL_1 | ADC12INCH_4; // A2 ADC input select; VR=Vref
#else
  ADC12MCTL0 = ADC12INCH_4; // A2 ADC input select; VR=Vdd
#endif
  ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt
#if MIN_VREF < 3
  while(!(REFCTL0 & REFGENRDY)); // Settle
#endif
  __delay_cycles(1000);
  adc_reading = 0xfff;
  uint32_t sum = 0;
	for(int i = 0; i < 32; i++) {
		// ======== Configure ADC ========
		// Take single sample when timer triggers and compare with threshold
		
		ADC12IFGR0 &= ~ADC12IFG0;
		ADC12CTL1 |= ADC12SHP | ADC12SHS_0 | ADC12CONSEQ_0 ;      // Use ADC12SC to trigger and single-channel
		ADC12CTL0 |= (ADC12ON + ADC12ENC + ADC12SC); 			// Trigger ADC conversion
		
		while(!(ADC12IFGR0 & ADC12IFG0)); 			// Wait till conversion over	
		adc_reading = ADC12MEM0; 					// Read ADC value
    sum += adc_reading;
		
		ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
	}
    ADC12CTL0 &= ~(ADC12ON);
	  char str[100];
#if MIN_VREF < 3
		 uart_write("Minimum Reading:");
		 sprintf( str, "%d V / 2.5V \r\n", sum >> 5);
#else
		 uart_write("Minimum Reading:");
		 sprintf( str, "%d V / 3.2V \r\n", sum >> 5);
#endif
		 uart_write( str );
}


void measure_vcap_adc() {
  //Configure P1.2 for ADC
  P1SEL1 |= BIT2;
  P1SEL0 |= BIT2;

  ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
#if VREF < 3
  while(!(REFCTL0 & REFGENRDY));
  REFCTL0 |= REFVSEL_2 | REFON;           // Select internal ref = 2.5V
#endif
  ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
  ADC12CTL1 = ADC12SHP;                   // Use sampling timer
  ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
#if VREF < 3
  ADC12MCTL0 = ADC12VRSEL_1 | ADC12INCH_2; // A2 ADC input select; VR=Vref
#else
  ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vdd
#endif
  //ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vref
  ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt
#if VREF < 3
  while(!(REFCTL0 & REFGENRDY)); // Settle
#endif
  __delay_cycles(1000);
  adc_reading = 0xfff;
		// ======== Configure ADC ========
		// Take single sample when timer triggers and compare with threshold
		
		ADC12IFGR0 &= ~ADC12IFG0;
		ADC12CTL1 |= ADC12SHP | ADC12SHS_0 | ADC12CONSEQ_0 ;      // Use ADC12SC to trigger and single-channel
		ADC12CTL0 |= (ADC12ON + ADC12ENC + ADC12SC); 			// Trigger ADC conversion
		
		while(!(ADC12IFGR0 & ADC12IFG0)); 			// Wait till conversion over	
		adc_reading = ADC12MEM0; 					// Read ADC value
		
		ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
    ADC12CTL0 &= ~(ADC12ON);
		
	  char str[100];
		 uart_write("ADC Reading:");
		 sprintf( str, "%d V\r\n", adc_reading );
		 uart_write( str );
}

// Alternates between discharging and reading adc pin
void dischargingRoutine(){
    P4OUT |= BIT3;
    P4DIR |= BIT3;
    P4OUT &= ~BIT3;
    P4OUT |= BIT3;
    P4DIR |= BIT3;
    P4OUT &= ~BIT3;
	uart_write("Discharge: ADC Reading: ");
	char str[100];
	sprintf( str, "%d V\r\n", adc_reading );
	uart_write( str );

  //Configure P1.2 for ADC
  P1SEL1 |= BIT2;
  P1SEL0 |= BIT2;

  ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
#if VREF < 3
  while(!(REFCTL0 & REFGENRDY));
  REFCTL0 |= REFVSEL_2 | REFON;           // Select internal ref = 2.5V
#endif
  ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
  ADC12CTL1 = ADC12SHP;                   // Use sampling timer
  ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
#if VREF < 3
  ADC12MCTL0 = ADC12VRSEL_1 | ADC12INCH_2; // A2 ADC input select; VR=Vref
#else
  ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vdd
#endif
  //ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vref
  ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt
#if VREF < 3
  while(!(REFCTL0 & REFGENRDY)); // Settle
#endif


  __delay_cycles(10000);
  adc_reading = 0xfff;
	while( adc_reading > VSAFE ){
    P4OUT |= BIT3;
    P4DIR |= BIT3;
    P4OUT &= ~BIT3;
		// ======== Configure ADC ========
		// Take single sample when timer triggers and compare with threshold
		
		ADC12IFGR0 &= ~ADC12IFG0;
		ADC12CTL1 |= ADC12SHP | ADC12SHS_0 | ADC12CONSEQ_0 ;      // Use ADC12SC to trigger and single-channel
		ADC12CTL0 |= (ADC12ON + ADC12ENC + ADC12SC); 			// Trigger ADC conversion
		
		while(!(ADC12IFGR0 & ADC12IFG0)); 			// Wait till conversion over	
		adc_reading = ADC12MEM0; 					// Read ADC value
		
		ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
		
		 uart_write("ADC Reading:");
		 sprintf( str, "%d V\r\n", adc_reading );
		 uart_write( str );
    // Now drain:
    #ifndef BUDDY_MCU
    P3OUT |= BIT3;
    P3DIR |= BIT3;
		mcu_delayms(10);	
    P3OUT &= ~BIT3;
    #else
    // Just let the active mcu drain us
		mcu_delayms(10);	
    #endif
		mcu_delayms(100);	

	}
  ADC12CTL0 &= ~(ADC12ON);
	//REFCTL0 &= ~REFON;
  uart_write("Exit discharge");
	adc_reading = 0;
}

// Generates an interrupt every period ms,
// for a total of numInterrupts interrupts.
void generateInterrupt( uint16_t period, uint16_t numInterrupts ){
	P3DIR |= BIT1;
	while(numInterrupts--){

		P3OUT |= BIT1;

		mcu_delayms( 1 );
		
		P3OUT &= ~BIT1;
		
    mcu_delayms( period - 1 );
	}
}

// These routines could be implemented with timers if needed, 
// but work this way for now

void mcu_delayms(uint16_t ms) {
	// Can count to a max of 65s
	while (ms) {
		__delay_cycles(16000);
		ms--;
  }
}

void mcu_delayus(uint16_t us) {
	// Can count to a max of 65ms
	while (us) {
		__delay_cycles(16); //for 8MHz
		us--;
  }
}

void activateLoad(size_t load, uint16_t time) {
  P3OUT |= pinMap[load];
  mcu_delayms(time);
  P3OUT &= ~pinMap[load]; 
}

