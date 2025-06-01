import pygame 
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self,pos,groups,sprite_type,surface = pygame.Surface((TILESIZE,TILESIZE))): #
		super().__init__(groups) #
		self.sprite_type = sprite_type #
		y_offset = HITBOX_OFFSET.get(sprite_type, 0) # Gunakan .get untuk default jika sprite_type tidak ada di HITBOX_OFFSET
		self.image = surface #
		
		# Penyesuaian untuk 'object' agar hitboxnya pas dengan visual di tanah
		if sprite_type == 'object': #
			self.rect = self.image.get_rect(topleft = (pos[0],pos[1] - TILESIZE)) #
		# --- PERUBAHAN UNTUK ITEM KUNCI ---
		elif sprite_type == 'item_key':
			self.rect = self.image.get_rect(topleft = pos)
			# Hitbox untuk kunci bisa lebih kecil atau sama dengan rectnya, agar lebih mudah diambil
			self.hitbox = self.rect.inflate(-10, -10) # Contoh: hitbox sedikit lebih kecil
		# --- AKHIR PERUBAHAN ---
		else:
			self.rect = self.image.get_rect(topleft = pos) #
		
		# Pastikan hitbox dibuat untuk semua tipe yang relevan
		if sprite_type != 'item_key': # item_key sudah punya hitbox sendiri
			self.hitbox = self.rect.inflate(0,y_offset) #