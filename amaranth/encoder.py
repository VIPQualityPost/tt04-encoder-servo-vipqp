from amaranth import *

class ABEncoder(Elaboratable):
    def __init__(self):
        # Ports
        self.a = Signal(1, reset = 0)
        self.b = Signal(1, reset = 0)
        self.counter = Signal(8, reset = 127)

        # State
        self.a_prev = Signal()
        self.b_prev = Signal()
        self.rst = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.If(self.a != self.a_prev):
            with m.If(self.a == 0):
                with m.If(self.b == 1):
                    m.d.sync += [
                        self.counter.eq(self.counter - 1),
                        self.a_prev.eq(self.a)
                    ]
                with m.Else():
                    m.d.sync += [
                        self.counter.eq(self.counter + 1),
                        self.a_prev.eq(self.a)
                    ]
            with m.Else():
                with m.If(self.b == 1):
                    m.d.sync += [
                        self.counter.eq(self.counter + 1),
                        self.a_prev.eq(self.a)
                    ]
                with m.Else():
                    m.d.sync += [
                        self.counter.eq(self.counter - 1),
                        self.a_prev.eq(self.a)
                    ]
            
        with m.If(self.b != self.b_prev):
            with m.If(self.b == 0):
                with m.If(self.a == 1):
                    m.d.sync += [
                        self.counter.eq(self.counter + 1),
                        self.b_prev.eq(self.b)
                    ]
                with m.Else():
                    m.d.sync += [
                        self.counter.eq(self.counter - 1),
                        self.b_prev.eq(self.b)
                    ]
            with m.Else():
                with m.If(self.a == 1):
                    m.d.sync += [
                        self.counter.eq(self.counter - 1),
                        self.b_prev.eq(self.b)
                    ]
                with m.Else():
                    m.d.sync += [
                        self.counter.eq(self.counter + 1),
                        self.b_prev.eq(self.b)
                    ]
            
        return m

if __name__ == "__main__":
    from amaranth.sim import *
    from amaranth.back import verilog

    dut = ABEncoder()

    def encoder_ut(encoder, direction):
        for _ in range(5):
            yield encoder.a.eq(1)
            for _ in range(5):
                yield Tick()
                yield Settle()

            yield encoder.b.eq(direction == 0)
            for _ in range(5):
                yield Tick()
                yield Settle()

            yield encoder.a.eq(0)
            for _ in range(5):
                yield Tick()
                yield Settle()
            
            yield encoder.b.eq(direction == 1)
            for _ in range(5):
                yield Tick()
                yield Settle()
            
    def proc():
        dut.rst.eq(1)
        for _ in range(10):
            yield Tick()
            yield Settle()

        dut.rst.eq(0)
        yield from encoder_ut(dut, 0)
        yield from encoder_ut(dut, 1)

    sim = Simulator(dut)
    sim.add_clock(1e-6)
    sim.add_sync_process(proc)

    with sim.write_vcd("encoder.vcd", 'w'):
        sim.run()

    if False:
        with open("pwm.v", "w") as f:
            f.write(verilog.convert(dut, ports=[dut.a, dut.b, dut.counter]))