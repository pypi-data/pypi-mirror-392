"""Core low-level module for CodeBot-CB2.

The *botcore* module gives you direct access to all the hardware on the CodeBot CB2.
    * system = `System`
    * leds = `CB_LEDs`
    * exp = `Expansion`
    * spkr = `Speaker`
    * buttons = `Buttons`
    * prox == `Proximity`
    * ls = `LineSensors`
    * enc = `Encoders`
    * motors = `Motors`
    * accel = `LIS2HH`

..
    Timers in use:
        prox emit = T1.3
        spkr = T2.1
        motor L/R = T3.1, T3.2
        Scheduler (SW) = T4
        EncL (PA1) = T5.2 (alt T2.2)
        EncR (PA2) = T5.3 (alt T2.3)

"""

# This is the "pure python" implementation.
import pyb
from pyb import Pin, Timer, ADC
import machine
#import stm
import micropython
from lis2hh import LIS2HH
from cb2hw import read_ls, set_led_val, read_leds, write_leds, prox_detect
import cb2hw




class System:
    """General system-level functions"""
    def __init__(self):
        # ADC object for internal channel reads (vref, temp)
        self.adcall = pyb.ADCAll(12, 0x70000)
        self.adc_cal_vref = self.adcall.read_vref()

        self.batt_sense = Pin(Pin.cpu.A3, Pin.ANALOG)
        self.batt_adc = ADC(self.batt_sense)

        self.pwr_is_usb = Pin(Pin.cpu.B2, Pin.IN, pull=Pin.PULL_UP)  # High if powered by USB

    def __str__(self):
        return "{:.1f}V, {:.1f}F, {}".format(self.pwr_volts(), self.temp_F(), "USB" if self.pwr_is_usb() else "BATT")

    def pwr_is_usb(self):
        """Are we powered by USB or Battery? (based on Power switch)
        
        Returns:
           int : 0 (Battery) or 1 (USB)
        """
        return self.pwr_is_usb.value()


    def pwr_volts(self):
        """Measure power supply voltage (battery or USB)
                
        Returns:
           float : Power supply voltage
        """
        return 2 * self.adc_cal_vref * self.batt_adc.read() / 4095


    def temp_C(self):
        """Measure the temperature in Celsius
        
        Returns:
           float : degrees C
        """
        return self.adcall.read_core_temp()


    def temp_F(self):
        """Measure the temperature in Fahrenheit
        
        Returns:
           float : degrees F
        """
        return self.temp_C() * 9 / 5 + 32



class Expansion:
    """Access to the Expansion Port"""
    def __init__(self):
        self.exp_gpio_0 = Pin(Pin.cpu.A6)
        self.exp_gpio_1 = Pin(Pin.cpu.A7)
        self.exp_gpio_0_alt = Pin(Pin.cpu.D2)   # Additional alternate funcs, e.g UART5_RX
        self.exp_gpio_1_alt = Pin(Pin.cpu.C12)  # Additional alternate funcs, e.g UART5_TX



class Speaker:
    """Control the Speaker"""
    def __init__(self):
        self.spkr = Pin(Pin.cpu.A5, Pin.AF_PP, af=Pin.AF1_TIM2)
        self.tim = Timer(2, freq=1000)
        self.ch = self.tim.channel(1, Timer.PWM, pin=self.spkr)
        self.ch.pulse_width_percent(0)

    def __str__(self):
        return "{}, {} Hz".format("On" if self.ch.pulse_width_percent() > 0.0 else "Off", self.tim.freq())

    def pitch(self, freq, duty=50):
        """Play a tone on the speaker, with the specified frequency and duty-cycle.

        This function produces a simple `Square wave <https://en.wikipedia.org/wiki/Square_wave>`_ to drive the speaker.

        Args:
          freq (int): Frequency in Hertz
          duty (int): Duty-cycle, 0-100% (ratio of high pulse to period of tone)
        """
        # Direct PWM output via TIM2_CH1
        self.tim.freq(freq)
        self.ch.pulse_width_percent(duty)


    def off(self):
        """Stop output to speaker."""
        self.ch.pulse_width_percent(0)



class Buttons:
    """Access to pushbutton switches BTN-0 and BTN-1."""
    def __init__(self):
        self.stat = [False, False]
        self.btn0 = Pin(Pin.cpu.B0, Pin.IN, pull=Pin.PULL_UP)
        self.btn1 = Pin(Pin.cpu.B1, Pin.IN, pull=Pin.PULL_UP)
        pyb.ExtInt(self.btn0, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, self._irq_press)
        pyb.ExtInt(self.btn1, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_UP, self._irq_press)

    def __str__(self):
        return "{}".format(self.is_pressed())

    def _irq_press(self, line):
        self.stat[line] = True

    def was_pressed(self, num=None):
        """Return True if specified button was pressed since last call of this function.
        Default with num=None, returns tuple of both buttons status since last call.

        Args:
          num (int): 0 for BTN-0, 1 for BTN-1
        """
        btn = tuple(self.stat)
        if num is None:
            self.stat[0] = self.stat[1] = False
            return btn
        else:
            self.stat[num] = False
            return btn[num]


    def is_pressed(self, num=None):
        """Return True if specified button is pressed, or tuple of both buttons if num=None.

        Args:
          num (int): 0 for BTN-0, 1 for BTN-1
        """
        if num is None:
            return (not self.btn0.value(), not self.btn1.value())
        elif num == 0:
            return not self.btn0.value()
        elif num == 1:
            return not self.btn1.value()
        else:
            raise ValueError("Button num must be 0, 1, or None")



class LedDriver:
    def __init__(self):
        self.led_usb = Pin(Pin.cpu.B9, Pin.OUT_PP)
        self.led_le = Pin(Pin.cpu.B11, Pin.OUT_PP)
        self.led_le.value(0)
        self.led_oe = Pin(Pin.cpu.B12, Pin.OUT_PP)
        self.led_spi = machine.SPI(2, baudrate=10000000)   # 10MHz bit rate for led_spi, satisfies following:
        # LED shift registers require >= 10ns stability of SDO before rising edge of CLK
        #                             >= 20ns pulse width for CLK and LE

        # Proximity emitter-drive enables upper 16 bits of LEDs. TIMER1_CH3 = PWM, active low
        self.prox_pwm = Pin(Pin.cpu.A10, Pin.AF_PP, af=Pin.AF1_TIM1)
        self.prox_tim = Timer(1, freq=56000)
        self.prox_ch = self.prox_tim.channel(3, Timer.PWM_INVERTED, pin=self.prox_pwm, pulse_width_percent=0)
        self.prox_duty = 50  # % duty-cycle when enabled

        # Init low-level control
        cb2hw.init_led_spi(self.led_spi)
        self.write = cb2hw.write_leds
        self.read = cb2hw.read_leds

        # Initialize for use
        self.write(0)
        self.enable(True)

    def enable(self, do_enable):
        # Assert active-low enable for LEDs
        self.led_oe.value(not do_enable)
        self.prox_ch.pulse_width_percent(self.prox_duty if do_enable else 0)

    # Write 32-bit value to LED driver shift registers.
    #   'val' is big-endian bitmask:
    #        P7.   P6.   P5.   P4.   P3.    P2.    P1.    P0.
    #        PWR.  X_R.  X_L.  LS4.  LS3.   LS2.   LS1.   LS0
    #        B0.   B1.   B2.   B3.   B4.    B5.    B6.    B7.      // user byte reversed from schematic
    #        ER.   EL.   L2-0. L2-1. L03-0. L03-1. L14-0. L14-1.   // LS emitters reversed from schematic
    def write_leds(self, val):
        # Pure python version - prefer cb2hw version for speed!
        # With native code emitter this function completes in about 100uS. Only 3uS to shift bits out SPI, rest is overhead.
        le = self.led_le.value
        bval = val.to_bytes(4, "big")  # Convert val to 32-bit big-endian bytes buffer
        self.led_spi.write(bval)
        # Latch-in the new data
        le(1)
        le(0)


class CB_LEDs:
    """Manage all the LEDs on CodeBot."""
    def __init__(self):
        self.driver = LedDriver()
        self.set_val = set_led_val

    def user(self, b):
        """Set all User *Byte* LEDs to the given binary integer value or list/tuple of bools.

        Args:
            b : *int* value used to set LEDs, from 0 to 255 (2 :superscript:`8`-1) ; or,
            b : *list* of 8 bools.

        Example::

            leds.user(0)    # turn all User LEDs off
            leds.user(255)  # turn all User LEDs on
            leds.user(0b10101010)  # Alternating LEDs
            leds.user( [True, False, False, True, True, True, True, True] )

        """
        set_led_val(b, 8, 8, True)


    def user_num(self, num, val):
        """Set single User *Byte* LED.

        Args:
            num (int): Number of LED *bit*, 0-7.
            val (bool): Value of LED (``True`` or ``False``)
        """
        num = int(num)
        if 0 <= num < 8:
            set_led_val(int(val), 15 - num, 1)
        else:
            raise ValueError("User LED must be in range 0-7.")


    def ls(self, b):
        """Set all User *Line Sensor* marker LEDs to the given binary integer value, or list/tuple of bools.

        Args:
            b : *int* value used to set LEDs, from 0 to 31 (2 :superscript:`5`-1), or
            b : *list* of 5 bools. (see `botcore.CB_LEDs.user` for example)
        """
        set_led_val(b, 16, 5)


    def ls_num(self, num, val):
        """Set single *Line Sensor* marker LED.

        Args:
            num (int): Number of LED *bit*, 0-4.
            val (bool): Value of LED (``True`` or ``False``)
        """
        num = int(num)
        if 0 <= num < 5:
            set_led_val(int(val), 16 + num, 1)
        else:
            raise ValueError("LS LED must be in range 0-4.")


    def ls_emit(self, ls_num, pwr):
        """Set *Line Sensor* infrared emitter LED to specified power level.

        Args:
            ls_num (int): Number of *Line Sensor* 0-4
            pwr (int): Power level 0-2
        """
        ls_ofs = (2, 0, 4, 2, 0)[ls_num]
        ls_val = (0, 1, 3)[pwr]
        set_led_val(ls_val, ls_ofs, 2)


    def pwr(self, is_on):
        """Set *Power* LED.

        Args:
            is_on (bool): Turn ON if ``True``
        """
        set_led_val(int(is_on), 23, 1)


    def usb(self, is_on):
        """Set *USB* LED.

        Args:
            is_on (bool): Turn ON if ``True``
        """
        self.driver.led_usb.value(is_on)


    def enc_emit(self, b):
        """Set both *Encoder* emitter LEDs (2-bit value).

        Args:
            b (int): Binary value, 0=off, 1=left, 2=right, 3=both
        """
        set_led_val(b, 6, 2)


    def prox(self, b):
        """Set both Proximity marker LEDs.

        Args:
            b : *int* binary value, 0=off, 1=left, 2=right, 3=both ; or,
            b : *list* of 2 bools. (see `botcore.CB_LEDs.user` for example)
        """
        set_led_val(b, 21, 2)


    def prox_num(self, num, val):
        """Set single *Proximity* marker LED.

        Args:
            num (int): Number of LED *bit*, 0-1.
            val (bool): Value of LED (``True`` or ``False``)
        """
        num = int(num)
        if 0 <= num < 2:
            set_led_val(int(val), 21 + num, 1)
        else:
            raise ValueError("Prox LED must be 0 or 1.")


    def prox_emit(self, pwr):
        # Set power level 0-8, yeilding 0-80mA.
        # WARNING: LED not rated for continuous operation above 40mA (pwr=4)
        #val = (0x00, 0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF)[pwr]
        val = (0x00, 0x01, 0x03, 0x07, 0x0F, 0x0F, 0x0F, 0x0F, 0x0F)[pwr]
        set_led_val(val, 24, 8)



class Proximity:
    """Manage the proximity sensors"""
    def __init__(self, leds):
        self.leds = leds
        self.prox_l_tmr = Pin(Pin.cpu.A8, Pin.IN)
        self.prox_r_tmr = Pin(Pin.cpu.A9, Pin.IN)
        self.range = cb2hw.prox_detect

    def range(self, samples=4, power=1, rng_low=0, rng_high=100):
        """Scan proximity sensors and return 0-100% range for each.
        This function runs a successive approximation algorithm to find the minimum range at which
        an object is detected by each sensor independently.

        Args:
            samples (int): Number of samples to read. Larger values give more accuracy at the expense of a longer scan time.
            power (int): Emitter power (0-8). (0=OFF,... 8=MAX)
            rng_low (int): Lowest sensitivity range (0-100) to scan within.
            rng_high (int): Highest sensitivity range (0-100) to scan within

        Returns:
            tuple of (L, R) int proximity values: 0-100 if object detected, or -1 if not.

            - If samples=1, returns bool (L, R) values.
            - **Note:** When samples=1 the **rng_high** value is not used. A single sample is taken at **rng_low**.
        """
        pass


    def detect(self, power=1, sens=100):
        """Return bool (L,R) of detection at given sensitivity level.

        Args:
            power (int): Emitter power (1-8).
            sens (int): Sensor sensitivity (0-100). Percent range from 0=least to 100=most sensitive.

        Returns:
            tuple of (L, R) bool detect status.
        """
        return prox_detect(1, power, sens)



class LineSensors:
    """Manage the line sensors."""
    def __init__(self, leds):
        self.leds = leds
        # Line sensors - reversed order from schematic label vs silkscreen
        # Reflection = lower ADC value
        ls4_adc = ADC(Pin(Pin.cpu.C0, Pin.ANALOG))
        ls3_adc = ADC(Pin(Pin.cpu.C1, Pin.ANALOG))
        ls2_adc = ADC(Pin(Pin.cpu.C2, Pin.ANALOG))
        ls1_adc = ADC(Pin(Pin.cpu.C3, Pin.ANALOG))
        ls0_adc = ADC(Pin(Pin.cpu.A0, Pin.ANALOG))

        self.emit_pwr = 2  # valid values are 1 (20mA) and 2 (40mA)
        self.sensor = (ls0_adc, ls1_adc, ls2_adc, ls3_adc, ls4_adc)
        self.thresh = 2500
        self.reflective_line = True

        # Init direct cb2hw functions
        self.check = cb2hw.check_ls

    def check(self, thresh=1000, is_reflective=False):
        """Fast check of all line sensors against threshold(s). Controls emitter also.

           Return a **tuple** of values for *all* line sensors. By default these are **bool** values indicating *presence of a line*,
           based on given parameters. See below for alternate behavior based on parameter types.

        Args:
            thresh(int): Threshold value to compare against sensor readings.
            is_reflective(bool): Set to True if the line being checked is reflective (white), False if not (black).

        Returns:
           tuple [5]: Collection of **bool** "line detected" values.

           - If *thresh=0*, returns raw ADC values (*ints*).
           - If *is_reflective* is an **int** value it is interpreted as *thresh_upper*, and the function returns -1,0,+1 for readings below/within/above thresholds.

        """
        pass


    def calibrate(self, threshold, is_reflective_line):
        """Set parameters used to detect presence of a line.

        Args:
            threshold (int): Threshold of ADC reading, below which *reflection* is detected. 0-4095 (2 :superscript:`12`-1)
            is_reflective_line (bool): Is the line reflective?
        """
        self.thresh = threshold
        self.reflective_line = is_reflective_line


    def read(self, num):
        """Read the raw ADC value of selected *Line Sensor*.

        Args:
            num (int): Number of *Line Sensor* to read (0-1)
        """
        self.leds.ls_emit(num, self.emit_pwr)
        pyb.udelay(200)
        val = self.sensor[num].read()
        self.leds.ls_emit(num, 0)
        return val


    def read_all(self):
        self.leds.set_val(0x3F, 0, 6)  # all emitters on full power
        pyb.udelay(200)
        vals = read_ls()
        self.leds.set_val(0, 0, 6)
        return vals

    def is_line(self, num):
        """Check for presence of line beneath specified *Line Sensor* using current calibration parameters.

        Args:
            num (int): Number of *Line Sensor* to read (0-1)
        """
        detect =  self.read(num) < self.thresh
        return detect if self.reflective_line else not detect



class Encoders:
    """Manage the wheel encoders.
    This class demonstrates simple low-level sensing of encoders via ADC channels. Higher performance implementations
    are available in separate modules, such as :mod:`timed_encoders`.
    """
    # Other implementation options
    # Option 1: Count in IRQ, Python handler
    # Option 2: Use Timer.IC (Input Capture mode) enc_l_tmr = Timer5,CH2 ; enc_r_tmr = Timer5,CH3
    #             * That would allow either counting in hardware and polling the count periodically, or
    #             * Capturing a running timer-count on enc transition and counting at IRQ.
    def __init__(self, leds):
        self.leds = leds
        enc_l_adc = ADC(Pin(Pin.cpu.A1, Pin.ANALOG))
        enc_r_adc = ADC(Pin(Pin.cpu.A2, Pin.ANALOG))
        self.sensor = (enc_l_adc, enc_r_adc)
        self.thresh = 2000

    def read(self, num):
        """Read given analog encoder value"""
        self.leds.enc_emit(1 << num)
        val = self.sensor[num].read()
        self.leds.enc_emit(0)
        return val


    def is_slot(self, num):
        """Check for slot in given encoder disc"""
        return self.read(num) > self.thresh



class Motors:
    """Manage the *Motors*"""
    def __init__(self):
        self.motor_stby = Pin(Pin.cpu.A4, Pin.OUT_PP)
        self.motor_r_in1 = Pin(Pin.cpu.B13, Pin.OUT_PP)
        self.motor_r_in2 = Pin(Pin.cpu.B14, Pin.OUT_PP)
        self.motor_l_in1 = Pin(Pin.cpu.C8, Pin.OUT_PP)
        self.motor_l_in2 = Pin(Pin.cpu.C9, Pin.OUT_PP)
        self.motor_l_pwm = Pin(Pin.cpu.C6, Pin.AF_PP, af=Pin.AF2_TIM3)
        self.motor_r_pwm = Pin(Pin.cpu.C7, Pin.AF_PP, af=Pin.AF2_TIM3)

        # Init with 0=Left, 1=Right
        self.in1 = (self.motor_l_in1, self.motor_r_in1)
        self.in2 = (self.motor_l_in2, self.motor_r_in2)

        # Motor PWM connections: L=TIM3_CH1, R=TIM3_CH2
        self.PWM_RATE = 1000   # Hz
        self.tim3 = Timer(3, freq=self.PWM_RATE)
        self.pwm = (
            self.tim3.channel(1, Timer.PWM, pin=self.motor_l_pwm),
            self.tim3.channel(2, Timer.PWM, pin=self.motor_r_pwm)
        )

        self.enable(False)

    def enable(self, do_enable):
        """Enable the motors.

        Args:
            do_enable (bool): Set ``True`` to allow motors to run.
        """
        self.motor_stby.value(do_enable)


    def run(self, num, pwr):
        """Set specified *motor* to given *power* level.

        Args:
            num (int): Number of motor: 0 (LEFT) or 1 (RIGHT)
            pwr (int): Power -100% to +100% (neg=CW=reverse, pos=CCW=forward)
        """
        self.in1[num].value(pwr < 0)
        self.in2[num].value(pwr > 0)
        self.pwm[num].pulse_width_percent(abs(pwr))  # LoL... Absolute POWER!



#micropython.alloc_emergency_exception_buf(100)

# Note: following was patch for MP bug, which has been corrected in our fork
# Explicity set "break and dead time" register: MOE=1, AOE=0
# stm.mem32[stm.TIM1 + stm.TIM_BDTR] = 0x00008C00

# Instantiate core objects
system = System()
leds = CB_LEDs()
exp = Expansion()
spkr = Speaker()
buttons = Buttons()
prox = Proximity(leds)
ls = LineSensors(leds)
enc = Encoders(leds)
motors = Motors()
accel = LIS2HH()

# Helpful constants
LEFT = 0
RIGHT = 1