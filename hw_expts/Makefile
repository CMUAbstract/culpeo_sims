INPUTS := loadProfiling.c uart.c
TARGET := main

EXPT_ID ?= 0

# Conversion: V = 4096*adc_val/3.3
# Converted down to V = 4096*adc_val/2.5
VHIGH ?= 3228

VSAFE_PATH ?= ./Vsafe_culpeo/

USE_VSAFE ?= 0

REPEATS ?= 0

TEST_EXTERNAL ?= 0

ifeq ($(TEST_EXTERNAL),1)
CFLAGS += -DTEST_EXTERNAL
endif

ifeq ($(USE_VSAFE),1)
CFLAGS += -DUSE_VSAFE
endif

CONFIG ?= 0

MSPGCC_PATH := /opt/ti/mspgcc/bin
MSP430_INC_PATH := /opt/ti/mspgcc/include/
MSP430_LD_PATH := /opt/ti/mspgcc/include/

CC := $(MSPGCC_PATH)/msp430-elf-gcc
AR := $(MSPGCC_PATH)/msp430-elf-ar
OBJCP := $(MSPGCC_PATH)/msp430-elf-objcopy

DEVICE := MSP430FR5994

ifeq ($(DEVICE), MSP430FR5994)
MCU := msp430fr5994
endif

CFLAGS += -D __$(DEVICE)__ -DTLOAD=$(TLOAD) -DVHIGH=$(VHIGH) -mmcu=$(MCU) \
-O2 -static -DEXPT_ID=$(EXPT_ID) -DREPEAT_COUNT=$(REPEATS) -DCONFIG=$(CONFIG)
IFLAGS := -I $(MSP430_INC_PATH) -I$(VSAFE_PATH)
LFLAGS := -T $(MCU).ld -L $(MSP430_LD_PATH) -mmcu=$(MCU)

COMPILE := $(patsubst %.c, %.o, $(INPUTS))
LINK := $(TARGET).out
ECHO := $(info $$VSAFE_PATH is [${VSAFE_PATH}])


all: $(ECHO) $(COMPILE) $(LINK) $(BINARY)

%.o: %.c
	$(CC) $(CFLAGS) $(IFLAGS) -c $< -o $@

%.out: $(COMPILE)
	$(CC) $(LFLAGS) $^ -o $@

clean:
	rm -f $(COMPILE) $(TARGET)
