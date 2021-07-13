INPUTS := loadProfiling.c uart.c
TARGET := main

EXPT_ID := 2

ifeq ($(EXPT_ID), 1)
VSAFE := 2381
TLOAD := 296
else ifeq ($(EXPT_ID), 2)
VSAFE := 2420
TLOAD := 152
else ifeq ($(EXPT_ID), 3)
VSAFE := 2539
TLOAD := 61
else ifeq ($(EXPT_ID), 4)
VSAFE := 2737
TLOAD := 30
else ifeq ($(EXPT_ID), 5)
VSAFE := 3129
TLOAD := 15
endif

MSPGCC_PATH := $(HOME)/opt/ti/mspgcc/bin
MSP430_INC_PATH := $(HOME)/opt/ti/mspgcc/msp430-elf/include/
MSP430_LD_PATH := $(HOME)/opt/ti/mspgcc/msp430-elf/lib/

CC := $(MSPGCC_PATH)/msp430-elf-gcc
AR := $(MSPGCC_PATH)/msp430-elf-ar
OBJCP := $(MSPGCC_PATH)/msp430-elf-objcopy

DEVICE := MSP430FR5994

ifeq ($(DEVICE), MSP430FR5994)
MCU := msp430fr5994
endif

CFLAGS := -D __$(DEVICE)__ -DVSAFE=$(VSAFE) -DTLOAD=$(TLOAD) -mmcu=$(MCU) -O2 -static
IFLAGS := -I $(MSP430_INC_PATH)
LFLAGS := -T $(MCU).ld -L $(MSP430_LD_PATH) -mmcu=$(MCU)

COMPILE := $(patsubst %.c, %.o, $(INPUTS))
LINK := $(TARGET).out

all: $(COMPILE) $(LINK) $(BINARY)

%.o: %.c
	$(CC) $(CFLAGS) $(IFLAGS) -c $< -o $@

%.out: $(COMPILE)
	$(CC) $(LFLAGS) $^ -o $@

clean:
	rm -f $(COMPILE) $(TARGET)
