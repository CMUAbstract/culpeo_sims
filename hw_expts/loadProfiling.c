#include <msp430.h>
#include <stdint.h>
#include <stdio.h>

#include "loadProfiling.h"
#include "uart.h"

//#define VSAFE 2381
//#define TLOAD 296

/* Not true anymore
#if VSAFE > VHIGH
#error "Vsafe must be less than Vhigh"
#endif
*/

void clockSetup();
void chargingRoutine();
void dischargingRoutine();
void mcu_delayms( uint16_t ms );
void mcu_delayus( uint16_t us );
void activateLoad( size_t level, uint16_t ms);


uint16_t adc_reading = 0;	

int main(void)
{
    WDTCTL = WDTPW | WDTHOLD;               // Stop WDT

    
	// Configure GPIO
    P1OUT |= BIT0;                         // Clear P1.0 output latch for a defined power-on state
    P1DIR |= BIT0;                          // Set P1.0 to output direction

    P2OUT &= ~BIT6;
    P2DIR |= BIT6;
	
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
      P4OUT &= ~BIT1;
		  P7OUT |= BIT0;

		mcu_delayms( 300 );
    // Discharge down to Vsafe
#ifdef USE_VSAFE
    dischargingRoutine(); // Only removed for now
#endif
    P2OUT |= BIT6;
    P2OUT &= ~BIT6;
    // Tap out load profile here
    P4OUT |= BIT2;
    P4OUT &= ~BIT2;
    for (int i = 0; i < LOAD_SIZE; i++) {
      activateLoad(loads[i],times[i]); // turns on and then off a given load 
    }
    P4OUT |= BIT3;
    P4OUT &= ~BIT3;
		mcu_delayms( 500 );
		// Disable Load and OP Booster
		P7OUT &= ~BIT0; 
		mcu_delayms( 3000 ); // Delay so we always catch the start with the saleae
    uart_write("Done");
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
	ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
	ADC12MCTL0 = ADC12INCH_2;              // A2 ADC input select; Vref=AVCC
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
  ADC12CTL2 = ADC12RES_2;                // 12-bit conversion results
  //ADC12MCTL0 = ADC12VRSEL_1 | ADC12INCH_2; // A2 ADC input select; VR=Vref
  ADC12MCTL0 = ADC12INCH_2; // A2 ADC input select; VR=Vref
  ADC12IER0 &= ~ADC12IE0;                  // Disable ADC conv complete interrupt
	
  //while( REFCTL0 & REFGENBUSY );

	//REFCTL0 = REFVSEL_3 | REFON;            //Set reference voltage(VR+) to 1.2

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
    P3OUT |= BIT3;
    P3DIR |= BIT3;
		mcu_delayms(10);	
    P3OUT &= ~BIT3;
		mcu_delayms(100);	

	}
  ADC12CTL0 &= ~(ADC12ON);
	//REFCTL0 &= ~REFON;
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
