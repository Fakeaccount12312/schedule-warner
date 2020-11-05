import webuntis
import datetime
from gpiozero import LED
from sys import argv
from time import sleep

if argv[1] == "-stop":
    leds = {"green": LED(24), "yellow": LED(7), "red": LED(21)}
    exit()

session = webuntis.Session(
    server='nessa.webuntis.com',
    username='Wiet1059',
    password='(4Hasen)',
    school='Kopernikus+Gym#',
    useragent='Skript, das mich vor Unterrichtsausfällen warnt'
)

session.login()

student = session.students().filter(full_name="Stefan Wietschorke")[0]
date = datetime.date.today()
timetable = session.timetable(start=date, end=date, student=student)
timetable = sorted(timetable, key=lambda x: x.start)
normal_day = True

leds = {"green": LED(24), "yellow": LED(7), "red": LED(21)}
led_modes = {"green": 0, "yellow": 0, "red": 0}

if timetable:
    if all([lesson.code == "cancelled" for lesson in timetable]):
        session.logout()
        while True:
            leds["green"].on()
            sleep(0.5)
            leds["green"].off()
            leds["yellow"].on()
            sleep(0.5)
            leds["yellow"].off()
            leds["red"].on()
            sleep(0.5)
            leds["red"].off()
            leds["yellow"].on()
            sleep(0.5)
            leds["yellow"].off()
    else:
        if timetable[0].code == "cancelled":
            if timetable[1].code == "cancelled":
                # the first two hours are cancelled
                led_modes["green"] = 1
            else:
                # the first hour is cancelled
                led_modes["green"] = "blinking"
            normal_day = False
        if timetable[0].original_teachers or timetable[0].original_rooms or timetable[0].code == "irregular":
            # something in the first hour has changed
            led_modes["yellow"] = 1
            normal_day = False
        elif any([lesson.original_teachers or lesson.original_rooms or lesson.code for lesson in timetable]):
            # something has changed later that day
            led_modes["yellow"] = "blinking"
            normal_day = False
        if normal_day:
            # nothing unusual occurs
            led_modes["red"] = 1

    session.logout()

    for led in ("green", "yellow", "red"):
        if led_modes[led] == 1:
            leds[led].on()
        elif not led_modes[led]:
            leds[led].off()
    while True:
        for led in ("green", "yellow", "red"):
            if led_modes[led] == "blinking":
                leds[led].on()
        sleep(1)
        for led in ("green", "yellow", "red"):
            if led_modes[led] == "blinking":
                leds[led].off()
        sleep(1)

# print("\n".join(map(str, timetable)))
# for i in timetable:
#     print(i.subjects[0].name, "mit", i.teachers[0].fore_name, i.teachers[0].surname, "von", str(i.start.time())[:-3], "bis", str(i.end.time())[:-3], "in Raum", i.rooms[0].name, "entfällt" if i.code == "cancelled" else "\b", "wird vertreten" if i.original_teachers else "\b", "(Raumwechsel)" if i.original_rooms else "")
