import pygame
from settings import *
from entity import Entity
from support import * # Pastikan support.py memiliki import_folder

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player_callback, report_death_callback):
        super().__init__(groups)
        self.sprite_type = 'enemy'

        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15 # Kecepatan animasi default

        # Grafik harus diinisialisasi setelah self.animations
        self.animations = {'idle':[],'move':[],'attack':[]} 
        self.import_graphics(monster_name) 

        if self.animations[self.status] and len(self.animations[self.status]) > 0:
            self.image = self.animations[self.status][self.frame_index]
        else:
            print(f"[WARNING] No animation frames found for '{monster_name}' -> '{self.status}'. Using dummy Surface.")
            self.image = pygame.Surface((TILESIZE, TILESIZE)) # Gambar dummy jika animasi tidak ada
            self.image.fill('purple') # Warna mencolok untuk debug

        self.rect = self.image.get_rect(topleft=pos)
        # Inflate hitbox: (horizontal_inflation, vertical_inflation)
        # Nilai negatif membuatnya lebih kecil.
        self.hitbox = self.rect.inflate(0, HITBOX_OFFSET.get('enemy', -10)) # Ambil dari settings jika ada, atau default -10
        self.obstacle_sprites = obstacle_sprites

        self.monster_name = monster_name
        if monster_name in monster_data:
            monster_info = monster_data[self.monster_name]
            self.health = monster_info['health']
            self.exp_amount = monster_info['exp'] 
            self.speed = monster_info['speed']
            self.attack_damage = monster_info['damage']
            self.resistance = monster_info['resistance']
            self.attack_radius = monster_info['attack_radius']
            self.notice_radius = monster_info['notice_radius']
            self.attack_type = monster_info['attack_type']
            attack_sound_path = monster_info.get('attack_sound', 'audio/attack/slash.wav') # Default jika tidak ada
        else:
            # Default stats jika monster tidak ada di monster_data untuk mencegah crash
            print(f"CRITICAL WARNING: Monster '{monster_name}' not in monster_data. Using default stats.")
            self.health = 50
            self.exp_amount = 10
            self.speed = 2
            self.attack_damage = 5
            self.resistance = 1
            self.attack_radius = 50
            self.notice_radius = 200
            self.attack_type = 'slash'
            attack_sound_path = 'audio/attack/slash.wav'


        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 600
        self.damage_player = damage_player_callback 
        self.report_death = report_death_callback 

        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # sound
        try:
            self.death_sound = pygame.mixer.Sound('audio/death.wav')
            self.hit_sound = pygame.mixer.Sound('audio/hit.wav')
            self.attack_sound = pygame.mixer.Sound(attack_sound_path)
            self.death_sound.set_volume(0.4) # Sesuaikan volume
            self.hit_sound.set_volume(0.4)
            self.attack_sound.set_volume(0.4)
        except pygame.error as e:
            print(f"ERROR loading sound for {monster_name}: {e}")
            # Buat objek Sound dummy agar tidak crash jika sound gagal load
            self.death_sound = None 
            self.hit_sound = None
            self.attack_sound = None


    def import_graphics(self, name):
        # self.animations sudah diinisialisasi sebagai dict kosong di __init__
        main_path = f'graphics/monsters/{name}/'
        for animation_type in self.animations.keys(): # Iterasi keys yang sudah ada ('idle', 'move', 'attack')
            full_path = main_path + animation_type
            self.animations[animation_type] = import_folder(full_path)
            if not self.animations[animation_type]:
                 print(f"[WARNING] No frames found in: {full_path} for monster '{name}'")


    def get_player_distance_direction(self, player):
        if player is None: # Jika player belum ada atau None
            return float('inf'), pygame.math.Vector2() # Jarak tak hingga, arah nol

        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2() # Arah nol jika jaraknya nol
        return distance, direction

    def get_status(self, player):
        if player is None:
            self.status = 'idle'
            return

        distance, _ = self.get_player_distance_direction(player)

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack': # Untuk mereset animasi attack jika baru masuk state attack
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self, player):
        if player is None and self.status != 'idle':
            self.status = 'idle' # Jika player hilang, kembali idle
            self.direction = pygame.math.Vector2()
            return

        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage,self.attack_type)
            if self.attack_sound: self.attack_sound.play()
        elif self.status == 'move':
            if player: # Hanya bergerak jika player ada
                self.direction = self.get_player_distance_direction(player)[1]
            else: # Jika player tidak ada, berhenti
                self.direction = pygame.math.Vector2()
        else: # idle
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation_frames = self.animations.get(self.status) # Dapatkan list frames untuk status saat ini
        
        if not animation_frames: # Jika tidak ada frame untuk status ini (misalnya, path salah)
            # print(f"Warning: No animation frames for monster '{self.monster_name}' status '{self.status}'")
            # Biarkan self.image apa adanya (dummy surface atau frame sebelumnya)
            return 

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation_frames):
            if self.status == 'attack':
                self.can_attack = False # Hanya set False setelah animasi attack selesai
            self.frame_index = 0 # Loop animasi
        
        self.image = animation_frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center) # Update rect berdasarkan hitbox

        # Efek flicker saat vulnerable
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255) # Pastikan alpha kembali normal

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            if self.attack_time is None or current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if self.hit_time is None or current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            if self.hit_sound: self.hit_sound.play()
            if player: # Hanya jika player yang menyerang ada
                self.direction = self.get_player_distance_direction(player)[1]
                if attack_type == 'weapon':
                    self.health -= player.get_full_weapon_damage()
                else: # magic
                    self.health -= player.get_full_magic_damage() # Asumsi player punya method ini

            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill() 
            if self.death_sound: self.death_sound.play()
            self.report_death(self.monster_name, self.rect.center, self.exp_amount)

    def hit_reaction(self):
        if not self.vulnerable: # Musuh terpental ke belakang saat menerima damage
            self.direction *= -self.resistance 

    def update(self):
        self.hit_reaction() # Reaksi terhadap pukulan (jika vulnerable)
        self.move(self.speed) # Bergerak berdasarkan self.direction dan self.speed
        self.animate() # Update animasi
        self.cooldowns() # Cek cooldown serangan dan vulnerabilitas
        self.check_death() # Cek apakah musuh mati

    def enemy_update(self,player):
        self.get_status(player) # Tentukan status (idle, move, attack) berdasarkan player
        self.actions(player)    # Lakukan aksi berdasarkan status