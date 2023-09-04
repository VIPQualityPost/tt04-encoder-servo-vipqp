from amaranth import *

class PWM(Elaboratable):
    def __init__(self):
        # Ports
        self.dutycycle = Signal(8, reset = 0)
        self.output = Signal(1)

        # State
        self.counter = Signal(8, reset = 0)

    def elaborate(self, platform):
        m = Module()

        dutycycle = self.dutycycle
        output = self.output
        counter = self.counter

        with m.If(counter < dutycycle):
            m.d.sync += [
                counter.eq(counter + 1),
                output.eq(1)
                ]
        with m.Else():
            m.d.sync += [
                counter.eq(counter + 1),
                output.eq(0)
                ]
        
        return m

if __name__ == "__main__":
    from amaranth.sim import *
    from amaranth.back import verilog

    dut = PWM()

    def pwm_ut(pwm, duty):
        yield pwm.dutycycle.eq(duty)
        for _ in range(255):
            yield Tick()
            yield Settle()

    def proc():
        for duty in range(255):
            yield from pwm_ut(dut, duty)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("pwm.vcd", 'w'):
        sim.run()

    if False:
        with open("pwm.v", "w") as f:
            f.write(verilog.convert(dut, ports=[dut.dutycycle, dut.output]))