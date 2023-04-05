from machine import Pin, PWM


class L293D:
    frequency = 1000

    MOTOR_index = {"left": 0, "right": 1, "enable": 2}
    MOTOR_PAIR_A = {"left": 0, "right": 2, "enable": 4}
    MOTOR_PAIR_B = {"left": 33, "right": 32, "enable": 25}

    MIN_DUTY = 21

    def __init__(self, active_pair=""):
        """
        # https://docs.micropython.org/en/latest/esp32/quickref.html#pwm-pulse-width-modulation
        
        PWM can be enabled on all output-enabled pins. The base frequency can range
        from 1Hz to 40MHz but there is a tradeoff; as the base frequency increases the
        duty resolution decreases.
        Currently the duty cycle has to be in the range of 0-1023 which corresponds
        to 0-100 percent duty cycle.
        """

        self._set_pins()
        self.status = {"pair": active_pair, "direction": "left"}  # start pair and direction
        self.DUTY_CYCLE = 0
        
        if not active_pair:
            if active_pair == "B":
                self.B_PIN[self.MOTOR_index.get("enable")].on()  # activate MOTOR_PAIR_B
            if active_pair == "A":
                self.A_PIN[self.MOTOR_index.get("enable")].on()  # activate MOTOR_PAIR_A
        else:
            self.A_PIN[self.MOTOR_index.get("enable")].on()  # activate MOTOR_PAIR_A
            self.B_PIN[self.MOTOR_index.get("enable")].on()  # activate MOTOR_PAIR_B

    def _set_pins(self):
        # Pin Decleration and set all Pins to duty: 0/LOW
        freq = self.frequency

        # MOTOR_PAIR_A
        A1 = PWM(Pin(self.MOTOR_PAIR_A.get("left")), freq=freq, duty=0)
        A2 = PWM(Pin(self.MOTOR_PAIR_A.get("right")), freq=freq, duty=0)
        EN1_2 = Pin(self.MOTOR_PAIR_A.get("enable"), Pin.OUT)
        EN1_2.off()

        self.A_PIN = [A1, A2, EN1_2]

        # MOTOR_PAIR_B

        B3 = PWM(Pin(self.MOTOR_PAIR_B.get("left")), freq=freq, duty=0)
        B4 = PWM(Pin(self.MOTOR_PAIR_B.get("right")), freq=freq, duty=0)
        EN3_4 = Pin(self.MOTOR_PAIR_B.get("enable"), Pin.OUT)
        EN3_4.off()

        self.B_PIN = [B3, B4, EN3_4]

    def set_speed(self, pair, duty, change_direction=False):
        self._check_pair_defined(pair)
        self.status["pair"] = pair

        if duty > self.MIN_DUTY or duty == 0:
            self.DUTY_CYCLE = int(duty)
        else:
            self.DUTY_CYCLE = 0
            print("Not allowed duty")

        if change_direction:
            # ramp down direction to zero
            self._change_duty_same_direction(pair, 0)

            # change direction flag and ramp up
            self._change_direction()

        self._change_duty_same_direction(pair, duty)

    def get_duty_direction_of_pair(self):
        return self.status.get("pair"), self.DUTY_CYCLE, self.status["direction"]

    def get_pair(self):
        return self.status.get("pair")

    def _change_direction(self):
        if self.status["direction"] == "left":
            self.status["direction"] = "right"
        else:
            self.status["direction"] = "left"

    def _change_duty_same_direction(self, pair, duty):
        value = self._convert_value(duty)
        direction = self.status["direction"]

        if self.status.get("pair") == "B":
            self.B_PIN[self.MOTOR_index.get(direction)].duty(value)
        else:
            self.A_PIN[self.MOTOR_index.get(direction)].duty(value)

    def _check_pair_defined(self, pair):
        # check if defined if not set one
        check = bool(self.status.get("pair"))

        if not check:
            self.status["pair"] = "A" if pair == "A" else "B"

    def _convert_value(self, duty):
        return int((duty * 2 ** 10) / 100)
    

