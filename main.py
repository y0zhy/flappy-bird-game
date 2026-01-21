from pygame import *
from random import randint
import sounddevice as sd
import numpy as np
import threading

init()

# ================= AUDIO SETTINGS (VOICE CONTROL) =================
# Параметри для керування голосом:
THRESH = 0.03        # поріг гучності (0.02–0.06) - менше = чутливіше
IMPULSE = -18        # сила стрибка - менше число = більший стрибок
gravity = 1.2        # гравітація - більше = швидше падає

volume = 0.0         # поточна гучність

def audio_callback(indata, frames, time, status):
    """Обробка звуку з мікрофона в реальному часі"""
    global volume
    volume = np.sqrt(np.mean(indata**2))  # Обчислюємо RMS (громкість)

def start_audio():
    """Запуск потоку для читання звуку з мікрофона"""
    stream = sd.InputStream(
        channels=1,
        samplerate=44100,
        callback=audio_callback
    )
    stream.start()

# Запуск аудіопотоку на фоні
threading.Thread(target=start_audio, daemon=True).start()
# ====================================================================

window_size = 1200, 800
window = display.set_mode(window_size)
display.set_caption("Flappy Bird - Voice Control")
clock = time.Clock()

player_rect = Rect(150, window_size[1] // 2 - 100, 100, 100)

# Load bird animation frames
bird_frames = []
for i in range(4):
    frame = image.load(f"assets/flight/bird{i}.gif")
    frame = transform.scale(frame, (100, 100))
    frame.set_colorkey((255, 255, 255))
    bird_frames.append(frame)

# Load background animation frames
background_frames = []
for i in range(64):
    try:
        frame = image.load(f"assets/city/{i}.gif")
        frame = transform.scale(frame, window_size)
        background_frames.append(frame)
    except:
        break

# Load pipe images
pipe_image = None
try:
    pipe_image = image.load("assets/pipes/tube.png")
    pipe_image.set_colorkey((255, 255, 255))
except:
    pass

def generate_pipes(count):
    pipe_width = 180
    gap = 220
    pipes = []
    x = window_size[0]
    for _ in range(count):
        h = randint(100, 440)
        pipes.append(Rect(x, 0, pipe_width, h))
        pipes.append(Rect(x, h + gap, pipe_width, window_size[1]))
        x += 650
    return pipes

# Animation variables
current_frame = 0
anim_timer = 0

bg_frame = 0
bg_timer = 0

pipes = generate_pipes(150)

# Game vars
y_velocity = 0
lose = False
score = 0
font_big = font.Font(None, 100)
font_small = font.Font(None, 24)

start_time = time.get_ticks()

# Animation vars
current_frame = 0
anim_timer = 0

bg_frame = 0
bg_timer = 0

# ================= MAIN LOOP =================
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()

    if not lose:
        # ----- VOICE JUMP: стрибок коли мікрофон реєструє звук -----
        if volume > THRESH:
            y_velocity = IMPULSE

        y_velocity += gravity
        player_rect.y += y_velocity

    # Animation
    anim_timer += 1
    if anim_timer > 6:
        anim_timer = 0
        current_frame = (current_frame + 1) % len(bird_frames)

    bg_timer += 1
    if bg_timer > 8:
        bg_timer = 0
        bg_frame = (bg_frame + 1) % len(background_frames)

    # Draw background
    if background_frames:
        window.blit(background_frames[bg_frame], (0, 0))
    else:
        window.fill("skyblue")

    window.blit(bird_frames[current_frame], player_rect)

    # Pipes
    for p in pipes[:]:
        if not lose:
            p.x -= 10

        if pipe_image:
            img = transform.scale(pipe_image, (p.width, p.height))
            if p.y == 0:
                img = transform.flip(img, False, True)
            window.blit(img, p)
        else:
            draw.rect(window, "green", p)

        if p.x < -200:
            pipes.remove(p)
            score += 0.5

        if player_rect.colliderect(p):
            lose = True

    if len(pipes) < 10:
        pipes += generate_pipes(50)

    # Floor / ceiling
    if player_rect.y < 0 or player_rect.y > window_size[1] - player_rect.h:
        lose = True

    # UI
    score_text = font_big.render(str(int(score)), True, "red")
    window.blit(score_text, (window_size[0]//2 - 50, 40))

    vol_text = font_small.render(f"Mic: {volume:.3f}", True, (50,50,50))
    window.blit(vol_text, (20, window_size[1]-20))

    if lose:
        over = font_big.render("GAME OVER", True, "red")
        window.blit(over, over.get_rect(center=window.get_rect().center))

        if key.get_pressed()[K_r]:
            pipes = generate_pipes(150)
            player_rect.y = window_size[1]//2
            y_velocity = 0
            score = 0
            lose = False

    display.update()
    clock.tick(60)
