from amaranth import *
from amaranth.build import Platform

from pwm import PWM
from encoder import ABEncoder

class PinLocations:
    def __init__(self):
        self.clk = 3
        self.rst = 4
        self.enc_a_pin = 0
        self.enc_b_pin = 1
        self.pwm_out_pin = 2

class TinyTapeoutTop(Elaboratable):
    def __init__(self):
        # TT has 8 in, 8 out
        self.io_in = Signal(8)
        self.io_out = Signal(8)
        
        self.pins = PinLocations()        
        
    def ports(self):
        return [self.io_in, self.io_out]
    
    def inputPin(self, idx):
        return self.io_in[idx]
    
    @property 
    def pin_clock(self):
        return self.inputPin(self.pins.clk)

    @property 
    def pin_reset(self):
        return self.inputPin(self.pins.rst)

    def elaborate(self, platform):
        m = Module()

        pwm = PWM()
        encoder = ABEncoder()

        m.submodules.pwm = pwm
        m.submodules.encoder = encoder

        m.domains += ClockDomain("sync")

        dummy = Signal(7, reset = 0)
 
        # clock and reset
        m.d.comb += [
            ClockSignal("sync").eq(self.pin_clock),
            ResetSignal("sync").eq(self.pin_reset),
        ]

        # inputs
        m.d.comb += [
            encoder.a.eq(self.pins.enc_a_pin),
            encoder.b.eq(self.pins.enc_b_pin)
        ]

        # inter-module
        m.d.comb += [
            pwm.dutycycle.eq(encoder.counter)
        ]

        # outputs
        outputs = Cat(
            pwm.output,
            dummy
        )
        
        output_pins = self.io_out
        assert outputs.shape() == output_pins.shape(), "inconsistent output shape"

        m.d.comb += output_pins.eq(outputs)
        
        return m

if __name__ == "__main__":
    from amaranth.sim import *

    dut = TinyTapeoutTop()

    def tt04_ut(dut, direction):
        yield dut.io_in.eq(0x01)
        for _ in range(5):
            yield Tick()
            yield Settle()

        yield dut.io_in.eq(0x03)
        for _ in range(5):
            yield Tick()
            yield Settle()

        yield dut.io_in.eq(0x00)
        for _ in range(5):
            yield Tick()
            yield Settle()
        
        yield dut.io_in.eq(0x02)
        for _ in range(5):
            yield Tick()
            yield Settle()

    def proc():
        dut.pin_reset.eq(1)
        for _ in range(25):
            yield Tick()
            yield Settle()
        
        dut.pin_reset.eq(1)
        yield from tt04_ut(dut, 0)
        yield from tt04_ut(dut, 1)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("tt04.vcd", 'w'):
        sim.run()

    if False:
        with open("pwm.v", "w") as f:
            f.write(verilog.convert(dut, ports=[dut.encoder.a, dut.encoder.b, dut.pwm.output]))