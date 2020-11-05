#!/usr/bin/env python3

import arbitrage as a

i=a.Arbitrage('/dev/ttyACM1')

p=i.device

p.msg('*idn?')

p.apply_sine(freq=1250, amp=1.254, off=0.52)
#p.apply_square(freq=1250, amp=1.254, off=0.52)
#p.apply_ramp(freq=1250, amp=1.254, off=0.52)
#p.apply_noise(freq=1250, amp=1.254, off=0.52)
