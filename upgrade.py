import pygame
from settings import *

class Upgrade:
	def __init__(self,player):
		# HAPUS: self.display_surface = pygame.display.get_surface()
		self.player = player
		self.attribute_nr = len(player.stats)
		self.attribute_names = list(player.stats.keys())
		self.max_values = list(player.max_stats.values())
		self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

		# item creation
		# self.height = self.display_surface.get_size()[1] * 0.8 # Akan dihitung di create_items
		# self.width = self.display_surface.get_size()[0] // 6   # Akan dihitung di create_items
		self.item_list = [] # Akan diisi oleh create_items

		# selection system 
		self.selection_index = 0
		self.selection_time = None
		self.can_move = True

	def input(self):
		keys = pygame.key.get_pressed()

		if self.can_move:
			if keys[pygame.K_RIGHT] and self.selection_index < self.attribute_nr - 1:
				self.selection_index += 1
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
			elif keys[pygame.K_LEFT] and self.selection_index >= 1:
				self.selection_index -= 1
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()

			if keys[pygame.K_SPACE]:
				self.can_move = False
				self.selection_time = pygame.time.get_ticks()
				if self.item_list: # Pastikan item_list sudah dibuat
					self.item_list[self.selection_index].trigger(self.player)

	def selection_cooldown(self):
		if not self.can_move:
			current_time = pygame.time.get_ticks()
			if current_time - self.selection_time >= 300:
				self.can_move = True

	# Method sekarang menerima 'surface'
	def create_items(self, surface):
		self.item_list = [] # Kosongkan dulu jika dipanggil ulang

		item_height = surface.get_size()[1] * 0.8
		item_width = surface.get_size()[0] // (self.attribute_nr if self.attribute_nr > 0 else 1) # Hindari bagi dengan nol

		for item_index, _ in enumerate(range(self.attribute_nr)): # Ubah nama variabel agar tidak bentrok
			# horizontal position
			full_width = surface.get_size()[0]
			increment = full_width // (self.attribute_nr if self.attribute_nr > 0 else 1)
			left = (item_index * increment) + (increment - item_width) // 2
			
			# vertical position 
			top = surface.get_size()[1] * 0.1

			# create the object 
			new_item = Item(left,top,item_width,item_height,item_index,self.font) # Ganti item menjadi new_item
			self.item_list.append(new_item)

	# Method display sekarang menerima 'surface'
	def display(self, surface):
		if not self.item_list: # Jika item belum dibuat (misalnya karena surface belum ada saat init)
			self.create_items(surface) # Buat item saat pertama kali display dipanggil dengan surface

		self.input()
		self.selection_cooldown()

		for index, item_obj in enumerate(self.item_list): # Ganti nama variabel item
			# get attributes
			name = self.attribute_names[index]
			value = self.player.get_value_by_index(index)
			max_value = self.max_values[index]
			cost = self.player.get_cost_by_index(index)
			# Teruskan 'surface' ke item_obj.display
			item_obj.display(surface,self.selection_index,name,value,max_value,cost)

class Item:
	def __init__(self,l,t,w,h,index,font):
		self.rect = pygame.Rect(l,t,w,h)
		self.index = index
		self.font = font

	def display_names(self,surface,name,cost,selected):
		color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

		title_surf = self.font.render(name,False,color)
		title_rect = title_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0,20))

		cost_surf = self.font.render(f'{int(cost)}',False,color)
		cost_rect = cost_surf.get_rect(midbottom = self.rect.midbottom - pygame.math.Vector2(0,20))
 
		surface.blit(title_surf,title_rect)
		surface.blit(cost_surf,cost_rect)

	def display_bar(self,surface,value,max_value,selected):
		top = self.rect.midtop + pygame.math.Vector2(0,60)
		bottom = self.rect.midbottom - pygame.math.Vector2(0,60)
		color = BAR_COLOR_SELECTED if selected else BAR_COLOR

		full_height = bottom[1] - top[1]
		if full_height <= 0: full_height = 1 # Hindari tinggi negatif/nol
		
		# Pastikan max_value tidak nol untuk menghindari ZeroDivisionError
		# dan value tidak melebihi max_value untuk perhitungan rasio
		current_value_clamped = max(0, min(value, max_value))
		ratio = (current_value_clamped / max_value) if max_value > 0 else 0
		
		relative_number = ratio * full_height
		# Pastikan tinggi value_rect tidak negatif
		bar_height = max(0, 10) # Tinggi minimum untuk batang nilai
		
		value_rect = pygame.Rect(top[0] - 15,bottom[1] - relative_number - (bar_height / 2) ,30,bar_height)
		# Koreksi sedikit: relative_number adalah tinggi dari bawah, jadi y atasnya adalah bottom[1] - relative_number
		# Kita gambar rectangle dari y atasnya.
		# Untuk value_rect, kita mungkin ingin menggambar dari atas ke bawah
		# atau dari bawah ke atas. Kode asli Anda menggambar dari bawah.
		# pygame.Rect(x, y, width, height)
		# y untuk value_rect adalah bottom[1] - relative_number
		
		# Batang utama (garis)
		pygame.draw.line(surface,color,top,bottom,5)
		# Batang nilai (persegi panjang yang menunjukkan nilai saat ini)
		# x, y, width, height
		# y_value_top = bottom[1] - relative_number
		# pygame.draw.rect(surface,color,pygame.Rect(top[0] - 15, y_value_top, 30, relative_number))
		# Kode asli Anda:
		pygame.draw.rect(surface,color,value_rect)


	def trigger(self,player):
		upgrade_attribute = list(player.stats.keys())[self.index]

		if player.exp >= player.upgrade_cost[upgrade_attribute] and player.stats[upgrade_attribute] < player.max_stats[upgrade_attribute]:
			player.exp -= player.upgrade_cost[upgrade_attribute]
			player.stats[upgrade_attribute] *= 1.2
			player.upgrade_cost[upgrade_attribute] *= 1.4

		if player.stats[upgrade_attribute] > player.max_stats[upgrade_attribute]:
			player.stats[upgrade_attribute] = player.max_stats[upgrade_attribute]

	def display(self,surface,selection_num,name,value,max_value,cost):
		if self.index == selection_num:
			pygame.draw.rect(surface,UPGRADE_BG_COLOR_SELECTED,self.rect)
			pygame.draw.rect(surface,UI_BORDER_COLOR,self.rect,4)
		else:
			pygame.draw.rect(surface,UI_BG_COLOR,self.rect)
			pygame.draw.rect(surface,UI_BORDER_COLOR,self.rect,4)
	
		self.display_names(surface,name,cost,self.index == selection_num)
		self.display_bar(surface,value,max_value,self.index == selection_num)