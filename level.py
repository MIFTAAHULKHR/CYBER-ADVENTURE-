import pygame
from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from popup_text import show_opening_popup 

class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False
        self.game_won = False

        self.opening_popup_shown = False

        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        try:
            self.key_image = pygame.image.load('graphics/items/key.png').convert_alpha()
        except pygame.error as e:
            print(f"ERROR: Tidak dapat memuat gambar kunci: {e}")
            self.key_image = pygame.Surface((32,32)); self.key_image.fill('magenta')

        try:
            self.winner_background_img = pygame.image.load('menu/winner_background.png').convert()
            self.winner_background_img = pygame.transform.scale(
                self.winner_background_img,
                (self.display_surface.get_width(), self.display_surface.get_height())
            )
            self.winner_background_rect = self.winner_background_img.get_rect(topleft=(0, 0))
            print("INFO: Gambar latar kemenangan berhasil dimuat.")
        except pygame.error as e:
            print(f"ERROR: Tidak dapat memuat gambar latar kemenangan: {e}. Menggunakan fallback teks.")
            self.winner_background_img = None
            try:
                self.win_font = pygame.font.Font(UI_FONT, WIN_FONT_SIZE)
            except Exception as font_e: 
                print(f"ERROR: Tidak dapat memuat font untuk kemenangan: {font_e}")
                self.win_font = pygame.font.Font(None, 72) # Font default Pygame

            win_text_color = TEXT_COLOR_WIN if 'TEXT_COLOR_WIN' in globals() else 'gold'
            self.win_text_surface = self.win_font.render('WINNER!!!', True, win_text_color)
            self.win_text_rect = self.win_text_surface.get_rect(center=(self.display_surface.get_width() / 2, self.display_surface.get_height() / 2))

        self.ransomware_enemies_total = 0
        self.ransomware_enemies_killed = 0

        self.create_map()

        self.ui = UI()
        if hasattr(self, 'player') and self.player is not None:
            self.upgrade = Upgrade(self.player)
        else:
            print("CRITICAL ERROR: Player tidak ada setelah create_map(). Upgrade menu tidak akan berfungsi.")
            self.upgrade = None 

        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'),
            'object': import_csv_layout('map/map_Objects.csv'),
            'entities': import_csv_layout('map/map_Entities.csv')
        }
        graphics = {
            'objects': import_folder('graphics/objects')
        }
        self.ransomware_enemies_total = 0
        player_created_in_map = False

        for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites], 'invisible')
                        elif style == 'object':
                            surf_index = int(col)
                            if 0 <= surf_index < len(graphics['objects']):
                                surf = graphics['objects'][surf_index]
                                Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)
                            else:
                                print(f"WARNING: Indeks objek {surf_index} di luar jangkauan untuk graphics['objects'] di map.")
                        elif style == 'entities':
                            if col == '0':
                                if not player_created_in_map:
                                    self.player = Player(
                                        (x, y),
                                        [self.visible_sprites],
                                        self.obstacle_sprites,
                                        self.create_attack,
                                        self.destroy_attack,
                                        self.create_magic
                                    )
                                    player_created_in_map = True
                                    print("INFO: Player instance created from map.")
                                else:
                                    print("WARNING: Multiple player entities ('0') found in map. Only the first one is used.")
                            else:
                                monster_name = ''
                                if col == '1': monster_name = 'trojan'
                                elif col == '2': monster_name = 'worm'
                                elif col == '3':
                                    monster_name = 'ransomware'
                                    self.ransomware_enemies_total += 1

                                if monster_name:
                                    if monster_name in monster_data:
                                        Enemy(
                                            monster_name,
                                            (x,y),
                                            [self.visible_sprites, self.attackable_sprites],
                                            self.obstacle_sprites,
                                            self.damage_player,
                                            self.handle_enemy_death
                                        )
                                    else:
                                        print(f"WARNING: Monster '{monster_name}' (map code '{col}') not in monster_data. Skipping.")
        
        if not player_created_in_map:
            print("CRITICAL WARNING: Player ('0') not found in 'map_Entities.csv'. Game may not function correctly.")
            # Pertimbangkan untuk tidak melanjutkan jika player tidak ada, atau membuat player default
            # self.player = Player((WIDTH/2, HEIGHT/2), [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack, self.create_magic) # Player default jika tidak ada di map

        print(f"Total ransomware enemies to defeat: {self.ransomware_enemies_total}")

    def spawn_key(self, position):
        if self.key_image:
            print(f"Spawning key at {position}")
            # Position adalah center dari enemy, jadi sesuaikan untuk topleft Tile
            key_topleft_x = position[0] - self.key_image.get_width() // 2
            key_topleft_y = position[1] - self.key_image.get_height() // 2
            Tile((key_topleft_x, key_topleft_y), [self.visible_sprites], 'item_key', self.key_image)
        else:
            print("ERROR: Cannot spawn key, key_image not loaded.")

    def handle_enemy_death(self, monster_name, position, exp_amount):
        if hasattr(self, 'player') and self.player is not None:
            self.add_exp(exp_amount)
        else:
            print(f"WARNING: Player not available to receive EXP from {monster_name}.")

        self.trigger_death_particles(position, monster_name)
        print(f"Enemy died: {monster_name} at {position}, exp: {exp_amount}")

        if monster_name == 'ransomware':
            self.ransomware_enemies_killed += 1
            print(f"Ransomware killed. Count: {self.ransomware_enemies_killed}/{self.ransomware_enemies_total}")
            if self.ransomware_enemies_total > 0 and self.ransomware_enemies_killed >= self.ransomware_enemies_total:
                if not self.game_won:
                    print("All ransomware defeated! Spawning key.")
                    self.spawn_key(position)
                    self.game_won = True
                    print("GAME WON!")
                    # Anda bisa menghentikan musik game utama dan memainkan musik kemenangan di sini

    def create_attack(self):
        if hasattr(self, 'player') and self.player is not None:
            self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])
        else:
            print("Warning: create_attack called but player does not exist.")

    def create_magic(self,style,strength,cost):
        if hasattr(self, 'player') and self.player is not None:
            if style == 'heal':
                self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])
            elif style == 'flame':
                self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])
        else:
            print("Warning: create_magic called but player does not exist.")

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if not (hasattr(self, 'player') and self.player is not None):
            return

        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if hasattr(target_sprite, 'sprite_type') and target_sprite.sprite_type == 'enemy' and hasattr(target_sprite, 'get_damage'):
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type)

    def damage_player(self,amount,attack_type):
        if hasattr(self, 'player') and self.player is not None and self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

    def trigger_death_particles(self,pos,particle_type):
        self.animation_player.create_particles(particle_type,pos,self.visible_sprites)

    def add_exp(self,amount):
        if hasattr(self, 'player') and self.player is not None:
            self.player.exp += amount
        # else:
            # print("Warning: Attempted to add EXP, but player does not exist.") # Sudah dicek di handle_enemy_death

    def toggle_menu(self):
        if hasattr(self, 'player') and self.player is not None: # Hanya toggle jika player ada dan game berjalan
            if not self.game_won: # Jangan izinkan pause jika game sudah dimenangkan
                self.game_paused = not self.game_paused
                if self.game_paused: print("INFO: Game paused. Upgrade menu active.")
                else: print("INFO: Game resumed.")
        else:
            print("INFO: Cannot toggle menu, game/player not fully initialized or game won.")

    def run(self):
        if not hasattr(self, 'player') or self.player is None:
            self.display_surface.fill('black')
            error_font = pygame.font.Font(None, 40)
            error_lines = [
                "CRITICAL ERROR: PLAYER NOT FOUND!",
                "Game cannot start without a player.",
                "Check 'map_Entities.csv' for player ('0')."
            ]
            for i, line in enumerate(error_lines):
                error_surf = error_font.render(line, True, 'red')
                error_rect = error_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40 + i * 45))
                self.display_surface.blit(error_surf, error_rect)
            return

        # --- AWAL PERUBAHAN: Logika untuk menampilkan popup pembuka ---
        if not self.opening_popup_shown:
            # 1. Gambar frame pertama dari level
            self.display_surface.fill(WATER_COLOR if 'WATER_COLOR' in globals() else '#71ddee')
            self.visible_sprites.custom_draw(self.player)
            self.ui.display(self.display_surface, self.player)
            pygame.display.update()

            # 2. Tampilkan popup
            show_opening_popup(self.display_surface)

            # 3. Set flag
            self.opening_popup_shown = True
            pygame.event.clear() # Bersihkan event agar input penutup popup tidak memicu aksi game
    

        # Logika utama game setelah popup (jika ada) selesai
        if self.game_won:
            if self.winner_background_img:
                self.display_surface.blit(self.winner_background_img, self.winner_background_rect)
            elif hasattr(self, 'win_text_surface'):
                self.display_surface.fill(UI_BG_COLOR if 'UI_BG_COLOR' in globals() else 'black')
                self.display_surface.blit(self.win_text_surface, self.win_text_rect)
            else: # Fallback paling akhir
                self.display_surface.fill('black'); font = pygame.font.Font(None, 70); surf = font.render('YOU WON!', True, 'yellow'); rect = surf.get_rect(center=(WIDTH/2, HEIGHT/2)); self.display_surface.blit(surf, rect)

        elif self.game_paused:
            self.visible_sprites.custom_draw(self.player) # Tetap gambar game di belakang
            self.ui.display(self.display_surface, self.player) # Tampilkan UI
            if hasattr(self, 'upgrade') and self.upgrade is not None:
                self.upgrade.display(self.display_surface)
            else: # Jika upgrade tidak ada (misal player gagal dibuat)
                pause_font = pygame.font.Font(UI_FONT if 'UI_FONT' in globals() else None, 50)
                pause_surf = pause_font.render('PAUSED', True, TEXT_COLOR if 'TEXT_COLOR' in globals() else 'white')
                pause_rect = pause_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,128)); self.display_surface.blit(s, (0,0))
                self.display_surface.blit(pause_surf, pause_rect)
        else: # Game sedang berjalan normal
            self.visible_sprites.custom_draw(self.player)
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()
            self.ui.display(self.display_surface, self.player)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        if self.display_surface is None:
            print("CRITICAL ERROR: YSortCameraGroup display_surface is None at init.")
            return

        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        try:
            self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
            self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
        except pygame.error as e:
            print(f"ERROR: Could not load ground.png for YSortCameraGroup: {e}")
            self.floor_surf = pygame.Surface(self.display_surface.get_size()).convert() # Dummy surface seukuran layar
            self.floor_surf.fill(WATER_COLOR if 'WATER_COLOR' in globals() else '#71ddee') # Isi dengan warna default
            self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

    def custom_draw(self,player):
        if self.display_surface is None: return
        if player is None : # Jika player tidak ada, gambar lantai saja tanpa offset
            if self.floor_surf: self.display_surface.blit(self.floor_surf, (0,0))
            return

        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        if self.floor_surf:
            floor_offset_pos = self.floor_rect.topleft - self.offset
            self.display_surface.blit(self.floor_surf,floor_offset_pos)
        # else: # Jika floor_surf gagal load dan tidak ada dummy, isi dengan warna
            # self.display_surface.fill(WATER_COLOR if 'WATER_COLOR' in globals() else '#71ddee')

        try:
            # Filter sprite yang punya rect dan image sebelum sorting dan drawing
            valid_sprites = [s for s in self.sprites() if hasattr(s, 'rect') and hasattr(s, 'image') and s.image is not None]
            sorted_sprites = sorted(valid_sprites,key = lambda sprite: sprite.rect.centery)
            for sprite in sorted_sprites:
                offset_pos = sprite.rect.topleft - self.offset
                self.display_surface.blit(sprite.image,offset_pos)
        except AttributeError as e:
            print(f"WARNING: AttributeError during YSortCameraGroup custom_draw. Skipping a sprite. Details: {e}")
        except Exception as e: # Tangkap error lain yang mungkin terjadi
            print(f"UNEXPECTED ERROR in YSortCameraGroup.custom_draw: {e}")

    def enemy_update(self,player):
        if player is None: return

        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy' and hasattr(sprite, 'enemy_update')]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)