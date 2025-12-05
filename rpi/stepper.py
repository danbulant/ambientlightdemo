import RPi.GPIO as GPIO
import time
import atexit
from gdmath import wrap

class StepperMotor:
    pins = (17, 27, 22, 23)
    step_sleep = 0.01
    step_count = 200

    def __init__(self):
        GPIO.setmode( GPIO.BCM )
        for pin in self.pins:
            GPIO.setup( pin, GPIO.OUT )
        for pin in self.pins:
            GPIO.output( pin, GPIO.LOW )
        atexit.register(self.cleanup)

    def cleanup(self):
        for pin in self.pins:
            GPIO.output( pin, GPIO.LOW )
        GPIO.cleanup()

    def _set_pins(self, out1, out2, out3, out4):
        GPIO.output( self.pins[0], out1 )
        GPIO.output( self.pins[1], out2 )
        GPIO.output( self.pins[2], out3 )
        GPIO.output( self.pins[3], out4 )

    current_step = 0
    def _apply_single_step(self):
        current_step_abs = wrap(self.current_step, 0, 4)
        if current_step_abs%4==0:
            self._set_pins(GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        elif current_step_abs%4==1:
            self._set_pins(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW)
        elif current_step_abs%4==2:
            self._set_pins(GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW)
        elif current_step_abs%4==3:
            self._set_pins(GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW)
        time.sleep(self.step_sleep)
    def single_step(self):
        self.current_step += 1
        self._apply_single_step()
    def single_step_back(self):
        self.current_step -= 1
        self._apply_single_step()
    def step(self, steps):
        for _ in range(abs(steps)):
            if steps > 0:
                self.single_step()
            else:
                self.single_step_back()
    def pos(self):
        return self.current_step % self.step_count
    def fpos(self):
        return (self.current_step % self.step_count) / self.step_count
    
    def single_step_towards(self, target_pos):
        target_pos = target_pos % self.step_count
        current_pos = self.pos()
        if target_pos == current_pos:
            return
        # Determine shortest direction
        # includes wrap-around (it's a circular motion motor)
        diff = (target_pos - current_pos) % self.step_count
        if diff > self.step_count / 2:
            self.single_step_back()
        else:
            self.single_step()
    def angle_to_pos(self, angle):
        return int((angle % 360) / 360 * self.step_count)
    def fpos_to_pos(self, fpos):
        return int((fpos % 1) * self.step_count)
    
stepper = StepperMotor()
