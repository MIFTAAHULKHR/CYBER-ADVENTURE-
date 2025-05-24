import pygame

class Message:
    def __init__(self, messages, display_surface):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.display_surface = display_surface

        # Set up other variables
        self.font = pygame.font.Font('freesansbold.ttf', 24)
        self.timer = pygame.time.Clock()
        self.messages = messages
        self.snip = self.font.render('', True, 'white')
        self.counter = 0
        self.speed = 3
        self.active_message = 0
        self.message = self.messages[self.active_message]
        self.done = False
        self.running = True
        self.split_screen = True

        # Transition variables
        self.alpha = 0
        self.transitioning_in = True
        self.transitioning_out = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.done:
                    if self.active_message < len(self.messages) - 1:
                        self.active_message += 1
                        self.message = self.messages[self.active_message]
                        self.counter = 0
                        self.done = False
                    else:
                        self.transitioning_out = True

    def update(self):
        if self.counter < self.speed * len(self.message):
            self.counter += 1
        elif self.counter >= self.speed * len(self.message):
            self.done = True

        # Handle transitions
        if self.transitioning_in:
            self.alpha += 3
            if self.alpha >= 255:
                self.alpha = 255
                self.transitioning_in = False
        elif self.transitioning_out:
            self.alpha -= 3
            if self.alpha <= 0:
                self.alpha = 0
                self.running = False

    def render(self):
        # Create a semi-transparent surface for the split-screen effect
        if self.split_screen:
            split_surface = pygame.Surface((1280, 220))
            split_surface.set_alpha(self.alpha)
            split_surface.fill((0, 0, 0))
            self.display_surface.blit(split_surface, (0, 500))

            self.snip = self.font.render(self.message[0:self.counter // self.speed], True, 'white')
            split_surface.blit(self.snip, (10, 10))

            self.display_surface.blit(split_surface, (0, 500))

    def run(self):
        while self.running:
            self.timer.tick(60)
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()