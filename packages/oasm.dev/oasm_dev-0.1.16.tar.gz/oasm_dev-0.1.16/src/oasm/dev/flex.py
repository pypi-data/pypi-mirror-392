"""
Flexible Peripheral Extension Platform Module

This module provides support for the Flexible Peripheral Extension Platform,
a low-cost solution for integrating analog and digital I/O channels into
experiment systems. It fulfills low-speed yet diverse monitoring and control
needs for parameters like temperatures, voltages, or positions.

The platform utilizes a standardized abstraction of interfaces between the RT-Core
and external chips, allowing easy integration of various AD/DA chips with different
features in a unified way. The timing resolution of the RT-Core is 4 ns (F_sys = 250 MHz).

Key Components:
- rsm: Runtime system management with extended bit fields for UART, coprocessor, SPI, and GPIO
- dio: Digital I/O port management with direction, inversion, and edge detection
- spi: SPI interface controller with support for multiple SPI segments and various devices
- cou: Parallel output ports for flexible configuration
- cin: Parallel input ports for flexible configuration
- ftw: Frequency tuning word ports for DDS (Direct Digital Synthesis) control
- flex: Main flexible device class with comprehensive configuration and control methods

Supported Interfaces:
- Parallel ports: For parallel data transfer to ADC/DAC or collective control signals
- Serial ports: SPI protocol for on-chip register configuration

Supported SPI Devices:
- AD5372: 32-channel DAC with calibration registers
- AD5791: 20-bit high precision DAC
- DAC8563: 16-bit dual-channel DAC
"""

from .std import *

# Flexible device register definitions
class rsm(rsm.__class__):
    """
    Runtime System Management (RSM) class for Flexible Peripheral Extension Platform.
    
    This class extends the base RSM class with additional control bits for various
    system components and interfaces in the Flex platform, including UART, coprocessor,
    SPI, and GPIO functionality.
    
    Bit Fields:
        uart: UART interface control - manages UART communication (bit 3)
        coproc: Coprocessor control - manages coprocessor functionality (bit 5)
        spi: SPI interface control - manages SPI communication interfaces (bit 6)
        gpio: GPIO control - manages general purpose input/output pins (bit 7)
    """
    uart = bit_field(3)  # UART interface control (bit 3)
    coproc = bit_field(5)  # Coprocessor control (bit 5)
    spi = bit_field(6)  # SPI interface control (bit 6)
    gpio = bit_field(7)  # GPIO control (bit 7)

rsm = rsm()

ttl = port('ttl')

class dio(ports):
    """
    Digital I/O (DIO) Port Management for Flexible Peripheral Extension Platform.
    
    This class manages digital input/output ports with comprehensive configuration
    capabilities including direction control, inversion settings, and edge detection
    for the Flex platform.
    
    Attributes:
        dir (port): Direction control port - configures each pin as input (0) or output (1)
        inv (port): Inversion control port - inverts the logic level of corresponding pins
        pos (port): Positive edge detection port - detects rising edges on input pins
        neg (port): Negative edge detection port - detects falling edges on input pins
    """
    
    def __init__(self):
        """Initialize digital I/O port management with direction, inversion, and edge detection."""
        super().__init__()
        self.dir = port('dir')  # Direction control (input=0, output=1)
        self.inv = port('inv')  # Inversion control (logic level inversion)
        self.pos = port('pos')  # Positive edge detection (rising edge)
        self.neg = port('neg')  # Negative edge detection (falling edge)

dio = dio()

class spi_ctl(port):
    """
    SPI Control Register
    
    Configures SPI communication parameters including clock division,
    SDI latency, phase, and polarity settings.
    
    Attributes:
        clk_div (bit_field): Clock divider (12 bits)
        sdi_ltn (bit_field): SDI latency (4 bits)
        pha (bit_field): Clock phase setting
        pol (bit_field): Clock polarity setting
    """
    
    clk_div = bit_field(0,11)
    sdi_ltn = bit_field(12,15)
    pha = bit_field(16)
    pol = bit_field(17)

class spi_cnt(port):
    """
    SPI Counter Register
    
    Manages SPI data transfer bit counts for total bits and SDO bits.
    
    Attributes:
        tot_bit (bit_field): Total number of bits to transfer (10 bits)
        sdo_bit (bit_field): Number of SDO bits (10 bits)
    """
    
    tot_bit = bit_field(0,9)
    sdo_bit = bit_field(10,19)

class spi(ports):
    """
    SPI Interface Controller
    
    Manages SPI communication with configurable segments, control registers,
    and data transfer operations for various SPI devices.
    
    Attributes:
        N_SPI_SEG (int): Number of SPI segments
        ctl (spi_ctl): SPI control register
        cnt (spi_cnt): SPI counter register
    """
    
    def __init__(self, idx, N_SPI_SEG):
        """
        Initialize SPI interface controller
        
        Args:
            idx (int): SPI interface index
            N_SPI_SEG (int): Number of SPI segments
        """
        super().__init__(f'spi{idx:02x}')
        self.N_SPI_SEG = N_SPI_SEG
        for i in range(N_SPI_SEG):
            setattr(self,f'&{i:02x}',port(f'&{i:02x}'))
        self.ctl = spi_ctl('ctl')
        self.cnt = spi_cnt('cnt')

    def config(self, pol, pha, sdi_ltn, clk_div):
        """
        Configure SPI communication parameters
        
        Args:
            pol (int): Clock polarity (0 or 1)
            pha (int): Clock phase (0 or 1)
            sdi_ltn (int): SDI latency (0-15)
            clk_div (int): Clock divider (0-4095)
        """
        self.ctl(pol=pol,pha=pha,sdi_ltn=sdi_ltn,clk_div=clk_div)

    def write(self, dat, bit_cnt):
        """
        Write data to SPI interface
        
        Args:
            dat (list): Data to write (list of integers)
            bit_cnt (int): Number of bits to transfer
        """
        for i in range(len(dat)):
            self[self.N_SPI_SEG-1-i](dat[i])
        self.cnt(tot_bit=bit_cnt, sdo_bit=bit_cnt)
    
    @staticmethod
    def wait():
        flex.wait(spi=1)
        std.timer(1,us=True,wait=2)
    
    def wr_5372(self, mod, adr, dat):
        """
        Low level SPI write function for AD5372 DAC.
        
        Args:
            mod (int): 2-bit mode selector
            adr (int): 6-bit address
            dat (int): 16-bit data
            
        Returns:
            None
            
        Note:
            For more detailed information, please refer to the AD5372 datasheet.
        """
        dat &= 0xffff
        dat |= bit_concat((mod, 2), (adr, 6)) << 16
        dat <<= 8
        self.write([dat], 24)
    
    def wr_5791(self, rwb, adr, dat):
        """
        Low level SPI write function for AD5791 high precision DAC.
        
        Args:
            rwb (int): Read/Write bit (0 for write operation)
            adr (int): 3-bit address
            dat (int): 20-bit data
            
        Returns:
            None
            
        Note:
            For more detailed information, please refer to the AD5791 datasheet.
        """
        dat &= 0xfffff
        dat |= bit_concat((rwb, 1), (adr, 3)) << 20
        dat <<= 8
        self.write([dat], 24)
    
    def wr_8563(self, cmd, adr, dat):
        """
        Low level SPI write function for DAC8563 dual-channel DAC.
        
        Args:
            cmd (int): 3-bit command selector
            adr (int): 3-bit address
            dat (int): 16-bit data
            
        Returns:
            None
            
        Note:
            For more detailed information, please refer to the DAC8563 datasheet.
        """
        dat &= 0xffff
        dat |= bit_concat((cmd, 3), (adr, 3)) << 16
        dat <<= 8
        self.write([dat], 24)
    
    def rd_5372(self, adr):
        """
        SPI register readback function for AD5372 DAC.
        
        Args:
            adr (int): Register address to read from
            
        Returns:
            int: Register value read from the AD5372
            
        Note:
            For valid register addresses, please refer to the AD5372 datasheet.
        """
        self.wr_5372(0b00, 0b000_101, adr)
        self.wait()
        self.wr_5372(0, 0, 0)
        self.wait()
        return pin(self)()
    
    def rd_5791(self, adr):
        """
        SPI register readback function for AD5791 DAC.
        
        Args:
            adr (int): Register address to read from
            
        Returns:
            int: Register value read from the AD5791
            
        Note:
            For valid register addresses, please refer to the AD5791 datasheet.
        """
        self.wr_5791(1, adr, 0)
        self.wait()
        self.wr_5791(0, 0, 0)
        self.wait()
        return pin(self)()
    
    def dac_5372(self, chn, val, dst="X"):
        """
        Set DAC outputs of AD5372 32-channel DAC.
        
        Args:
            chn (int): Channel number
            val (int or float): Output value
            dst (str, optional): Destination register type ('X' for data, 'C' for offset, 'M' for gain). Defaults to 'X'.
            
        Returns:
            None
            
        Note:
            If val is a float, it will be converted to integer. If dst is 'X', the value
            is treated as 2's complement and converted accordingly.
        """
        mod = {"X": 3, "C": 2, "M": 1}[dst]
        if mod == 3:
            if type(val) is float:
                val = round(val/20*0xfffe)
            val ^= 0x8000
            self.wr_5372(mod, chn+8, val)
        else:
            self.wr_5372(mod, chn+8, val)
    
    def dac_5791(self, val):
        """
        Set DAC outputs of AD5791 20-bit high precision DAC.
        
        Args:
            val (int or float): Output value in 2's complement format
            
        Returns:
            None
            
        Note:
            If val is a float, it will be converted to integer using the formula: round(val/20*0xffffe)
        """
        if type(val) is float:
            val = round(val/20*0xffffe)
        self.wr_5791(0, 1, val)
    
    def dac_8563(self, chn, val):
        """
        Set DAC outputs of DAC8563 16-bit dual-channel DAC.
        
        Args:
            chn (int): Channel number (0 or 1)
            val (int or float): Output value in 2's complement format
            
        Returns:
            None
            
        Note:
            If val is a float, it will be converted to integer using the formula: round(val/20*0xfffe)
            The value is then converted to 2's complement by XOR with 0x8000.
        """
        if type(val) is float:
            val = round(val/20*0xfffe)
        val ^= 0x8000
        self.wr_8563(0b011, chn, val)

class cou(ports):
    """
    Parallel Output Ports
    
    Manages parallel output ports with flexible configuration support. Each port can be up to 32 bits wide.
    These ports are used for parallel data transfer to external devices or for collective control signals.
    
    Attributes:
        N_COU (int or list): Number of parallel output ports or list of port configurations
    """
    
    def __init__(self, N_COU):
        """
        Initialize parallel output ports
        
        Args:
            N_COU (int or list): Number of parallel output ports or list of port configurations
        """
        super().__init__()
        if type(N_COU) in (tuple,list):
            for i in range(len(N_COU)):
                setattr(self,f'&{i:02x}',(N_COU[i] or port)(f'&{i:02x}'))
        else:
            for i in range(N_COU):
                setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

class cin(ports):
    """
    Parallel Input Ports
    
    Manages parallel input ports with flexible configuration support. Each port can be up to 32 bits wide.
    These ports are used for parallel data reception from external devices or for collective status signals.
    
    Attributes:
        N_CIN (int or list): Number of parallel input ports or list of port configurations
    """
    
    def __init__(self, N_CIN):
        """
        Initialize parallel input ports
        
        Args:
            N_CIN (int or list): Number of parallel input ports or list of port configurations
        """
        super().__init__()
        if type(N_CIN) in (tuple,list):
            for i in range(len(N_CIN)):
                setattr(self,f'&{i:02x}',(N_CIN[i] or port)(f'&{i:02x}'))
        else:
            for i in range(N_CIN):
                setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

class ftw(ports):
    """
    Frequency Tuning Word Ports
    
    Manages frequency tuning word ports for DDS (Direct Digital Synthesis) control.
    
    Attributes:
        N_DDS (int): Number of DDS channels
    """
    
    def __init__(self, N_DDS):
        """
        Initialize frequency tuning word ports
        
        Args:
            N_DDS (int): Number of DDS channels
        """
        super().__init__()
        for i in range(N_DDS):
            setattr(self,f'&{i:02x}',port(f'&{i:02x}'))

clr = port('clr')
ena = port('ena')
opt = port('opt')
amp = port('amp')
pow = port('pow')
ofs = port('ofs')
    
class flex(std.__class__):
    """
    Flexible Peripheral Extension Platform Class
    
    This class provides the main interface for the Flexible Peripheral Extension Platform,
    which is a crucial component of the RTMQv2 framework. It enables low-cost integration of
    analog and digital I/O channels for diverse monitoring and control needs in experiment systems.
    
    The platform offers a standardized abstraction between the RT-Core and external chips,
    supporting various AD/DA converters with different features in a unified way.
    
    Key Features:
    - Digital I/O management with direction, inversion, and edge detection
    - SPI interface control for multiple devices (AD5372, AD5791, DAC8563)
    - Counter input/output port management
    - DDS (Direct Digital Synthesis) channel configuration
    - Flexible device configuration with customizable parameters
    
    Inherits from std.__class__ for standard RTMQv2 functionality.
    """
    
    def config(self, N_DIO, N_COU, N_CIN, N_SPI, N_SPI_SEG=16, N_DDS=8):
        """
        Configure flexible device parameters and hardware resources.
        
        This method initializes the core configuration with specified resource counts,
        creating the necessary hardware interfaces and port structures for the flexible
        peripheral platform.
        
        Args:
            N_DIO (int): Number of digital I/O ports
            N_COU (int): Number of parallel output ports (each up to 32 bits wide) or list of port configurations
            N_CIN (int): Number of parallel input ports (each up to 32 bits wide) or list of port configurations
            N_SPI (int): Number of SPI interfaces
            N_SPI_SEG (int, optional): Number of SPI segments per interface. Defaults to 16.
            N_DDS (int, optional): Number of DDS (Direct Digital Synthesis) channels. Defaults to 8.
            
        Returns:
            None
            
        Note:
            Creates core configuration with all necessary hardware resources and initializes
            the required interface objects (SPI, COU, CIN, FTW).
        """
        self.__dict__['core'] = base_core(
        ["ICF", "ICA", "ICD", "DCF", "DCA", "DCD",
        "NEX", "FRM", "SCP", "TIM", "WCL", "WCH",
        "LED", "FAI", "MAC", "CPR",
        "TTL", "DIO", "CTR", "CSM", "TTS", "TEV",
        "CLR", "ENA", "OPT", "FTW", "POW", "AMP", "OFS", "SIG",
        "IOU", "COU", "IIN", "CIN"] + \
        [f"SPI{n:02X}" for n in range(N_SPI)], ["ICA", "DCA", "TIM"],
        {"NEX": [None]*32 + ["ADR", "BCE", "RTA", "RTD"],
        "FRM": ["PL1", "PL0", "TAG", "DST"],
        "SCP": ["MEM", "TGM", "CDM", "COD"],
        "WCL": ["NOW", "BGN", "END"],
        "WCH": ["NOW", "BGN", "END"],
        "DIO": ["DIR", "INV", "POS", "NEG"],
        "CTR": [None]*N_DIO,
        "FTW": [None]*N_DDS,
        "IOU": [None]*(len(N_COU) if type(N_COU) in (tuple,list) else N_COU),
        "COU": [None]*(len(N_COU) if type(N_COU) in (tuple,list) else N_COU),
        "IIN": [None]*(len(N_CIN) if type(N_CIN) in (tuple,list) else N_CIN),
        "CIN": [None]*(len(N_CIN) if type(N_CIN) in (tuple,list) else N_CIN)} | \
        {f"SPI{n:02X}": ([None]*N_SPI_SEG + ["CTL", "CNT"]) for n in range(N_SPI)},
        8192, 131072)
        for i in range(N_SPI):
            self.__dict__[f'spi{i:02x}'] = spi(i,N_SPI_SEG)
        self.__dict__['cou'] = cou(N_COU)
        self.__dict__['cin'] = cin(N_CIN)
        self.__dict__['ftw'] = ftw(N_DDS)     

    def gpio(self, pos, out=1):
        """
        Configure GPIO (General Purpose Input/Output) pins
        
        This method configures and accesses GPIO pins using the parallel output (COU) and input (CIN) ports.
        
        Args:
            pos (int or list): GPIO position(s) to configure
            out (int, optional): Direction (1 for output, 0 for input). Defaults to 1.
        
        Returns:
            pin: Configured GPIO pin object
        """
        if type(pos) in (tuple,list):
            return [self.gpio(i,out) for i in pos]
        cfg = self.cou[6+(pos>>5)]
        if out:
            cfg.on(pos&0x1f)
        else:
            cfg.off(pos&0x1f)
        return pin(self.cou if out else self.cin,pos>>5,pos&0x1f)

    def dds(self, chn, f=None, a=None, p=None, o=None, enable=None, clear=None, linear=None):
        """
        Configure DDS (Direct Digital Synthesis) channel
        
        Args:
            chn (int): DDS channel number
            f (float, optional): Frequency in MHz. Defaults to None.
            a (float, optional): Amplitude (0-1). Defaults to None.
            p (float, optional): Phase offset. Defaults to None.
            o (float, optional): DC offset. Defaults to None.
            enable (bool, optional): Enable/disable channel. Defaults to None.
            clear (bool, optional): Clear phase accumulator. Defaults to None.
            linear (bool, optional): Linear frequency sweep mode. Defaults to None.
        """
        if enable in (False,0):
            ena.off(chn)           
        if f is None:
            self.ftw[chn]()
        else:
            self.ftw[chn](round(f*(1<<32)/250))
        if a is not None:
            amp(round(a*0xFFFF))
        if p is not None:
            pow(round(p*(1<<32)))
        if o is not None:
            ofs(round(o*0x7FFFF))
        if linear is not None:
            opt.set((chn,int(linear)))
        if clear in (True,1):
            clr.on(chn)
        if enable in (True,1):
            ena.on(chn)
            std.pause()
    
flex = flex(**globals())
flex.config(1,12,6,1)

def shift_out(sclk,mosi,dat,n=8):
    """
    Shift data out through SPI-like interface
    
    This function sends data through a MOSI (Master Out Slave In) pin using a clock signal
    on the SCLK pin, shifting out one bit at a time.
    
    Args:
        sclk: Clock pin object to generate clock pulses
        mosi: Master Out Slave In pin object to send data through
        dat (int): Data to shift out
        n (int, optional): Number of bits to shift. Defaults to 8.
        
    Returns:
        None
        
    Note:
        Data is shifted out from MSB (Most Significant Bit) to LSB (Least Significant Bit).
    """
    sclk.off()
    for i in range(n):
        mosi((dat>>(n-1-i))&1)
        sclk.on()
        sclk.off()

def shift_in(sclk,miso,reg,n=8):
    """
    Shift data in through SPI-like interface
    
    This function reads data from a MISO (Master In Slave Out) pin using a clock signal
    on the SCLK pin, and stores the result in the specified register.
    
    Args:
        sclk: Clock pin object to generate clock pulses
        miso: Master In Slave Out pin object to read data from
        reg: Register name to store shifted data
        n (int, optional): Number of bits to shift. Defaults to 8.
        
    Returns:
        None: Data is directly stored in the specified register
        
    Note:
        Uses std.pause(2) between clock edges for timing stabilization.
    """
    R[reg] = 0
    sclk.off()
    for i in range(n):
        sclk.on()
        std.pause(2)
        R[reg] |= miso()<<(n-1-i)
        sclk.off()
        std.pause(2)