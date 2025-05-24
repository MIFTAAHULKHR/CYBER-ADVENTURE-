import pygame
from settings import * 

class UI:
	def __init__(self):
		self.font = pygame.font.Font(UI_FONT,UI_FONT_SIZE)

		# bar setup 
		self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)
		self.energy_bar_rect = pygame.Rect(10,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)

		# convert weapon dictionary
		self.weapon_graphics = []
		for weapon in weapon_data.values():
			path = weapon['graphic']
			weapon = pygame.image.load(path).convert_alpha()
			self.weapon_graphics.append(weapon)

		# convert magic dictionary
		self.magic_graphics = []
		for magic in magic_data.values():
			magic = pygame.image.load(magic['graphic']).convert_alpha()
			self.magic_graphics.append(magic)

	def show_bar(self, surface, current,max_amount,bg_rect,color):
		if surface is None:
			return

		try:
			pygame.draw.rect(surface,UI_BG_COLOR,bg_rect)

			if max_amount <= 0: 
				ratio = 0
			else:
				current_clamped = max(0, min(current, max_amount))
				ratio = current_clamped / max_amount
			
			current_width = bg_rect.width * ratio
				
			current_rect = bg_rect.copy()
			current_rect.width = int(current_width)

			pygame.draw.rect(surface,color,current_rect)
			pygame.draw.rect(surface,UI_BORDER_COLOR,bg_rect,3)

		except Exception as e:
			print(f"ERROR in UI.show_bar drawing ({color}): {e}")


	def show_exp(self, surface, exp):
		if surface is None: return

		text_surf = self.font.render(str(int(exp)),False,TEXT_COLOR)
		x = surface.get_size()[0] - 20 
		y = surface.get_size()[1] - 20 
		text_rect = text_surf.get_rect(bottomright = (x,y))

		pygame.draw.rect(surface,UI_BG_COLOR,text_rect.inflate(20,20)) 
		surface.blit(text_surf,text_rect) 
		pygame.draw.rect(surface,UI_BORDER_COLOR,text_rect.inflate(20,20),3) 

	def selection_box(self, surface, left,top, has_switched):
		if surface is None: return pygame.Rect(0,0,0,0)

		bg_rect = pygame.Rect(left,top,ITEM_BOX_SIZE,ITEM_BOX_SIZE)
		pygame.draw.rect(surface,UI_BG_COLOR,bg_rect) 
		if has_switched:
			pygame.draw.rect(surface,UI_BORDER_COLOR_ACTIVE,bg_rect,3) 
		else:
			pygame.draw.rect(surface,UI_BORDER_COLOR,bg_rect,3) 
		return bg_rect

	def weapon_overlay(self, surface, weapon_index,has_switched):
		if surface is None: return
		
		# Hitung posisi Y secara dinamis
		# Posisi Y akan berada di dekat bagian bawah layar
		# (tinggi layar - ukuran kotak - margin bawah)
		y_position = surface.get_height() - ITEM_BOX_SIZE - 10 # 10 adalah margin dari bawah

		bg_rect = self.selection_box(surface, 10, y_position, has_switched) 
		weapon_surf = self.weapon_graphics[weapon_index]
		weapon_rect = weapon_surf.get_rect(center = bg_rect.center)

		surface.blit(weapon_surf,weapon_rect) 

	def magic_overlay(self, surface, magic_index,has_switched):
		if surface is None: return
		
		# Hitung posisi Y secara dinamis, sedikit di atas atau di sebelah weapon box
		# Di sini kita letakkan di sebelah kanan weapon box pada Y yang sama
		# Jika Anda ingin di atasnya, logikanya akan berbeda.
		# Untuk konsistensi dengan kode asli (magic di sebelah weapon), kita buat Y-nya sama.
		y_position = surface.get_height() - ITEM_BOX_SIZE - 10 # Y yang sama dengan weapon box
		x_position = 10 + ITEM_BOX_SIZE + 5 # Posisi X: setelah weapon box + sedikit spasi (10 adalah X weapon box, ITEM_BOX_SIZE adalah lebarnya)
                                            # Kode asli Anda menggunakan X = 80, yang berarti (10+ITEM_BOX_SIZE-10) jika ITEM_BOX_SIZE = 80
                                            # Mari kita gunakan x_position yang lebih jelas

		# Jika ITEM_BOX_SIZE = 80, maka 10 + 80 + 5 = 95. Kode asli Anda X = 80
		# Untuk mencocokkan kode asli, X untuk magic adalah sekitar 80.
		# Jadi X weapon adalah 10, X magic adalah 80.
		# Ini berarti ada spasi 80 - (10 + ITEM_BOX_SIZE) jika kita ingin mereka bersebelahan tanpa overlap.
		# Mari kita gunakan nilai X eksplisit dari kode asli Anda:
		x_weapon = 10
		x_magic = 80 # Ini adalah nilai dari kode asli Anda untuk magic box

		# bg_rect = self.selection_box(surface, x_position, y_position, has_switched)
		# Menggunakan x_magic dan y_position yang sama dengan weapon
		bg_rect = self.selection_box(surface, x_magic, y_position, has_switched)
		magic_surf = self.magic_graphics[magic_index]
		magic_rect = magic_surf.get_rect(center = bg_rect.center)

		surface.blit(magic_surf,magic_rect) 

	def display(self, surface, player):
		if surface is None:
			return
		
		self.show_bar(surface, player.health,player.stats['health'],self.health_bar_rect,HEALTH_COLOR)
		self.show_bar(surface, player.energy,player.stats['energy'],self.energy_bar_rect,ENERGY_COLOR)
		self.show_exp(surface, player.exp)

		self.weapon_overlay(surface, player.weapon_index,not player.can_switch_weapon)
		self.magic_overlay(surface, player.magic_index,not player.can_switch_magic)