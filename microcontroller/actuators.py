from l293d import L293D


def drive_motor(data):
    necessary_data = ['__class', 'duty', "change_direction"]

    motor, duty, cd = [data.get(k) for k in necessary_data]
    
    try:
        motor.set_speed(
            pair=motor.get_pair(),
            duty=int(duty),
            change_direction=bool(cd)
        )
    except Exception as e:
        return str(e)


def init_all_actuators():
    # id, name, f, input_for_f
    LIST = []

    # append actuator Motor with B Path
    LIST.append(
        ["Motor_B", drive_motor, {"__class": L293D("B"), "duty": 0, "change_direction": False}]
    )

    return LIST
