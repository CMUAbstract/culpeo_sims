#include <msp430.h>
#include <stdio.h>

#include "uart.h"

void uart_init() {
	P2SEL1  |=  BIT0 + BIT1;            // P2.0 UCA0TXD output
	P2SEL0 &=  ~(BIT0 + BIT1);            // P2.1 UCA0RXD input
	
	UCA0CTLW0 = UCSWRST;
	UCA0CTLW0 |=  UCSSEL__SMCLK;  // USCI Clock = SMCLK, USCI_A0 disabled

	UCA0BRW   =  8;                // From datasheet table selects baudrate = 115200bps, @clk = SMCLK 8MHz

	UCA0MCTLW  |=  UCOS16 | 0x00A0 | 0xF700;             // Modulation value = 1 from datasheet

	UCA0CTLW0 &= ~UCSWRST;             // Clear UCSWRST to enable USCI_A0

}

void uart_write(char* str) {
  for(int i = 0; str[i] != '\0'; i++) {
    while (!(UCA0IFG & UCTXIFG));    // TX buffer ready?
    UCA0TXBUF = str[i];
  }
}

void uart_writen(char* data, int n) {
  while(n--) {
    while (!(UCA0IFG & UCTXIFG));
    UCA0TXBUF = *data++;
  }
}

void uart_writec(char data) {
  while (!(UCA0IFG & UCTXIFG));
  UCA0TXBUF = data;
}

void uart_printhex8(uint8_t n) {

	char str[100];

	sprintf( str, "0x%d ", n, n);

  uart_write(str);
}

void uart_printhex32(uint32_t n) {
	char str[100];

	sprintf( str, "%d(%x)\r\n", n, n);

  uart_write(str);
}
