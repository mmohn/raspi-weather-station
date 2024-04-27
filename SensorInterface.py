import bme280
import smbus2
from datetime import datetime, timedelta
import warnings
from time import sleep

class SensorInterface:
    """
        Interface class for the BME280 environmental sensor
        (humidity, pressure, temperature)
    """
    
    # humidity, pressure and temperature units of BME280
    HUMIDITY_UNIT = "%";
    PRESSURE_UNIT = " hPa";
    TEMPERATURE_UNIT = "°C";

    # limits for readout interval in seconds
    MIN_READOUT_INTERVAL = 1;
    MAX_READOUT_INTERVAL = 3600;


    def __init__(self, readout_interval=1, port=1, address=0x76):
        """
        Initialize SensorInterface object with given readout interval in seconds
        (default: 1), port number (default: 1) and address (default: 0x76).
        """
        self._address = address;
        self._bus = smbus2.SMBus(port);
        bme280.load_calibration_params(self._bus, self._address);
        self.readout_interval = readout_interval;
        self._last_readout = datetime.min;


    @property
    def humidity(self):
        if self._needs_refresh:
            self._read_values();
        return self._humidity;

    @property
    def pressure(self):
        if self._needs_refresh:
            self._read_values();
        return self._pressure;
    
    @property
    def temperature(self):
        if self._needs_refresh:
            self._read_values();
        return self._temperature;


    @property
    def readout_interval(self):
        return self._readout_interval;

    @readout_interval.setter
    def readout_interval(self, value):
        warn_str = "Readout interval {:g} replaced by {:s} value {:d}.";
        if not isinstance(value, (float, int)):
            raise TypeError
        elif value < self.MIN_READOUT_INTERVAL:
            warnings.warn(warn_str.format(value, "minimum", self.MIN_READOUT_INTERVAL), stacklevel=2);
            value = self.MIN_READOUT_INTERVAL;
        elif value > self.MAX_READOUT_INTERVAL:
            warnings.warn(warn_str.format(value, "maximum", self.MAX_READOUT_INTERVAL), stacklevel=2);
            value = self.MAX_READOUT_INTERVAL;
        self._readout_interval = value;


    @property
    def _needs_refresh(self):
        delta_time = datetime.now() - self._last_readout;
        if delta_time > timedelta(seconds=self._readout_interval):
            return True;
        else:
            return False;
    

    def _read_values(self):
        bme280_data = bme280.sample(self._bus, self._address);
        self._last_readout = datetime.now();
        self._humidity = bme280_data.humidity;
        self._pressure = bme280_data.pressure;
        self._temperature = bme280_data.temperature;



# Self-tests 

if __name__ == "__main__":
    print("Testing sensor initialization...");
    print("-"*80);
    try:
        SensorInterface(readout_interval="notanumber");
    except TypeError:
        print("Successfully raised TypeError.");
    print("Trigger warnings for maximum and minimum readout interval:");
    SensorInterface(readout_interval = float('inf'));
    my_sensor = SensorInterface(readout_interval = -1);
    print("\n\nChanging readout interval:");
    print("-"*80);
    my_sensor.readout_interval = 3;
    print(f"Readout interval successfully changed to {my_sensor.readout_interval}.");
    print("\n\nRead all values within readout interval:");
    print("-"*80);
    fmt_str = "{:20s}{:8.2f}{:3s}";
    print(fmt_str.format("Humidity", my_sensor.humidity, my_sensor.HUMIDITY_UNIT));
    first_time = my_sensor._last_readout;
    print(fmt_str.format("Pressure", my_sensor.pressure, my_sensor.PRESSURE_UNIT));
    print(fmt_str.format("Temperature", my_sensor.temperature, my_sensor.TEMPERATURE_UNIT));
    last_time = my_sensor._last_readout;
    if not first_time == last_time:
        print("Reading multiple values in quick succession was not successful!");
    else:
        print("Successfully read all three values with a single readout.");
    print("\n\nRead two values with two readouts:");
    print("-"*80);
    print(fmt_str.format("Humidity", my_sensor.humidity, my_sensor.HUMIDITY_UNIT));
    first_time = my_sensor._last_readout;
    sleep(my_sensor.readout_interval);
    print(fmt_str.format("Humidity", my_sensor.humidity, my_sensor.HUMIDITY_UNIT));
    last_time = my_sensor._last_readout;
    if first_time == last_time:
        print("Reading values twice was not successful!");
    else:
        print("Successfully read two values with two readouts.");
