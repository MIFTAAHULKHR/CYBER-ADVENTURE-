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
from popup_text import show_opening_popup, show_key

class Level:
    def __init__(self):
        # --- PINDAHKAN BARIS INI KE ATAS ---
        self.display_surface = pygame.display.get_surface() # 
        # --- BATAS PEMINDAHAN ---

        self.game_paused = False #
        self.game_won = False #

        self.opening_popup_shown = False #
        self.victory_message_shown = False #

        self.visible_sprites = YSortCameraGroup() #
        self.obstacle_sprites = pygame.sprite.Group() #

        self.current_attack = None #
        self.attack_sprites = pygame.sprite.Group() #
        self.attackable_sprites = pygame.sprite.Group() #

        try:
            self.key_image = pygame.image.load('graphics/items/key.png').convert_alpha() #
        except pygame.error as e:
            print(f"ERROR: Tidak dapat memuat gambar kunci: {e}") #
            self.key_image = pygame.Surface((32,32)); self.key_image.fill('magenta') #

        self.key_sprite = None 
        self.all_ransomware_defeated = False 

        self.winner_font = None
        self.winner_text_surface = None
        self.winner_text_rect = None

        try:
            font_path = UI_FONT if 'UI_FONT' in globals() else None
            # Pastikan WINNER_TEXT_FONT_SIZE ada di settings.py atau berikan nilai default di sini
            font_size = WINNER_TEXT_FONT_SIZE if 'WINNER_TEXT_FONT_SIZE' in globals() else 100
            self.winner_font = pygame.font.Font(font_path, font_size)
        except Exception as e:
            print(f"ERROR: Tidak dapat memuat font untuk layar kemenangan: {e}.") 
            self.winner_font = pygame.font.Font(None, 120) 

        # Pastikan WINNER_TEXT_COLOR ada di settings.py atau berikan nilai default
        winner_text_color = WINNER_TEXT_COLOR if 'WINNER_TEXT_COLOR' in globals() else 'yellow'
        self.winner_text_surface = self.winner_font.render('WINNER!', True, winner_text_color) 
        
        # SEKARANG self.display_surface sudah ada sebelum baris ini
        self.winner_text_rect = self.winner_text_surface.get_rect(center=(self.display_surface.get_width() / 2, self.display_surface.get_height() / 2)) 
        
        print("INFO: Setup teks kemenangan selesai.")
        
        self.ransomware_enemies_total = 0 #
        self.ransomware_enemies_killed = 0 #

        self.create_map() 

        self.ui = UI() #
        if hasattr(self, 'player') and self.player is not None:
            self.upgrade = Upgrade(self.player) #
        else:
            print("CRITICAL ERROR: Player tidak ada setelah create_map(). Upgrade menu tidak akan berfungsi.") #
            self.upgrade = None #

        self.animation_player = AnimationPlayer() #
        self.magic_player = MagicPlayer(self.animation_player) #


    def create_map(self): #
        layouts = {
            'boundary': import_csv_layout('map/map_FloorBlocks.csv'), #
            'object': import_csv_layout('map/map_Objects.csv'), #
            'entities': import_csv_layout('map/map_Entities.csv') #
        }
        graphics = {
            'objects': import_folder('graphics/objects') #
        }
        self.ransomware_enemies_total = 0 #
        player_created_in_map = False #

        for style,layout in layouts.items(): #
            for row_index,row in enumerate(layout): #
                for col_index, col in enumerate(row): #
                    if col != '-1': #
                        x = col_index * TILESIZE #
                        y = row_index * TILESIZE #
                        if style == 'boundary': #
                            Tile((x,y),[self.obstacle_sprites], 'invisible') #
                        elif style == 'object': #
                            surf_index = int(col) #
                            if 0 <= surf_index < len(graphics['objects']): #
                                surf = graphics['objects'][surf_index] #
                                Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf) #
                            else:
                                print(f"WARNING: Indeks objek {surf_index} di luar jangkauan untuk graphics['objects'] di map.") #
                        elif style == 'entities': #
                            if col == '0': # Player
                                if not player_created_in_map: #
                                    self.player = Player(
                                        (x, y), #
                                        [self.visible_sprites], #
                                        self.obstacle_sprites, #
                                        self.create_attack, #
                                        self.destroy_attack, #
                                        self.create_magic #
                                    )
                                    player_created_in_map = True #
                                    print("INFO: Player instance created from map.") #
                                else:
                                    print("WARNING: Multiple player entities ('0') found in map. Only the first one is used.") #
                            else: # Musuh
                                monster_name = '' #
                                if col == '1': monster_name = 'trojan' #
                                elif col == '2': monster_name = 'worm' #
                                elif col == '3': #
                                    monster_name = 'ransomware' #
                                    self.ransomware_enemies_total += 1 #

                                if monster_name: #
                                    if monster_name in monster_data: #
                                        Enemy(
                                            monster_name, #
                                            (x,y), #
                                            [self.visible_sprites, self.attackable_sprites], #
                                            self.obstacle_sprites, #
                                            self.damage_player, #
                                            self.handle_enemy_death #
                                        )
                                    else:
                                        print(f"WARNING: Monster '{monster_name}' (map code '{col}') not in monster_data. Skipping.") #
        
        if not player_created_in_map: #
            print("CRITICAL WARNING: Player ('0') not found in 'map_Entities.csv'. Game may not function correctly.") #

        print(f"Total ransomware enemies to defeat: {self.ransomware_enemies_total}") #

    def spawn_key(self, position):
        if self.key_image: #
            print(f"Spawning key at {position}") #
            key_topleft_x = position[0] - self.key_image.get_width() // 2 #
            key_topleft_y = position[1] - self.key_image.get_height() // 2 #
            # --- PERUBAHAN: Simpan referensi ke tile kunci ---
            self.key_sprite = Tile((key_topleft_x, key_topleft_y), [self.visible_sprites], 'item_key', self.key_image) #
        else:
            print("ERROR: Cannot spawn key, key_image not loaded.") #

    def handle_enemy_death(self, monster_name, position, exp_amount): #
        if hasattr(self, 'player') and self.player is not None: #
            self.add_exp(exp_amount) #
        else:
            print(f"WARNING: Player not available to receive EXP from {monster_name}.") #

        self.trigger_death_particles(position, monster_name) #
        print(f"Enemy died: {monster_name} at {position}, exp: {exp_amount}") #

        if monster_name == 'ransomware': #
            self.ransomware_enemies_killed += 1 #
            print(f"Ransomware killed. Count: {self.ransomware_enemies_killed}/{self.ransomware_enemies_total}") #
            if self.ransomware_enemies_total > 0 and self.ransomware_enemies_killed >= self.ransomware_enemies_total: #
                # --- PERUBAHAN: Jangan langsung set game_won ---
                if not self.all_ransomware_defeated : # Hanya spawn kunci sekali
                    print("All ransomware defeated! Spawning key.") #
                    self.spawn_key(position) #
                    self.all_ransomware_defeated = True
                    # self.game_won = True # HAPUS BARIS INI
                    # print("GAME WON!") # HAPUS BARIS INI

    # ... (method create_attack, create_magic, destroy_attack, player_attack_logic, damage_player, dll. tetap sama)
    def create_attack(self): #
        if hasattr(self, 'player') and self.player is not None: #
            self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites]) #
        else:
            print("Warning: create_attack called but player does not exist.") #

    def create_magic(self,style,strength,cost): #
        if hasattr(self, 'player') and self.player is not None: #
            if style == 'heal': #
                self.magic_player.heal(self.player,strength,cost,[self.visible_sprites]) #
            elif style == 'flame': #
                self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites]) #
        else:
            print("Warning: create_magic called but player does not exist.") #

    def destroy_attack(self): #
        if self.current_attack: #
            self.current_attack.kill() #
        self.current_attack = None #

    def player_attack_logic(self): #
        if not (hasattr(self, 'player') and self.player is not None): #
            return

        if self.attack_sprites: #
            for attack_sprite in self.attack_sprites: #
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False) #
                if collision_sprites: #
                    for target_sprite in collision_sprites: #
                        if hasattr(target_sprite, 'sprite_type') and target_sprite.sprite_type == 'enemy' and hasattr(target_sprite, 'get_damage'): #
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type) #

    def damage_player(self,amount,attack_type): #
        if hasattr(self, 'player') and self.player is not None and self.player.vulnerable: #
            self.player.health -= amount #
            self.player.vulnerable = False #
            self.player.hurt_time = pygame.time.get_ticks() #
            self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites]) #

    def trigger_death_particles(self,pos,particle_type): #
        self.animation_player.create_particles(particle_type,pos,self.visible_sprites) #

    def add_exp(self,amount): #
        if hasattr(self, 'player') and self.player is not None: #
            self.player.exp += amount #

    def toggle_menu(self): #
        if hasattr(self, 'player') and self.player is not None: 
            if not self.game_won: #
                self.game_paused = not self.game_paused #
                if self.game_paused: print("INFO: Game paused. Upgrade menu active.") #
                else: print("INFO: Game resumed.") #
        else:
            print("INFO: Cannot toggle menu, game/player not fully initialized or game won.") #


    def check_key_collection(self):
        if self.all_ransomware_defeated and self.key_sprite and hasattr(self.player, 'hitbox'):
            if self.player.hitbox.colliderect(self.key_sprite.hitbox):
                print("Key collected by player!")
                self.key_sprite.kill() # Hapus kunci dari layar
                self.key_sprite = None # Hapus referensi
                self.game_won = True # SEKARANG baru game won
                print("GAME WON!")
                # Tambahkan suara atau efek jika perlu

    def run(self): #
        if not hasattr(self, 'player') or self.player is None: #
            # Tampilkan pesan error jika player tidak ada
            self.display_surface.fill('black') #
            error_font = pygame.font.Font(None, 40) #
            error_lines = [ #
                "CRITICAL ERROR: PLAYER NOT FOUND!", #
                "Game cannot start without a player.", #
                "Check 'map_Entities.csv' for player ('0')." #
            ]
            for i, line in enumerate(error_lines): #
                error_surf = error_font.render(line, True, 'red') #
                error_rect = error_surf.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40 + i * 45)) #
                self.display_surface.blit(error_surf, error_rect) #
            return

        if not self.opening_popup_shown: #
            # Logika popup pembuka...
            self.display_surface.fill(WATER_COLOR if 'WATER_COLOR' in globals() else '#71ddee') #
            if hasattr(self, 'player') and self.player is not None: 
                 self.visible_sprites.custom_draw(self.player) #
            self.ui.display(self.display_surface, self.player) #
            pygame.display.update() #

            show_opening_popup(self.display_surface) #

            self.opening_popup_shown = True #
            pygame.event.clear() #
    
        if self.game_won:
            # Tampilkan layar kemenangan (latar belakang game + teks "WINNER!")
            if hasattr(self, 'player') and self.player is not None:
                 self.visible_sprites.custom_draw(self.player) #
            else:
                self.display_surface.fill(WATER_COLOR if 'WATER_COLOR' in globals() else '#71ddee') #

            if self.winner_text_surface and self.winner_text_rect:
                self.display_surface.blit(self.winner_text_surface, self.winner_text_rect) #
            else: 
                fb_font = pygame.font.Font(None, 70)
                fb_surf = fb_font.render('YOU WON!', True, 'yellow')
                fb_rect = fb_surf.get_rect(center=(WIDTH/2, HEIGHT/2))
                self.display_surface.blit(fb_surf, fb_rect)

        elif self.game_paused: 
            # Logika game dipause...
            self.visible_sprites.custom_draw(self.player) #
            self.ui.display(self.display_surface, self.player) #
            if hasattr(self, 'upgrade') and self.upgrade is not None: #
                self.upgrade.display(self.display_surface) #
            else: 
                pause_font = pygame.font.Font(UI_FONT if 'UI_FONT' in globals() else None, 50) #
                pause_surf = pause_font.render('PAUSED', True, TEXT_COLOR if 'TEXT_COLOR' in globals() else 'white') #
                pause_rect = pause_surf.get_rect(center=(WIDTH/2, HEIGHT/2)) #
                s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); s.fill((0,0,0,128)); self.display_surface.blit(s, (0,0)) #
                self.display_surface.blit(pause_surf, pause_rect) #
        else: # Game sedang berjalan normal
            self.visible_sprites.custom_draw(self.player) #
            self.visible_sprites.update() #
            self.visible_sprites.enemy_update(self.player) #
            self.player_attack_logic() 
            
            # --- PERUBAHAN: Cek pengambilan kunci ---
            if not self.game_won: # Hanya cek jika game belum dimenangkan
                self.check_key_collection()

            self.ui.display(self.display_surface, self.player) #

class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):  # Diperbaiki: __init__ bukan _init_
        super().__init__()  # Diperbaiki: __init__ bukan _init_

        # Setup tampilan layar
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_width() // 2
        self.half_height = self.display_surface.get_height() // 2
        self.offset = pygame.math.Vector2()

        # Zoom
        self.zoom = 1  # Zoom default (1 = normal)

        # Load lantai
        try:
            self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
            self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))
        except pygame.error as e:
            print(f"[ERROR] Gagal memuat 'ground.png': {e}")
            self.floor_surf = pygame.Surface((800, 600))
            self.floor_surf.fill((113, 221, 238))
            self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        if player is None:
            return

        # Hitung offset dari posisi player
        self.offset.x = player.rect.centerx - self.half_width / self.zoom
        self.offset.y = player.rect.centery - self.half_height / self.zoom

        # Batas offset agar kamera tidak keluar map
        map_width = self.floor_rect.width
        map_height = self.floor_rect.height

        max_offset_x = map_width - self.display_surface.get_width() / self.zoom
        max_offset_y = map_height - self.display_surface.get_height() / self.zoom

        self.offset.x = max(0, min(self.offset.x, max_offset_x))
        self.offset.y = max(0, min(self.offset.y, max_offset_y))

        # Gambar lantai
        floor_offset_pos = self.floor_rect.topleft - self.offset
        floor_scaled_size = (
            int(self.floor_surf.get_width() * self.zoom),
            int(self.floor_surf.get_height() * self.zoom)
        )
        scaled_floor = pygame.transform.scale(self.floor_surf, floor_scaled_size)
        scaled_floor_rect = scaled_floor.get_rect(topleft=(floor_offset_pos * self.zoom))
        self.display_surface.blit(scaled_floor, scaled_floor_rect)

        # Gambar semua sprite sesuai urutan Y
        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            scaled_image = pygame.transform.scale(sprite.image, (
                int(sprite.image.get_width() * self.zoom),
                int(sprite.image.get_height() * self.zoom)
            ))
            scaled_rect = scaled_image.get_rect(topleft=offset_pos * self.zoom)
            self.display_surface.blit(scaled_image, scaled_rect)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites()
                         if getattr(sprite, 'sprite_type', None) == 'enemy']
        for enemy in enemy_sprites:
            if hasattr(enemy, 'enemy_update'):
                enemy.enemy_update(player)