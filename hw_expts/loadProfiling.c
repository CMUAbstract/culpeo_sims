#include <msp430.h>
#include <stdint.h>
#include <stdio.h>

#include "loadProfiling.h"
#include "uart.h"

//#define VSAFE 2381
//#define TLOAD 296


#if VSAFE > VHIGH
#error "Vsafe must be less than Vhigh"
#endif

void clockSetup();
void chargingRoutine();
void dischargingRoutine();
void mcu_delayms( uint16_t ms );
void mcu_delayus( uint16_t us );
void activateLoad( size_t level, uint16_t ms);


uint16_t adc_reading = 0;	

// Map indicating which mosfets are connect to which GPIO pins
// Note, we assume these are all coming off of port 3
uint16_t pinMap[NUM_SIGS] = {BIT3, BIT4, BIT5, BIT6};
// Connected to res:        1000   470,  220,   47  Ohm
// Actual current:                5.4  11.5    48   mA
int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;               // Stop WDT

    
	// Configure GPIO
    P1OUT |= BIT0;                         // Clear P1.0 output latch for a defined power-on state
    P1DIR |= BIT0;                          // Set P1.0 to output direction
	
	// Control pin for Input Power -- connected to relay
	P4OUT &= ~BIT1;
	P4DIR |= BIT1;
	
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
  
  // P3.7 is connected to discharging circuit
  // P3.6-3 is connected to specific load currents
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
    while(1)
    {
		// Initially, all pins are set to LOW
		P5IFG &= ~BIT6;
		
		// Wait for Button Press on P5.6
    //while(1) {
      __bis_SR_register(LPM3_bits+GIE);
      uart_write("Start!\r\n");	
      
      // Start Charging
      P4OUT |= BIT1;
      chargingRoutine();
      
      // Disable Charging and enable OP Booster
      P4OUT &= ~BIT1;
    //}
		P7OUT |= BIT0;

		mcu_delayms( 100 );
    //while(1);
    // Discharge down to Vsafe
    // TODO need to figure out if this discharges
    dischargingRoutine();
		// Enable Load and run for tLOAD	
		//P8OUT |= BIT1; // --> don't need anymore

    // Tap out load profile here
    for (int i = 0; i < LOAD_SIZE; i++) {
      activateLoad(loads[i],times[i]); // turns on and then off a given load 
    }
    //mcu_delayms(0xffff);
    //mcu_delayms(0xffff);
		// Disable Load and OP Booster
		P7OUT &= ~BIT0;
		//P8OUT &= ~BIT1;
    uart_write("Done tload!");
	}
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
	sprintf( str, "%d V\r\n", adc_reading );
	uart_write( str );
	
	//Configure P1.2 for ADC
	P1SEL1 |= BIT2;
	P1SEL0 |= BIT2;

	ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
	ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
	ADC12CTL1 = ADC12SHP;                   // Use sampling timer
	ADC12CTL2 |= ADC12RES_2;                // 12-bit conversion results
	ADC12MCTL0 |= ADC12INCH_2;              // A2 ADC input select; Vref=AVCC
	ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt

	__delay_cycles(10000);

	while( adc_reading < VHIGH ){
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
		mcu_delayms(10);	

	}
	adc_reading = 0;
  uart_write("exit charge!");
}

// Alternates between discharging and reading adc pin
void dischargingRoutine(){
	uart_write("Discharge: ADC Reading: ");
	char str[100];
	sprintf( str, "%d V\r\n", adc_reading );
	uart_write( str );

  //Configure P1.2 for ADC
  P1SEL1 |= BIT2;
  P1SEL0 |= BIT2;

  ADC12CTL0 &= ~ADC12ENC; 					// Disable ADC
  ADC12CTL0 = ADC12SHT0_2 | ADC12ON;      // Sampling time, S&H=16, ADC12 on
  ADC12CTL1 = ADC12SHP;                   // Use sampling timer
  ADC12CTL2 |= ADC12RES_2;                // 12-bit conversion results
  ADC12MCTL0 |= ADC12INCH_2;              // A2 ADC input select; Vref=AVCC
  ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt

  __delay_cycles(10000);
  adc_reading = 0xfff;
	while( adc_reading > VSAFE ){
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
    P3OUT |= BIT7;
    P3DIR |= BIT7;
		mcu_delayms(10);	
    P3OUT &= ~BIT7;

	}
  uart_write("Exit discharge");
	adc_reading = 0;
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

