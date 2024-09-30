import random
import time
import pvrecorder as pvr
import pygame as pg

for i, v in enumerate(pvr.PvRecorder.get_available_devices()):
    print(f'[{i}] {v}')

recorder = pvr.PvRecorder(device_index=-1, frame_length=1024)


pg.init()

run = True

WIDTH, HEIGHT = 583, 699
display = pg.display.set_mode((WIDTH, HEIGHT))

background = [0, 255, 0]

faces = [
    pg.image.load('assets/v0.png'),
    pg.image.load('assets/v1.png'),
    pg.image.load('assets/v2.png'),
    pg.image.load('assets/v3.png'),
    pg.image.load('assets/v4.png'),
    pg.image.load('assets/v5.png'),
]

eyes = [
    pg.image.load('assets/b0.png'),
    pg.image.load('assets/b1.png'),
    pg.image.load('assets/b2.png'),
    pg.image.load('assets/b3.png'),
]

recorder.start()

maximal = 4096
sensitivity = 0

eyes_stage = 0

volume = 1

avg_len = 50

while run:
    start_time = time.time()
    display.fill(background)
    for i in pg.event.get():
        if i.type == pg.KEYDOWN:
            if i.key == pg.K_ESCAPE:
                run = False
        if i.type == pg.QUIT:
            run = False
    emotion = 0
    data = recorder.read()

    plus_lengths = []

    minus_lengths = []

    last_is_minus = False
    is_recording_started = False
    current_wave = -1

    wave_len = 0

    minimal = 0
    maximum = 0

    for i in range(len(data)):
        data[i] *= volume
        compressed = data[i] / (maximal / (HEIGHT // 2))
        # pg.draw.line(display, [0, 0, 0], (i, compressed + HEIGHT // 2), (i, HEIGHT // 2))
        if data[i] > 0:
            if data[i] > maximum:
                maximum = data[i]
            if not is_recording_started and last_is_minus:
                is_recording_started = True
            if not is_recording_started:
                continue
            if last_is_minus:
                current_wave += 1
                plus_lengths.append(1)
            else:
                plus_lengths[current_wave] += 1
            last_is_minus = False

        if data[i] < 0:
            if data[i] < minimal:
                minimal = data[i]
            if is_recording_started:
                if not last_is_minus:
                    minus_lengths.append(1)
                else:
                    minus_lengths[current_wave] += 1
            last_is_minus = True

    if len(plus_lengths) >= 2 and len(minus_lengths) >= 2:
        if len(plus_lengths) > len(minus_lengths):
            plus_lengths.pop(-1)
        elif len(minus_lengths) > len(plus_lengths):
            minus_lengths.pop(-1)
        minus_lengths.pop(-1)
        plus_lengths.pop(-1)

        amplitude = maximum - minimal

        for i in range(len(minus_lengths)):
            wave_len += minus_lengths[i] + plus_lengths[i]

        wave_len /= len(minus_lengths)

        if wave_len > sensitivity:
            if wave_len < 30 or amplitude < 1000:
                emotion = 1 if amplitude < 1500 else 2
            elif wave_len > 200 or amplitude > 7000:
                emotion = 5
            else:
                emotion = 4
                if wave_len < 80:
                    emotion = 3
    if random.randint(0, 100) == 1 and eyes_stage == 0:
        eyes_stage += 1
    if eyes_stage != 0:
        eyes_stage += 1
        if eyes_stage == len(eyes):
            eyes_stage = 0

    display.blit(faces[emotion], [0, 0])
    display.blit(eyes[eyes_stage], [0, 0])
    pg.display.update()

pg.quit()
