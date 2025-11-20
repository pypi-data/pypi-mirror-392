import pkgutil
__path__ = pkgutil.extend_path(__path__,__name__)
__path__.reverse()

import math
from .. import *
from .. import rtmq2

"""
DEVice Management Core Module for RTMQv2 Framework

This module provides the fundamental hardware abstraction layer and device management utilities
for the RTMQv2 (Real-Time Multi-Queue version 2) framework. It implements core communication protocols
and hardware interaction patterns that enable high-level control of the RT-Core and its peripherals.

The RT-Core operates with 4 ns timing resolution (F_sys = 250 MHz) and provides deterministic execution
for quantum experiment control applications, requiring precise and efficient hardware abstraction.

The module implements:
- Bus abstraction for RTMQv2 hardware communication
- Port control with bit-field manipulation for fine-grained register access
- Device management utilities for hardware configuration
- Hardware abstraction layer for simplified device interaction

Key Components:
- bus: Bus communication abstraction for executing RTMQv2 assembly operations
- bit_field: Bit-level manipulation for precise control over register bits
- port: Port control with bit-field operations for register access
- pin: Individual pin control for fine-grained I/O manipulation
- dev: Device management base class for hardware abstraction
- ports: Multi-port device management for complex devices

This module serves as the foundation for all device-specific implementations in the RTMQv2 framework,
including the standard device (std), real-time waveform generator (rwg), and flexible peripheral platform (flex).
"""

LO = 0xfffff
HI = 0xfff00000

class bus(table):
    """
    Bus communication abstraction.
    
    This class provides a high-level interface for bus operations, allowing
    configuration and execution of assembly instructions through a
    simplified API.
    
    Attributes:
        cfg: Configuration context for assembly operations
        
    Methods:
        __call__: Execute bus operations with given parameters
        __repr__: String representation of bus operations
        rtmq2: Convert bus operations to RTMQ v2 assembly
    """
    
    def __call__(self, key, *args):
        """
        Execute bus operation with given key and arguments.
        
        Args:
            key: Operation key or register name
            *args: Additional arguments for the operation
            
        Returns:
            self: For method chaining
        """
        cfg = self.__dict__.get('cfg',None)
        if cfg not in (None,list):
            asm = rtmq2.asm
            asm.__enter__()
            asm.core = cfg.core
        if len(self) > 0 and self[-1][0].endswith('.'):
            if cfg is list:
                self[-1][0] += key
            else:
                self[-1][0] = self[-1][0][:-1]
                rtmq2.sfs(self[-1][0], key)
        elif type(key) is str and key[0] not in '&$':
            if len(self) == 0 or cfg is list:
                super().append([key])
            else:
                self[-1][0] = key
        else:
            args = (key,) + args
        if cfg is list:
            self[-1] += list(args)
        elif len(args) > 0:
            key = self[-1][0]
            func = rtmq2.__dict__.get(key,None)
            if func is None:
                if len(args) == 1:
                    #print(f"mov('{key}',{hex(args[0])})")
                    rtmq2.mov(key,args[0])
                else:
                    #print(f"mov('{key}',({hex(args[0])},{hex(args[1])}))")
                    rtmq2.mov(key,args)
            else:
                #print(f'{key}('+','.join(map(hex,args))+')')
                func(*args)
        if cfg not in (None,list):
            try:
                if len(rtmq2.asm) > 0:
                    cfg(rtmq2.asm(),dnld=0)
            finally:
                rtmq2.asm.__exit__(0,0,0)
        return self
    def __repr__(self):
        """
        Return string representation of bus operations.
        
        Returns:
            str: String representation of all bus operations in the table
        """
        return '\n'.join(i[0]+'('+','.join(map(lambda v:hex(v) if type(v) is int else f"'{v}'",i[1:]))+')' for i in self[:])
    def rtmq2(self):
        """
        Convert bus operations to RTMQ v2 assembly instructions.
        
        This method processes each operation in the bus table and converts it
        to the corresponding RTMQ v2 assembly instruction.
        
        Returns:
            None
        """
        if self.__dict__.get('cfg',None) is not list:
            return
        for i in self:
            key = i[0]
            func = rtmq2.__dict__.get(key,None)
            if func is None:
                if '.' in key:
                    key,sub = key.split('.')
                    #print(f"sfs('{key}','{sub}')")
                    rtmq2.sfs(key,sub)
                if len(i) == 2:
                    #print(f"mov('{key}',{hex(i[1])})")
                    rtmq2.mov(key,i[1])
                elif len(i) == 3:
                    #print(f"mov('{key}',({hex(i[1])},{hex(i[2])}))")
                    rtmq2.mov(key,i[1:])
            else:
                #print(f'{key}('+','.join(map(hex,i[1:]))+')')
                func(*i[1:])

bus = context(table=bus)

class bit_field:
    """
    Bit field descriptor for port control operations.
    
    This class provides bit-level manipulation capabilities for port operations,
    allowing precise control over individual bits or bit ranges within port values.
    
    Attributes:
        rng: Tuple representing the bit range (start, end)
        msk: Bit mask for the specified range
        
    Methods:
        __init__: Initialize bit field with specified range
        __get__: Get value from the bit field
        __set__: Set value to the bit field
    """
    
    def __init__(self, *args):
        """
        Initialize bit field with specified bit range.
        
        Args:
            *args: Bit positions or range specification
            
        Raises:
            AssertionError: If no arguments provided or invalid range
        """
        assert len(args) > 0, 'Empty bits field'
        self.rng = (min(args),max(args))
        self.msk = ((1<<(self.rng[1]+1-self.rng[0]))-1)<<self.rng[0]

    def __get__(self, obj, cls=None):
        """
        Get value from the bit field.
        
        Args:
            obj: Object containing the value
            cls: Class (optional)
            
        Returns:
            int: Value extracted from the bit field
        """
        if obj is None:
            return self
        return (obj._val & self.msk) >> self.rng[0]

    def __set__(self, obj, val):
        """
        Set value to the bit field.
        
        Args:
            obj: Object to modify
            val: Value to set in the bit field
        """
        obj._val &= ~self.msk
        obj._val |=  self.msk & (val << self.rng[0])
        
class port:
    """
    Port control class for hardware interface operations.
    
    This class provides a high-level interface for controlling hardware ports
    with support for bit-field manipulation and bus communication.
    
    Attributes:
        _key: Port identifier or name
        _val: Current port value
        
    Methods:
        __init__: Initialize port with optional key
        __call__: Execute port operation with arguments
        on: Turn on specified bits
        off: Turn off specified bits
        set: Set specific bit values
    """
    
    def __init__(self, _key=None):
        """
        Initialize port with optional identifier.
        
        Args:
            _key: Port identifier (defaults to class name if None)
        """
        self._key = self.__class__.__name__ if _key is None else _key

    def __call__(self, *args, **kwargs):
        """
        Execute port operation with given arguments.
        
        Args:
            *args: Positional arguments for port operation
            **kwargs: Keyword arguments for port operation
            
        Returns:
            self: For method chaining
        """
        bus(self._key)
        if len(args) == 0 and len(kwargs) == 0:
            return
        nargs = len(args)
        for i in args[::-1]:
            if type(i) in (tuple,list):
                nargs -= 1
            else:
                break
        self._val = 0 if nargs < 2 else args[0]
        for i, v in args[nargs:]:
            if type(i) in (tuple,list):
                bit_field(*i).__set__(self,v)
            elif self._val == 0:
                self._val = (v&1)<<i
            else:
                self._val |= (v&1)<<i
        for k, v in kwargs.items():
            setattr(self, k, v)
        if nargs == 0:
            val = self._val
            msk = None
        elif nargs == 1:
            val = args[0]
            msk = self._val if len(args)-nargs+len(kwargs) > 0 else None
        else:
            val = self._val
            msk = args[1]
        if msk is None:
            bus(val)
        else:
            bus(val,msk)
        return self
    
    def on(self, *args, **kwargs):
        """
        Turn on specified bits of the port.
        
        Args:
            *args: Bit positions or bit field ranges to turn on
            **kwargs: Bit field names to turn on
            
        Returns:
            self: For method chaining
        """
        self._val = 0
        if len(args) > 0:
            for i in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i
                else:
                    self._val |= 1<<i
        else:
            for k,v in kwargs.items():
                setattr(self, k, -1)
        msk = self._val
        self(-1, msk)
    
    def off(self, *args, **kwargs):
        """
        Turn off specified bits of the port.
        
        Args:
            *args: Bit positions or bit field ranges to turn off
            **kwargs: Bit field names to turn off
            
        Returns:
            self: For method chaining
        """
        self._val = 0
        if len(args) > 0:
            for i in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i
                else:
                    self._val |= 1<<i
        else:
            for k,v in kwargs.items():
                setattr(self, k, -1)
        msk = self._val
        self(0, msk)
    
    def set(self, *args, **kwargs):
        """
        Set specific bit values of the port.
        
        Args:
            *args: Bit position-value pairs to set
            **kwargs: Bit field name-value pairs to set
            
        Returns:
            self: For method chaining
        """
        if len(args) > 0:
            self._val = 0
            for i,v in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,v)
                elif self._val == 0:
                    self._val = (v&1)<<i
                else:
                    self._val |= (v&1)<<i
            val = self._val
            self._val = 0
            for i,v in args:
                if type(i) in (tuple,list):
                    bit_field(*i).__set__(self,-1)
                elif self._val == 0:
                    self._val = 1<<i   
                else:
                    self._val |= 1<<i
            msk = self._val
        else:
            self._val = 0
            for k, v in kwargs.items():
                setattr(self, k, v)
            val = self._val
            self._val = 0
            for k, v in kwargs.items():
                setattr(self, k, -1)
            msk = self._val
        self(val, msk)

class pin:
    """
    Individual pin control class for hardware interface.
    
    This class provides fine-grained control over individual pins within a port,
    allowing read/write operations on specific pin positions.
    
    Attributes:
        port: Parent port object
        sub: Sub-port identifier (optional)
        pos: Pin position or bit range
        
    Methods:
        __init__: Initialize pin with port and position
        __call__: Read or write pin value
        on: Turn pin on (set to 1)
        off: Turn pin off (set to 0)
    """
    
    def __init__(self,port,sub=None,pos=None):
        """
        Initialize pin with port and position information.
        
        Args:
            port: Parent port object
            sub: Sub-port identifier (optional)
            pos: Pin position, bit range, or bit field name
        """
        self.port = port
        self.sub = sub
        if type(pos) is str:
            pos = getattr(port.__class__,pos,None)
            if type(pos) is bit_field:
                pos = pos.rng
        self.pos = pos

    def __call__(self, *args):
        """
        Read or write pin value.
        
        Args:
            *args: If no arguments, read pin value; if arguments provided, write value
            
        Returns:
            int: Pin value when reading, None when writing
        """
        if len(args) == 0:
            if self.pos is None:
                return rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub]
            elif type(self.pos) in (tuple,list):
                return ((rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub])>>self.pos[0])&((1<<(self.pos[1]+1-self.pos[0]))-1)
            else:
                return ((rtmq2.R[self.port._key] if self.sub is None else rtmq2.R[self.port._key][self.sub])>>self.pos)&1
        else:
            if self.pos is None:
                (self.port if self.sub is None else self.port[self.sub])(*args)
            else:
                (self.port if self.sub is None else self.port[self.sub]).set((self.pos,args[0]))
    
    def on(self):
        """Turn pin on by setting value to 1."""
        self(-1)
    
    def off(self):
        """Turn pin off by setting value to 0."""
        self(0)

class dev:
    """
    Device management base class for hardware abstraction.
    
    This class provides a foundation for device management, allowing
    configuration and control of hardware devices through port operations.
    
    Attributes:
        Inherits port configuration from initialization
        
    Methods:
        __init__: Initialize device with port configurations
        __setitem__: Set device port values
        __setattr__: Set device attributes with port handling
    """
    
    def __init__(self, **kwargs):
        """
        Initialize device with port configurations.
        
        Args:
            **kwargs: Port configurations as key-value pairs
        """
        for k,v in kwargs.items():
            if isinstance(v,port):
                self.__dict__[k] = v

    def __setitem__(self, key, val):
        """
        Set device port value using dictionary-like syntax.
        
        Args:
            key: Port identifier or index
            val: Value to set, can be tuple, table, or primitive value
            
        Returns:
            val: The value that was set
        """
        if type(key) is int:
            key = f'&{key:02x}'
        try:
            sub = super().__getattribute__(key)
        except:
            sub = None
        if isinstance(sub,port):
            if isinstance(self, ports):
                bus(self.__class__.__name__+f'.')
            if type(val) is tuple:
                if type(val[-1]) is dict:
                    sub(*val[:-1],**val[-1])
                else:
                    sub(*val)
            elif type(val) is table:
                sub(*val[:],**val.__dict__)
            else:
                sub(val)
        else:
            object.__setattr__(self, key, val)
        return val

    def __setattr__(self, key, val):
        """
        Set device attribute with port operation handling.
        
        Args:
            key: Attribute name
            val: Value to set
            
        Returns:
            val: The value that was set
        """
        try:
            sub = super().__getattribute__(key)
        except:
            sub = None
        if isinstance(sub,port):
            self[key] = val
        else:
            object.__setattr__(self, key, val)
        return val
    
class ports(port,dev):
    """
    Multi-port device management class.
    
    This class combines port and device functionality to manage multiple ports
    within a single device, providing unified access to port operations.
    
    Attributes:
        Inherits from both port and dev classes
        
    Methods:
        __getattribute__: Get attribute with automatic port operation handling
        __getitem__: Get port using dictionary-like syntax
        
    Inherits from:
        port: Provides port operation functionality
        dev: Provides device management functionality
    """
    
    def __getattribute__(self, key):
        """
        Get attribute with automatic port operation handling.
        
        Args:
            key: Attribute name
            
        Returns:
            Attribute value with port operation context
        """
        sub = super().__getattribute__(key)
        if isinstance(sub,port):
            bus(self._key+f'.')
        return sub

    def __getitem__(self, key):
        """
        Get port using dictionary-like syntax.
        
        Args:
            key: Port identifier or index
            
        Returns:
            port: Port object for the specified key
        """
        bus(self._key+f'.')
        if type(key) is int:
            key = f'&{key:02x}'
        key = str(key)
        return self.__dict__.get(key,port(key))