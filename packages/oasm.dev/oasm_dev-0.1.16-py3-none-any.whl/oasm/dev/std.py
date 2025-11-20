"""
Standard Device Configuration Module for RTMQv2

This module defines standard device registers and basic operations
for RTMQv2 development environment. RTMQ (Real-Time Microsystem for Quantum physics)
is a 32-bit SoC framework designed for quantum experiment control and other scenarios
requiring nano-second timing precision.

The framework's design philosophy emphasizes that computation is part of the timing sequence,
with programs running on the RT-Core having well-defined timing characteristics.

Key Components:
- led: LED control port
- rsm: Runtime System Management with basic controls for master, monitor, and timer
- exc: Exception handling with various error types (halt, resume, TCS, division by zero, etc.)
- tim: Timer control port for precise timing operations
- std: Standard device class with core operations (boot, nop, hold, pause, timer, wait)

The RT-Core can directly access two address spaces:
- CSR (Control-Status Register) space: 8-bit address space (256 CSRs maximum)
- TCS (Tightly-Coupled Stack) space: Special memory space similar to windowed GPR space
"""

from . import *
from ..rtmq2 import *
    

led = port('led')


class rsm(port):
    """
    Runtime System Management (RSM) class.
    
    This class provides system management controls for runtime operations in the RTMQv2 framework.
    It manages various system-level functions and resources.
    
    Bit Fields:
        master: Master control - enables/disables the master controller (bit 0)
        monitor: Monitor control - enables/disables the monitoring system (bit 1)
        timer: Timer control - enables/disables the timer system (bit 2)
        
    Additional bit fields may be defined in derived classes for specific implementations.
    """
    master = bit_field(0)  # Master control (bit 0)
    monitor = bit_field(1)  # Monitor control (bit 1)
    timer = bit_field(2)  # Timer control (bit 2)

rsm = rsm()


class exc(port):
    """
    Exception Handling (EXC) class.
    
    This class provides exception handling functionality for various error conditions
    in the RTMQv2 framework. It allows control of exception states and resumption.
    
    Bit Fields:
        halt: Halt exception - triggers when the system halts (bit 0)
        resume: Resume control - resumes execution after halt (bit 1)
        tcs: TCS exception - triggers on TCS access errors (bit 2)
        byzero: Divide by zero exception - triggers on division by zero operations (bit 3)
        ich: Instruction cache hit exception - monitors instruction cache hits (bit 4)
        dch: Data cache hit exception - monitors data cache hits (bit 5)
        unaligned: Unaligned access exception - triggers on unaligned memory access (bit 6)
        fifo: FIFO exception - triggers on FIFO overflow/underflow conditions (bit 7)
        
    Additional bit fields may be defined in derived classes for specific implementations,
    such as PLL control in the RWG implementation.
    """
    halt = bit_field(0)  # Halt exception (bit 0)
    resume = bit_field(1)  # Resume control (bit 1)
    tcs = bit_field(2)  # TCS exception (bit 2)
    byzero = bit_field(3)  # Divide by zero exception (bit 3)
    ich = bit_field(4)  # Instruction cache hit exception (bit 4)
    dch = bit_field(5)  # Data cache hit exception (bit 5)
    unaligned = bit_field(6)  # Unaligned access exception (bit 6)
    fifo = bit_field(7)  # FIFO exception (bit 7)

exc = exc()


tim = port('tim')


class std(dev):
    """
    Standard Device class providing core operations.
    
    This class implements fundamental device operations including boot,
    timing control, wait states, and basic instruction execution.
    
    Attributes:
        C_STD: Standard core configuration
        us: Microsecond timing constant (250)
        
    Methods:
        boot: Boot the device from binary file
        nop: Execute no-operation instructions
        hold: Execute hold operations
        pause: Execute pause operations
        timer: Configure and execute timer operations
        wait: Execute wait operations with system management
    """
    
    C_STD = C_STD
    us = 250

    def boot(self):
        """
        Boot the device by loading binary instructions.
        
        Returns:
            asm: Assembly object containing loaded instructions
        """
        import os,sys
        with asm:
            path = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
            with open(os.path.join(path,self.__class__.__qualname__+'.bin'),'rb') as f:
                while True:
                    v = f.read(4)
                    if len(v) == 0:
                        break
                    asm(int.from_bytes(v))
            return asm()
        
    def nop(self, n = 1, hp = 0):
        """
        Execute no-operation instructions.
        
        Args:
            n: Number of NOP instructions (default: 1)
            hp: High priority flag (default: 0)
            
        Returns:
            self: For method chaining
        """
        bus('nop', n, hp)
        return self

    def hold(self, n = 1):
        """
        Execute hold operations.
        
        Args:
            n: Number of hold operations (default: 1)
            
        Returns:
            self: For method chaining
        """
        return self.nop(n, 1)

    def pause(self, n = 1):
        """
        Execute pause operations.
        
        Args:
            n: Number of pause operations (default: 1)
            
        Returns:
            self: For method chaining
        """
        return self.nop(n, 2)

    def timer(self, dur, us=False, strict=True, wait=1):
        """
        Configure and execute timer operations.
        
        Args:
            dur: Duration value
            us: Whether duration is in microseconds (default: False)
            strict: Strict timing mode (default: True)
            wait: Wait control flags (default: 1)
        """
        if wait & 1:
            self.hold()
        if us:
            dur = round(dur * self.us)
        if type(dur) is int:
            if dur == 0:
                return
            dur = dur - 1
        tim(dur)
        (exc.on if strict else exc.off)(resume=1)
        rsm.on(timer=1)
        if wait >> 1:
            self.hold()
    
    def wait(self, **kwargs):
        """
        Execute wait operations with system management.
        
        Args:
            **kwargs: System management control parameters (e.g., timer, monitor, master)
            
        Note:
            Uses the rsm attribute for system management operations.
        """
        self.rsm.on(**kwargs)
        self.hold()
        self.rsm.off(**kwargs)

std = std(**globals())