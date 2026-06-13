import RPi.GPIO as GPIO
import threading
import time
import sys


BUTTON_PIN = 14

leds = [4, 17, 18, 27, 22, 23, 24, 25, 7]
type_list = ["ladder", "snake", "ping_pong", "static", "reverse_blink", "blink"]
flags = ["time", "len", "type", "quantity"]


def init_GPIO():
    GPIO.setmode(GPIO.BCM)
    for pin in leds:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)


def ladder_LED(time_out: float, stop_event):
    init_GPIO()

    try:
        while not stop_event.is_set():
            for pin in leds:
                GPIO.output(pin, True)

                if stop_event.wait(time_out):
                    break

            for pin in reversed(leds):
                GPIO.output(pin, False)

                if stop_event.wait(time_out):
                    break

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()


def snake_LED(time_out: float, lens: int, stop_event):
    init_GPIO()

    try:
        for ind in range(lens):
            GPIO.output(leds[ind], True)

            if stop_event.wait(time_out):
                break

        ind = lens % len(leds)
        len_leds = len(leds)

        while not stop_event.is_set():
            GPIO.output(leds[ind], True)

            off_ind = (ind - lens) % len_leds
            GPIO.output(leds[off_ind], False)

            ind = (ind + 1) % len_leds

            if stop_event.wait(time_out):
                break

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()


def ping_pong_LED(time_out: float, lens: int, stop_event):
    init_GPIO()

    try:
        for ind in range(lens):
            GPIO.output(leds[ind], True)

        if stop_event.wait(time_out):
            return

        first_ind = lens
        len_leds = len(leds)
        last_ind = 0

        while not stop_event.is_set():

            while first_ind < len_leds:
                GPIO.output(leds[first_ind], True)
                GPIO.output(leds[last_ind], False)

                if stop_event.wait(time_out):
                    break

                first_ind += 1
                last_ind += 1

            first_ind -= 1
            last_ind -= 1

            while last_ind >= 0:
                GPIO.output(leds[first_ind], False)
                GPIO.output(leds[last_ind], True)

                if stop_event.wait(time_out):
                    break

                first_ind -= 1
                last_ind -= 1

            first_ind += 1
            last_ind += 1

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()


def static_LED(stop_event):
    init_GPIO()

    try:
        for pin in leds:
            GPIO.output(pin, True)

        stop_event.wait()

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()


def reverse_blink_LED(time_out: float, quantity: int, stop_event):
    init_GPIO()

    try:
        while not stop_event.is_set():

            for pin in leds:
                GPIO.output(pin, True)

            for pin in reversed(leds):

                for _ in range(quantity):
                    GPIO.output(pin, False)

                    if stop_event.wait(time_out):
                        break

                    GPIO.output(pin, True)

                    if stop_event.wait(time_out):
                        break

                if stop_event.is_set():
                    break

                GPIO.output(pin, False)

                if stop_event.wait(time_out):
                    break

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()


def blink_LED(time_out: float, quantity: int, stop_event):
    init_GPIO()

    try:
        while not stop_event.is_set():

            for pin in leds:
                GPIO.output(pin, False)

            for pin in leds:

                for _ in range(quantity):
                    GPIO.output(pin, True)

                    if stop_event.wait(time_out):
                        break

                    GPIO.output(pin, False)

                    if stop_event.wait(time_out):
                        break

                if stop_event.is_set():
                    break

                GPIO.output(pin, True)

                if stop_event.wait(time_out):
                    break

    except KeyboardInterrupt:
        pass

    finally:
        GPIO.cleanup()
    

def LED_logic(type_LED: str, time_out: float, lens: int, quantity: int, stop_event=None):
    if stop_event is None:
        stop_event = threading.Event()

    match type_LED:
        case "ladder":
            ladder_LED(time_out, stop_event)
        case "snake":
            snake_LED(time_out, lens, stop_event)
        case "ping_pong":
            ping_pong_LED(time_out, lens, stop_event)
        case "static":
            static_LED(stop_event)
        case "reverse_blink":
            reverse_blink_LED(time_out, quantity, stop_event)
        case "blink":
            blink_LED(time_out, quantity, stop_event)



def help_print():
    available_types = "[" + ", ".join(type_list) + "]"

    help_text = f"""
Options:
  -help          Show this help message
  -time <float>  Set timeout delay (default: 0.5)
  -len <int>     Set length (default: 1, max: {len(leds) - 1})
  -quantity <int>   Set number of flashes for blink modes (default: 5)
  -type <str>    Set LED type (default: ladder) \n\t\t{available_types}
"""
    print(help_text)


def check_ind(ind: int, argc: int, flg: str) -> bool:
    if(ind < argc): 
        return True
    else: 
        print(f"Error: the {flg} has no argument")
        return False


def main():
    argc = len(sys.argv)
    argv = sys.argv

    time_out = 0.5
    lens = 1
    type_LED = "ladder"
    current_mode = 0
    quantity = 5
    ind = 1 
    
    while ind < argc:
        match argv[ind]:
            case "-help":
                help_print()
                return 
            
            case "-time":
                if check_ind(ind + 1, argc, argv[ind]):
                    ind += 1
                    try:
                        time_out = float(argv[ind])
                    except ValueError:
                        print(f"Error: Value for {argv[ind-1]} must be a float number\n")
                        return
                else:
                    return

            case "-len":
                if check_ind(ind + 1, argc, argv[ind]):
                    ind += 1
                    try:
                        lens = int(argv[ind])
                    except ValueError:
                        print(f"Error: Value for {argv[ind-1]} must be an integer number\n")
                        return
                else:
                    return

            case "-type":
                if check_ind(ind + 1, argc, argv[ind]):
                    ind += 1
                    type_LED = argv[ind]
                    if not type_LED in type_list:
                        print(f"Error: Unknown LED type '{type_LED}'. Available types are: {type_list}")
                        return
                    
                    current_mode = type_list.index(type_LED)
                    
                else:
                    return
            
            case "-quantity":
                if check_ind(ind + 1, argc, argv[ind]):
                    ind += 1
                    try:
                        quantity = int(argv[ind])
                    except ValueError:
                        print(f"Error: Value for {argv[ind-1]} must be an integer number\n")
                        return
                else:
                    return
            
            case _:
                print(f"Error: Unknown parameter '{argv[ind]}'\n")
                help_print()
                return
        
        ind += 1


    if lens >= len(leds):
        print(f"Error: The specified length ({lens}) exceeds the number of available LED pins ({len(leds)}).")
        return
    
    print(f"Running with parameters: time_out={time_out}, lens={lens}, quantity={quantity}, type_LED='{type_LED}'")


    stop_event = threading.Event()

    animation_thread = threading.Thread(
        target=LED_logic,
        args=(type_LED, time_out, lens, quantity, stop_event)
    )

    animation_thread.start()

    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    last = GPIO.input(BUTTON_PIN)

    try:
        while True:
            state = GPIO.input(BUTTON_PIN)

            if last == 1 and state == 0:
                stop_event.set()
                animation_thread.join()

                current_mode = (current_mode + 1) % len(type_list)

                stop_event = threading.Event()
                animation_thread = threading.Thread(
                    target=LED_logic,
                    args=(type_list[current_mode], time_out, lens, quantity, stop_event)
                )

                animation_thread.start()
                GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)                

            last = state
            time.sleep(0.01)

        

    except KeyboardInterrupt:
        pass

    finally:
        stop_event.set()
        animation_thread.join()
        GPIO.cleanup()

    


if __name__ == "__main__":
    main()
