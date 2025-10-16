import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIN_DATA = 20
PIN_CLK = 21
PIN_LE = 22
PIN_OE1 = 23
PIN_OE2 = 24
PIN_OE3 = 25

PIN_SW1 = 26
PIN_SW2 = 27

GPIO.setup([PIN_DATA, PIN_CLK, PIN_LE, PIN_OE1, PIN_OE2, PIN_OE3], GPIO.OUT)
GPIO.setup([PIN_SW1, PIN_SW2], GPIO.IN)

GPIO.output([PIN_DATA, PIN_CLK, PIN_LE], GPIO.LOW)
GPIO.output([PIN_OE1, PIN_OE2, PIN_OE3], GPIO.HIGH)

CZERWONE_NS = [16, 30, 32, 47]
ZIELONE_NS = [18, 19, 28, 34, 35, 45]
ZOLTE_NS = [17, 29, 33, 46]
CZERWONE_WE = [0, 8]
ZIELONE_WE = [2, 3, 10, 11]
ZOLTE_WE = [1, 9]

PIESI_NS_CZERWONE = [4, 7, 12, 15]
PIESI_WE_CZERWONE = [20, 22, 24, 27, 36, 38, 41, 44]
PIESI_NS_ZIELONE = [5, 6, 13, 14]
PIESI_WE_ZIELONE = [21, 23, 25, 26, 37, 39, 42, 43]

pedestrian_request_SW1 = False
pedestrian_request_SW2 = False
MIN_GREEN_TIME = 5
EXTENDED_TIME_CHECK_INTERVAL = 0.5


def update_traffic_lights(data_bits):
    GPIO.output([PIN_OE1, PIN_OE2, PIN_OE3], GPIO.HIGH)

    for bit in data_bits:
        GPIO.output(PIN_DATA, GPIO.HIGH if bit == '1' else GPIO.LOW)
        GPIO.output(PIN_CLK, GPIO.HIGH)
        GPIO.output(PIN_CLK, GPIO.LOW)

    GPIO.output(PIN_LE, GPIO.HIGH)
    GPIO.output(PIN_LE, GPIO.LOW)

    GPIO.output([PIN_OE1, PIN_OE2, PIN_OE3], GPIO.LOW)


def create_48_bit_pattern(bits_to_set):
    pattern_list = ['0'] * 48
    for bit_number in bits_to_set:
        if 0 <= bit_number <= 47:
            index = 47 - bit_number
            pattern_list[index] = '1'
    return "".join(pattern_list)


def controlled_green(green_bits, red_bits_other, sw_request_flag, phase_name, extended_time=5):
    global pedestrian_request_SW1, pedestrian_request_SW2

    print(f"FAZA: {phase_name} (min {MIN_GREEN_TIME}s)")
    bits = green_bits + red_bits_other + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
    update_traffic_lights(create_48_bit_pattern(bits))

    sleep(MIN_GREEN_TIME)

    elapsed_time = 0
    while elapsed_time < extended_time:
        if GPIO.input(PIN_SW1) == GPIO.HIGH and sw_request_flag == 'SW1':
            pedestrian_request_SW1 = True
            print("SW1")
            break
        if GPIO.input(PIN_SW2) == GPIO.HIGH and sw_request_flag == 'SW2':
            pedestrian_request_SW2 = True
            print("SW2")
            break

        sleep(EXTENDED_TIME_CHECK_INTERVAL)
        elapsed_time += EXTENDED_TIME_CHECK_INTERVAL


def traffic_cycle_with_pedestrians():
    global pedestrian_request_SW1, pedestrian_request_SW2

    # FAZA A: RUCH PÓŁNOC/POŁUDNIE (N-S)
    car_bits_A = ZIELONE_NS + CZERWONE_WE
    ped_bits_A = PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
    update_traffic_lights(create_48_bit_pattern(car_bits_A + ped_bits_A))

    controlled_green(ZIELONE_NS, CZERWONE_WE, 'SW1', "N-S ZIELONE / W-E CZERWONE", extended_time=5)

    # ZMIANA FAZY N-S
    if pedestrian_request_SW1:
        print("PRZEJŚCIE DO ŻÓŁTEGO N-S: Aktywowano żądanie SW1.")

        bits = ZOLTE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(2)

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_ZIELONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(5)
        pedestrian_request_SW1 = False

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)

    else:
        print("PRZEJŚCIE DO ŻÓŁTEGO N-S: Standardowy cykl.")
        bits = ZOLTE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(2)

        print("WSZYSTKIE CZERWONE (Samochody).")
        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)

    # FAZA B: RUCH WSCHÓD/ZACHÓD (W-E)
    car_bits_B = CZERWONE_NS + ZIELONE_WE
    ped_bits_B = PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
    update_traffic_lights(create_48_bit_pattern(car_bits_B + ped_bits_B))

    controlled_green(ZIELONE_WE, CZERWONE_NS, 'SW2', "W-E ZIELONE / N-S CZERWONE", extended_time=5)

    # ZMIANA FAZY W-E
    if pedestrian_request_SW2:
        print("PRZEJŚCIE DO ŻÓŁTEGO W-E: Aktywowano żądanie SW2.")

        bits = ZOLTE_WE + CZERWONE_NS + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(2)

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_ZIELONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(5)
        pedestrian_request_SW2 = False

        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)

    else:
        print("PRZEJŚCIE DO ŻÓŁTEGO W-E: Standardowy cykl.")
        bits = ZOLTE_WE + CZERWONE_NS + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(2)

        print("WSZYSTKIE CZERWONE (Samochody).")
        bits = CZERWONE_NS + CZERWONE_WE + PIESI_NS_CZERWONE + PIESI_WE_CZERWONE
        update_traffic_lights(create_48_bit_pattern(bits))
        sleep(1)


try:
    print("START SYGNALIZACJI ŚWIETLNEJ (Ctrl+C, aby zakończyć)")
    while True:
        traffic_cycle_with_pedestrians()

except KeyboardInterrupt:
    print("Program zakończony przez użytkownika.")

finally:
    GPIO.output([PIN_OE1, PIN_OE2, PIN_OE3], GPIO.HIGH)
    GPIO.cleanup()
    print("Piny GPIO przywrócone do domyślnej konfiguracji.")
