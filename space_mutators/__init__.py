def __init__(self, render=False):
    self.render_mode = render
    if self.render_mode:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        pygame.display.init()
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
