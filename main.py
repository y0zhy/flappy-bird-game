from pygame import *
from random import randint
init()

window_size = 1200 ,800
window = display.set_mode(window_size)
display.set_caption("Flappy Bird - Survival Game")
clock = time.Clock()
player_rect = Rect(150, window_size[1] // 2 - 100, 100, 100)

# Load bird animation frames
bird_frames = []
for i in range(4):
    frame = image.load(f"assets/flight/bird{i}.gif")  # Load from assets/flight/
    frame = transform.scale(frame, (100, 100))
    frame.set_colorkey((255, 255, 255))  # Make white background transparent
    bird_frames.append(frame)

# Load background animation frames
background_frames = []
for i in range(64):  # 0.gif to 63.gif
    try:
        frame = image.load(f"assets/city/{i}.gif")
        frame = transform.scale(frame, window_size)  # Scale to window size
        background_frames.append(frame)
    except:
        break  # Stop if a frame is missing

# Load pipe images
pipe_image = None
try:
    pipe_image = image.load("assets/pipes/tube.png")  # Try to load tube image
    pipe_image.set_colorkey((255, 255, 255))  # Make white background transparent
except:
    pass  # If no pipe image, will use green rectangles as fallback

# Animation variables
current_frame = 0
animation_timer = 0
animation_speed = 6  # Lower = faster animation

# Background animation variables
bg_current_frame = 0
bg_animation_timer = 0
bg_animation_speed = 8  # Background animation speed

# Rotation variable
bird_rotation = 0  # Current rotation angle

# Game over variables
game_over_timer = 0
auto_close_delay = 7 * 60  # 7 seconds in frames (60 FPS)
survival_time = 0
start_time = time.get_ticks()
game_should_exit = False  # Flag to indicate when to exit the game

# Fonts
pixel_font = font.Font(None, 72)  # Pixel-style font for Game Over
small_font = font.Font(None, 24)  # Small font for timer

def generate_pipes(count):
    pipe_width = 180  # Increased from 140
    gap = 220  # Decreased from 280
    min_height = 100
    max_height = 440
    distance = 650
    pipes = []
    start_x = window_size[0] 
    for i in range(count):
        height = randint(min_height, max_height)
        top_pipe = Rect(start_x, 0, pipe_width, height)
        bottom_pipe = Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
        pipes.extend([top_pipe, bottom_pipe])
        start_x += distance
    return pipes

pies = generate_pipes(150)
main_font = font.Font(None, 100)
score = 0
lose = False
y_velocity = 4
while True:
    for e in event.get():
        if e.type == QUIT:
            quit()
    
    # Track survival time
    if not lose:
        survival_time = (time.get_ticks() - start_time) / 1000  # Convert to seconds
    
    # Update bird animation
    animation_timer += 1
    if animation_timer >= animation_speed:
        animation_timer = 0
        current_frame = (current_frame + 1) % len(bird_frames)  # Cycle through frames
    
    # Update background animation
    bg_animation_timer += 1
    if bg_animation_timer >= bg_animation_speed:
        bg_animation_timer = 0
        bg_current_frame = (bg_current_frame + 1) % len(background_frames)  # Cycle through background frames
    
    # Update bird rotation based on key presses
    keys = key.get_pressed()
    if (keys[K_w] or keys[K_UP]) and not lose:
        bird_rotation = 45  # 45 degrees clockwise when W or UP is pressed
    elif (keys[K_s] or keys[K_DOWN]) and not lose:
        bird_rotation = 135  # 135 degrees clockwise when S or DOWN is pressed
    else:
        bird_rotation = 0  # Neutral position when no keys pressed
    
    # Get current animation frame and apply rotation
    current_bird_image = bird_frames[current_frame]
    if bird_rotation != 0:
        current_bird_image = transform.rotate(current_bird_image, bird_rotation)
    
    # Adjust position to keep bird centered after rotation
    bird_rect = current_bird_image.get_rect(center=player_rect.center)
    
    # Draw animated background
    if background_frames:
        window.blit(background_frames[bg_current_frame], (0, 0))
    else:
        window.fill("SkyBlue") # Fallback to solid color if no background frames
    
    window.blit(current_bird_image, bird_rect) # Draw the animated and rotated bird
    for pie in pies[:]:
        if not lose :
            pie.x -= 10
        
        # Draw pipe image or fallback to green rectangle
        if pipe_image:
            scaled_pipe = transform.scale(pipe_image, (pie.width, pie.height))
            # Flip top pipes upside down (pipes that start from y=0)
            if pie.y == 0:
                scaled_pipe = transform.flip(scaled_pipe, False, True)
            window.blit(scaled_pipe, pie)
        else:
            draw.rect(window, "Green", pie)
        
        if pie.x <= -100:
            pies.remove(pie)
            score += 0.5
        if player_rect.colliderect(pie):
            if not lose:  # Just collided
                lose = True
                game_over_timer = time.get_ticks()  # Start the timer
    if len(pies) < 8:
        pies += generate_pipes(150)
    
    # Display Game Over text immediately after collision
    if lose:
        game_over_text = pixel_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(window_size[0]//2, window_size[1]//2))
        window.blit(game_over_text, game_over_rect)
        
        # Auto-close after 7 seconds
        if time.get_ticks() - game_over_timer > auto_close_delay * 1000 / 60:  # Convert frames to ms
            print(f"Game Over! Survival time: {survival_time:.1f} seconds, Score: {int(score)} points")
            game_should_exit = True
    
    if game_should_exit:
        break  # Exit the main game loop
    
    score_text = main_font.render(f'{int(score)}', 1, "Red")
    center_text = window_size[0] // 2 - score_text.get_rect().w 
    window.blit(score_text, (center_text, 50))
    
    # Display timer in bottom left corner (small and almost invisible)
    timer_text = small_font.render(f'Time: {survival_time:.1f}s', True, (50, 50, 50))  # Dark gray, almost invisible
    timer_rect = timer_text.get_rect(bottomleft=(20, window_size[1] - 20))
    window.blit(timer_text, timer_rect)

    display.update()

    clock.tick(60)

    keys = key.get_pressed()

    # Handle movement keys (W/S and Up/Down arrows)
    if (keys[K_w] or keys[K_UP]) and not lose:
        player_rect.y -= 15
    if (keys[K_s] or keys[K_DOWN]) and not lose:
        player_rect.y += 15
    
    if keys[K_r] and lose:
        pies = generate_pipes(150)
        player_rect.y = window_size[1] // 2 - 100
        score = 0
        lose = False
        y_velocity = 2
        start_time = time.get_ticks()  # Reset survival timer
        survival_time = 0
    
    if player_rect.y >= window_size[1] - player_rect.h:
        lose = True
    
    if  lose:
        y_velocity *= 1.1
        if y_velocity > 30:  # Limit maximum fall speed
            y_velocity = 30
        player_rect.y += y_velocity
        if player_rect.y > window_size[1]:  # Prevent going too far below screen
            player_rect.y = window_size[1]

quit()    
    
    

