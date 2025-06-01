import pygame
from support import import_folder
from random import choice

class AnimationPlayer:
    def __init__(self):
        self.frames = {
            # magic
            'flame': import_folder('graphics/particles/flame/frames'),
            'aura': import_folder('graphics/particles/aura'),
            'heal': import_folder('graphics/particles/heal/frames'),

            # attacks
            'claw': import_folder('graphics/particles/claw'),
            'slash': import_folder('graphics/particles/slash'),
            'sparkle': import_folder('graphics/particles/sparkle'),
            # 'leaf_attack': import_folder('graphics/particles/leaf_attack'), # <-- BARIS INI DIHAPUS/DIKOMENTARI
            'thunder': import_folder('graphics/particles/thunder'),

            # monster deaths
            'trojan': import_folder('graphics/particles/smoke_orange'),
            'worm': import_folder('graphics/particles/raccoon'), # Pastikan path ini benar dan berisi gambar
            'ransomware': import_folder('graphics/particles/nova'),
        }
        

    def reflect_images(self, frames):
        new_frames = []
        if frames: # Pastikan frames tidak None atau kosong
            for frame in frames:
                flipped_frame = pygame.transform.flip(frame, True, False)
                new_frames.append(flipped_frame)
        return new_frames

    def create_particles(self, animation_type, pos, groups):
        if animation_type in self.frames:
            animation_frames = self.frames[animation_type]
            if animation_frames: # Pastikan ada frame yang dimuat untuk tipe ini
                ParticleEffect(pos, animation_frames, groups)
            else:
                print(f"[WARNING] AnimationPlayer.create_particles: No frames found for animation_type '{animation_type}' (folder might be empty or path issue). Particles not created.")
        else:
            print(f"[WARNING] AnimationPlayer.create_particles: animation_type '{animation_type}' not found in self.frames. Particles not created.")


class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups):
        super().__init__(groups)
        self.sprite_type = 'particle' # Lebih generik daripada 'magic'
        self.frame_index = 0
        self.animation_speed = 0.15 # Bisa disesuaikan per partikel jika perlu
        self.frames = animation_frames

        if self.frames and len(self.frames) > 0: # Pastikan ada frame dan list tidak kosong
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=pos)
        else:
            # Jika tidak ada frame, buat dummy surface kecil agar tidak error, lalu kill
            print(f"[ERROR] ParticleEffect.__init__: No animation_frames provided or list is empty for particle at pos {pos}. Killing particle.")
            self.image = pygame.Surface((1, 1), pygame.SRCALPHA) # Dummy transparan kecil
            self.rect = self.image.get_rect(center=pos)
            self.kill() # Hancurkan sprite ini segera jika tidak ada frame

    def animate(self):
        # Jika sprite sudah di-kill (misalnya karena tidak ada frame di init), jangan proses lebih lanjut
        if not self.alive():
            return
        # Juga, jika karena alasan lain frames menjadi None/kosong setelah init
        if not self.frames or len(self.frames) == 0:
            self.kill()
            return

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            # Pastikan frame_index yang di-cast ke int valid
            try:
                self.image = self.frames[int(self.frame_index)]
            except IndexError:
                print(f"[ERROR] ParticleEffect.animate: Frame index {int(self.frame_index)} out of range for {len(self.frames)} frames. Killing particle.")
                self.kill()


    def update(self):
        self.animate()
