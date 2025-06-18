import sys
import pygame

def darken_image(image, darkness=40):
    """Return a darkened copy of an image."""
    dark_img = pygame.Surface(image.get_size(), flags=pygame.SRCALPHA)
    dark_img.fill((0, 0, 0, darkness))  # RGBA overlay
    copy = image.copy()
    copy.blit(dark_img, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    return copy

def scale_down(image, scale=0.95):
    """Return a scaled-down version of an image."""
    w, h = image.get_size()
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.smoothscale(image, new_size)

def show_title_screen(screen):
    sw, sh = screen.get_width(), screen.get_height()

    # Load and scale background
    background = pygame.image.load("PUP Dash/assets/images/Background.png")
    background = pygame.transform.scale(background, (sw, sh))

    # Title
    title_img = pygame.image.load("PUP Dash/assets/Title UI/Title.png")
    title_img = pygame.transform.scale(title_img, (int(sw * 1), int(sh * 0.9)))
    title_rect = title_img.get_rect(center=(sw // 2, int(sh * 0.50)))

    # Start button
    start_img = pygame.image.load("PUP Dash/assets/Title UI/StartB.png").convert_alpha()
    start_img = pygame.transform.scale(start_img, (int(sw * 0.28), int(sh * 0.15)))
    start_hover = darken_image(start_img)
    start_pressed = scale_down(darken_image(start_img))
    
    start_rect = start_img.get_rect(center=(sw // 2, int(sh * 0.55)))

    # Quit button
    quit_img = pygame.image.load("PUP Dash/assets/Title UI/QuitB.png").convert_alpha()
    quit_img = pygame.transform.scale(quit_img, (int(sw * 0.18), int(sh * 0.10)))
    quit_hover = darken_image(quit_img)
    quit_pressed = scale_down(darken_image(quit_img))
    
    quit_rect = quit_img.get_rect(center=(sw // 2, int(sh * 0.70)))

    mouse_held = False

    while True:
        screen.blit(background, (0, 0))
        screen.blit(title_img, title_rect)

        mouse_pos = pygame.mouse.get_pos()

        # START button render
        if start_rect.collidepoint(mouse_pos):
            if mouse_held:
                pressed_rect = start_pressed.get_rect(center=start_rect.center)
                screen.blit(start_pressed, pressed_rect)
            else:
                screen.blit(start_hover, start_rect)
        else:
            screen.blit(start_img, start_rect)

        # QUIT button render
        if quit_rect.collidepoint(mouse_pos):
            if mouse_held:
                pressed_rect = quit_pressed.get_rect(center=quit_rect.center)
                screen.blit(quit_pressed, pressed_rect)
            else:
                screen.blit(quit_hover, quit_rect)
        else:
            screen.blit(quit_img, quit_rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_held = True

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                if start_rect.collidepoint(event.pos):
                    print("Start button clicked!")
                    return
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
