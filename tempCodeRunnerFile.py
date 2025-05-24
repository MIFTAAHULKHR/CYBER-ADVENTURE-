

import pygame, sys
from settings import *
from level import Level
# from popup_text import show_opening_popup # <-- IMPORT INI TIDAK DIPERLUKAN LAGI DI SINI

class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('CYBER ADVENTURE')
        self.clock = pygame.time.Clock()

        self.level = None

        try:
            self.start_bg = pygame.image.load('menu/menu_utama.png').convert()
            self.start_bg_rect = self.start_bg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        except pygame.error as e:
            print(f"Error loading start_bg: {e}")
            self.start_bg = None

        try:
            self.button_start = pygame.image.load('graphics/button/button_start.png').convert_alpha()
            self.button_start_pressed = pygame.image.load('graphics/button/button_start.png').convert_alpha() # Sebaiknya gambar berbeda untuk pressed
            self.button_start_rect = self.button_start.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))

            self.button_credits = pygame.image.load('graphics/button/button_credits.png').convert_alpha()
            self.button_credits_pressed = pygame.image.load('graphics/button/button_credits.png').convert_alpha() # Sebaiknya gambar berbeda
            self.button_credits_rect = self.button_credits.get_rect(center=(WIDTH // 2, HEIGHT // 2))

            self.button_exit = pygame.image.load('graphics/button/button_exit.png').convert_alpha()
            self.button_exit_pressed = pygame.image.load('graphics/button/button_exit.png').convert_alpha() # Sebaiknya gambar berbeda
            self.button_exit_rect = self.button_exit.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        except pygame.error as e:
            print(f"Error loading button images: {e}")
            # Set rect ke None jika gambar gagal dimuat untuk menghindari error di event loop
            self.button_start_rect = None
            self.button_credits_rect = None
            self.button_exit_rect = None


        pygame.mixer.init()
        try:
            self.background_sound = pygame.mixer.Sound('audio/early_sound.mp3')
            self.button_click_sound = pygame.mixer.Sound('audio/click_sound.ogg')
            self.main_game_sound = pygame.mixer.Sound('audio/early_sound.mp3') # Ganti nama agar lebih jelas
            self.main_game_sound.set_volume(0.3)
        except pygame.error as e:
            print(f"Error loading audio: {e}")
            self.background_sound = None
            self.button_click_sound = None
            self.main_game_sound = None


    def show_start_screen(self):
        if not self.start_bg:
            print("Start screen background not loaded, skipping start screen and proceeding to game.")
            return True # Langsung mulai game jika tidak ada start screen

        if hasattr(self, 'background_sound') and self.background_sound:
            self.background_sound.play(loops=-1)

        button_start_pressed_visual = False
        button_credits_pressed_visual = False
        button_exit_pressed_visual = False
        hovered_button = None

        start_screen_active = True
        while start_screen_active:
            self.screen.fill('black')
            if self.start_bg:
                self.screen.blit(self.start_bg, self.start_bg_rect)

            # Hanya blit tombol jika berhasil dimuat
            if hasattr(self, 'button_start') and self.button_start:
                current_start_img = self.button_start_pressed if button_start_pressed_visual and hasattr(self, 'button_start_pressed') else self.button_start
                self.screen.blit(current_start_img, self.button_start_rect)
            if hasattr(self, 'button_credits') and self.button_credits:
                current_credits_img = self.button_credits_pressed if button_credits_pressed_visual and hasattr(self, 'button_credits_pressed') else self.button_credits
                self.screen.blit(current_credits_img, self.button_credits_rect)
            if hasattr(self, 'button_exit') and self.button_exit:
                current_exit_img = self.button_exit_pressed if button_exit_pressed_visual and hasattr(self, 'button_exit_pressed') else self.button_exit
                self.screen.blit(current_exit_img, self.button_exit_rect)


            if hovered_button:
                rect_attr_name = f'button_{hovered_button}_rect'
                if hasattr(self, rect_attr_name) and getattr(self, rect_attr_name) is not None:
                    rect = getattr(self, rect_attr_name)
                    button_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    button_surf.fill((100, 100, 100, 100)) # Efek hover semi-transparan
                    self.screen.blit(button_surf, rect.topleft)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Reset visual press jika bukan mouse up
                if event.type != pygame.MOUSEBUTTONUP:
                    button_start_pressed_visual = False
                    button_credits_pressed_visual = False
                    button_exit_pressed_visual = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Tombol kiri mouse
                        if self.button_start_rect and self.button_start_rect.collidepoint(event.pos):
                            button_start_pressed_visual = True
                            if self.button_click_sound: self.button_click_sound.play()
                        elif self.button_credits_rect and self.button_credits_rect.collidepoint(event.pos):
                            button_credits_pressed_visual = True
                            if self.button_click_sound: self.button_click_sound.play()
                        elif self.button_exit_rect and self.button_exit_rect.collidepoint(event.pos):
                            button_exit_pressed_visual = True
                            if self.button_click_sound: self.button_click_sound.play()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Cek apakah visual press aktif sebelum melakukan aksi
                        if self.button_start_rect and self.button_start_rect.collidepoint(event.pos) and button_start_pressed_visual:
                            if self.background_sound: self.background_sound.stop()
                            start_screen_active = False
                            return True # Mulai game
                        elif self.button_credits_rect and self.button_credits_rect.collidepoint(event.pos) and button_credits_pressed_visual:
                            self.show_credits_screen()
                            # Tetap di start screen setelah credits
                        elif self.button_exit_rect and self.button_exit_rect.collidepoint(event.pos) and button_exit_pressed_visual:
                            pygame.quit()
                            sys.exit()
                        # Reset semua visual press setelah mouse up, di mana pun kliknya
                        button_start_pressed_visual = False
                        button_credits_pressed_visual = False
                        button_exit_pressed_visual = False

                if event.type == pygame.MOUSEMOTION:
                    hovered_button = None # Reset
                    if self.button_start_rect and self.button_start_rect.collidepoint(event.pos):
                        hovered_button = 'start'
                    elif self.button_credits_rect and self.button_credits_rect.collidepoint(event.pos):
                        hovered_button = 'credits'
                    elif self.button_exit_rect and self.button_exit_rect.collidepoint(event.pos):
                        hovered_button = 'exit'

            self.clock.tick(FPS)
        return False # Jika loop selesai tanpa menekan start (misal, menutup jendela)

    def show_credits_screen(self):
        credits_font = pygame.font.Font(UI_FONT, 30) # Sesuaikan ukuran font jika perlu
        credits_lines = [
            "Credits:",
            "Giovan Lado - 123140068",
            "Pradana Figo Ariansyah - 123140063",
            "Elfa Noviana Sari - 123140066",
            "Miftahul Khoiriyah - 123140064"
        ]
        active_loop = True
        background_credits = pygame.Surface(self.screen.get_size()).convert()
        background_credits.fill((30,30,30)) # Warna latar gelap

        # Gambar tombol kembali yang lebih jelas
        back_button_font = pygame.font.Font(UI_FONT, UI_FONT_SIZE + 6)
        back_text_render = back_button_font.render("BACK", True, TEXT_COLOR)
        back_button_padding = 20
        back_button_rect = back_text_render.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        back_button_rect_inflated = back_button_rect.inflate(back_button_padding, back_button_padding)


        while active_loop:
            self.screen.blit(background_credits, (0,0)) # Latar belakang credits

            line_height = 40 # Jarak antar baris
            start_y = (HEIGHT - (len(credits_lines) * line_height)) // 2 - 50 # Posisi Y awal

            for i, line in enumerate(credits_lines):
                credits_text = credits_font.render(line, True, TEXT_COLOR) # Warna teks terang
                credits_rect = credits_text.get_rect(center=(WIDTH // 2, start_y + i * line_height))
                self.screen.blit(credits_text, credits_rect)

            # Gambar tombol kembali
            pygame.draw.rect(self.screen, UI_BORDER_COLOR, back_button_rect_inflated, border_radius=5) # Kotak tombol
            pygame.draw.rect(self.screen, UI_BG_COLOR, back_button_rect_inflated.inflate(-6,-6), border_radius=5) # Isi tombol
            self.screen.blit(back_text_render, back_button_rect)


            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN: # Kembali dengan Esc atau Enter
                        active_loop = False
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and back_button_rect_inflated.collidepoint(event.pos):
                         if self.button_click_sound: self.button_click_sound.play()
                         active_loop = False
                         return
            self.clock.tick(FPS)


    def run(self):
        start_pressed = self.show_start_screen()

        if not start_pressed:
            print("Start screen was exited or failed to load. Exiting game.")
            pygame.quit()
            sys.exit()

        # --- PEMANGGILAN POPUP DIHAPUS DARI SINI ---
        # Tampilkan popup pembuka SETELAH tombol Start ditekan
        # show_opening_popup(self.screen) # <-- BARIS INI DIHAPUS/DIKOMENTARI

        # Mainkan suara game utama setelah popup selesai (sekarang akan dimainkan segera setelah start)
        if hasattr(self, 'main_game_sound') and self.main_game_sound:
            self.main_game_sound.play(loops=-1)

        self.level = Level()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        if self.level: self.level.toggle_menu()
                    # Tambahkan tombol escape untuk kembali ke menu utama atau keluar (opsional)
                    # if event.key == pygame.K_ESCAPE:
                    #     if self.level and (self.level.game_paused or self.level.game_won):
                    #          # Kembali ke menu utama atau logika lain
                    #          print("Escape pressed during pause/win screen - Implement return to menu")
                    #          # self.level = None # Hapus level
                    #          # self.run() # Mulai dari awal (akan memanggil show_start_screen lagi)
                    #          # return # atau keluar dari loop ini
                    #     elif self.level and not self.level.game_paused and not self.level.game_won:
                    #         self.level.toggle_menu() # Masuk ke menu pause jika di game

            self.screen.fill(WATER_COLOR)

            if self.level:
                self.level.run()
            else:
                # Ini seharusnya tidak terjadi jika start_pressed True
                font = pygame.font.Font(None, 50)
                text = font.render("Error: Level Gagal Dimuat!", True, (255,0,0))
                text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
                self.screen.blit(text, text_rect)

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()