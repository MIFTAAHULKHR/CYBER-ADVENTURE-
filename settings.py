WIDTH    = 960
HEIGHT   = 640
FPS      = 60
TILESIZE = 64
HITBOX_OFFSET = {
	'player': -26,
	'object': -40,
	'invisible': 0,
    'item_key': 0,
    'enemy': -10
    }

# ui 
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200 # Width of the health bar
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = 'graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

#font
WIN_FONT_SIZE = 72
TEXT_COLOR_WIN = 'gold'

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red' # Color of the health bar
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

#Winner Screen Colors
WINNER_GRID_BG_COLOR = (30, 30, 45)  # Contoh: Biru keunguan gelap
WINNER_GRID_LINE_COLOR = (50, 50, 70) # Contoh: Garis lebih terang
WINNER_TEXT_COLOR = 'yellow'
WINNER_TEXT_FONT_SIZE = 100 # Ukuran font untuk "WINNER!"

# weapons 
weapon_data = {
	'sword': {'cooldown': 100, 'damage': 15,'graphic':'graphics/weapons/sword/full.png'},
	'lance': {'cooldown': 400, 'damage': 30,'graphic':'graphics/weapons/lance/full.png'},
	'axe': {'cooldown': 300, 'damage': 20, 'graphic':'graphics/weapons/axe/full.png'},
	'rapier':{'cooldown': 50, 'damage': 8, 'graphic':'graphics/weapons/rapier/full.png'},
	'sai':{'cooldown': 80, 'damage': 10, 'graphic':'graphics/weapons/sai/full.png'}}

# magic
magic_data = {
	'flame': {'strength': 5,'cost': 20,'graphic':'graphics/particles/flame/fire.png'},
	'heal' : {'strength': 20,'cost': 10,'graphic':'graphics/particles/heal/heal.png'}}

# enemy
monster_data = {
	'trojan':	{'health': 100,'exp':100,'damage':3,
            	'attack_type': 'slash', 
                'attack_sound':'audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 
                'attack_radius': 80, 'notice_radius': 200},
	'worm':		{'health': 300,'exp':250,'damage':5,
          		'attack_type': 'claw',  
          		'attack_sound':'audio/attack/claw.wav','speed': 2, 'resistance': 3, 
          		'attack_radius': 120, 'notice_radius': 500},
	'ransomware':{'health': 100,'exp':110,'damage':8,
                'attack_type': 'thunder', 
                'attack_sound':'audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 
                'attack_radius': 60, 'notice_radius': 200},
}
	