import RPi.GPIO as GPIO
import time

class StepperMotor:
    pins = (17, 27, 22, 23)
    step_sleep = 0.002
    step_count = 200

    def __init__(self):
        GPIO.setmode( GPIO.BCM )
        for pin in self.pins:
            GPIO.setup( pin, GPIO.OUT )
            GPIO.output( pin, GPIO.LOW )

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
        if self.current_step%4==0:
            self._set_pins(GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.LOW)
        elif self.current_step%4==1:
            self._set_pins(GPIO.LOW, GPIO.HIGH, GPIO.LOW, GPIO.LOW)
        elif self.current_step%4==2:
            self._set_pins(GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.LOW)
        elif self.current_step%4==3:
            self._set_pins(GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.HIGH)
        time.sleep(self.step_sleep)
    def single_step(self):
        self._apply_single_step()
        self.current_step += 1
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