from machine import SPI, Pin

class MCP3008:
    # The speed parameter is an integer in the range 500,000 through 32,000,000
    # and represents the SPI clock speed in Hz.
    max_speed_hz = 1000000  # 1MHz

    # SPI Pins
    # https://docs.micropython.org/en/latest/esp32/quickref.html#hardware-spi-bus
    # https://pinout.xyz/#
    SPI_CHANNEL = 1  # HSPI=1, VSPI=2

    if SPI_CHANNEL == 1:
        SPI_PINS = (14, 13, 12)  # sck (serial clock), mosi, miso
    else:
        SPI_PINS = (28, 23, 19)

        # Total number of channels on the chip
    noc = 8
    resolution = 10

    # 1 = single-ended, 0 = differential
    mode = 1

    def __init__(self, cs=15):
        # self.bus, self.device = bus, device
        self.spi = SPI(
            self.SPI_CHANNEL,
            baudrate=self.max_speed_hz,
            firstbit=SPI.MSB,  # SPI.LSB, SPI.MSB
            sck=Pin(self.SPI_PINS[0]),
            mosi=Pin(self.SPI_PINS[1]),
            miso=Pin(self.SPI_PINS[2])
        )

        # set chosen chip select (cs)
        self.CS_PIN = Pin(cs, Pin.OUT)
        self.CS_PIN.on()  # pin negated -> pin high to deselect

        # create arrays
        self.out_buf = bytearray(3)
        self.in_buf = bytearray(3)

    def read(self, channel):
        """SPI Interface for MCP3xxx-based ADCs reads. Due to 10-bit accuracy, the returned
        value ranges [0, 1023].
        
        :param int channel: channel to read from
        """

        # check if input in range of noc
        if (channel > self.noc - 1) or (channel < 0):
            return -1

        #  Order of send bytes:
        # 00000001 m210XXXX XXXXXXXX
        self.out_buf[0], self.out_buf[2] = 0x01, 0x0

        # set mode and channel in byte order correctly
        # see doc: table 5-2 and figure 6-1
        self.out_buf[1] = (channel | (self.mode << 3)) << 4

        # Performs an SPI transaction. Chip-select should be held active between blocks.
        self.CS_PIN.off()
        self.spi.write_readinto(self.out_buf, self.in_buf)
        self.CS_PIN.on()

        # combine data correctly
        # see doc: figure 6-1
        # Order:
        # XXXXXXXX XXXXX098 76543210
        data = ((self.in_buf[1] & 3) << 8) + self.in_buf[2]

        return self.convert_data(data)

    def convert_data(self, value):
        """Perform linear interpolation for x between (x1,y1) and (x2,y2) on adc"""

        return int((value / int(2 ** self.resolution - 1)) * 100), "percent"

    def close(self):
        self.spi.deinit()
        self.CS_PIN.off()
