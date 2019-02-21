import sys
import time
# import logging
import Adafruit_MAX31855.MAX31855 as MAX31855
import Adafruit_GPIO.SPI as SPI


def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


# Raspberry Pi software SPI configuration.
def init_sensor_software(cs):
    CLK = 25
    CS = cs
    DO = 18
    return MAX31855.MAX31855(CLK, CS, DO)


# Raspberry Pi hardware SPI configuration.
def init_sensor_hardware():
    SPI_PORT0 = 0
    SPI_DEVICE0 = 0
    return MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT0, SPI_DEVICE0, max_speed_hz=5000000))


def read_temp(sensor):
    raw = read_raw_temp(sensor)
    return 'Thermocouple Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(raw['thermo'], c_to_f(raw['thermo'])) + '\n' + \
           ' Internal Temperature: {0:0.3F}*C / {1:0.3F}*F'.format(raw['internal'], c_to_f(raw['internal']))


def read_raw_temp(sensor):
    temp = c_to_f(sensor.readTempC())
    internal = c_to_f(sensor.readInternalC())
    # raw = {'internal': internal1, 'thermo': temp1}
    return {'internal': internal, 'temp': temp}

# print(sys.path)


# sensor = init_hardware()
#
# print('Press Ctrl-C to quit.')
# while True:
#     print(read_temp(sensor))
#     time.sleep(5.0)
