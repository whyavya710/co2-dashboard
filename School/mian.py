import asyncio
import math
import random

import pygame


WIDTH, HEIGHT = 960, 700
ARENA = pygame.Rect(24, 94, 912, 550)
INK = (20, 32, 32)
PANEL = (29, 47, 43)
FIELD = (45, 80, 63)
GRID = (54, 91, 69)
MINT = (157, 231, 190)
GOLD = (246, 202, 111)
CORAL = (240, 111, 93)
PAPER = (241, 238, 215)
MUTED = (158, 177, 158)


class Character:
	def __init__(self, name, health, attack_power, speed, radius, color, x, y):
		self.name = name
		self.max_health = health
		self.health = health
		self.attack_power = attack_power
		self.speed = speed
		self.radius = radius
		self.color = color
		self.x = float(x)
		self.y = float(y)

	@property
	def is_alive(self):
		return self.health > 0

	def take_damage(self, amount):
		damage = min(self.health, max(0, amount))
		self.health -= damage
		return damage

	def heal(self, amount):
		healing = min(self.max_health - self.health, max(0, amount))
		self.health += healing
		return healing


class ArenaGame:
	def __init__(self):
		pygame.init()
		pygame.display.set_caption("Verdant Arena")
		self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
		self.clock = pygame.time.Clock()
		self.title = pygame.font.SysFont("dejavusans", 25, bold=True)
		self.ui = pygame.font.SysFont("dejavusans", 16, bold=True)
		self.small = pygame.font.SysFont("dejavusans", 12, bold=True)
		self.random = random.Random()
		self.reset()

	def reset(self):
		self.player = Character("Astra", 100, 30, 245, 17, MINT, ARENA.centerx, ARENA.centery)
		self.enemies = []
		self.pickups = []
		self.wave = 1
		self.score = 0
		self.kills = 0
		self.facing = pygame.Vector2(1, 0)
		self.attack_cooldown = 0
		self.attack_flash = 0
		self.invulnerable = 0
		self.wave_timer = 0
		self.notice = "Clear the arena"
		self.notice_timer = 1.5
		self.game_over = False
		self.spawn_wave()

	def spawn_wave(self):
		for _ in range(2 + self.wave):
			side = self.random.randrange(4)
			if side == 0:
				x, y = self.random.randint(70, WIDTH - 70), ARENA.top + 30
			elif side == 1:
				x, y = self.random.randint(70, WIDTH - 70), ARENA.bottom - 30
			elif side == 2:
				x, y = ARENA.left + 30, self.random.randint(140, ARENA.bottom - 45)
			else:
				x, y = ARENA.right - 30, self.random.randint(140, ARENA.bottom - 45)
			self.enemies.append(Character(
				"Bramble", 34 + self.wave * 7, 8 + self.wave,
				72 + min(self.wave * 4, 45), 16, CORAL, x, y,
			))
		self.notice = f"Wave {self.wave}"
		self.notice_timer = 1.3

	def attack(self):
		if self.attack_cooldown or self.game_over:
			return
		self.attack_cooldown = 0.36
		self.attack_flash = 0.18
		for enemy in self.enemies[:]:
			delta = pygame.Vector2(enemy.x - self.player.x, enemy.y - self.player.y)
			if delta.length() > 94:
				continue
			if delta.length_squared() and self.facing.dot(delta.normalize()) < 0.35:
				continue
			enemy.take_damage(self.player.attack_power)
			if not enemy.is_alive:
				self.enemies.remove(enemy)
				self.kills += 1
				self.score += 100 + self.wave * 10
				if self.random.random() < 0.25:
					self.pickups.append([enemy.x, enemy.y, 12.0])

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return False
				if self.game_over and event.key == pygame.K_r:
					self.reset()
				elif event.key == pygame.K_SPACE:
					self.attack()
			if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
				direction = pygame.Vector2(event.pos) - pygame.Vector2(self.player.x, self.player.y)
				if direction.length_squared():
					self.facing = direction.normalize()
				self.attack()
		return True

	def update(self, dt):
		if self.game_over:
			return
		self.attack_cooldown = max(0, self.attack_cooldown - dt)
		self.attack_flash = max(0, self.attack_flash - dt)
		self.invulnerable = max(0, self.invulnerable - dt)
		self.notice_timer = max(0, self.notice_timer - dt)
		keys = pygame.key.get_pressed()
		move = pygame.Vector2(
			int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
			int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
		)
		if move.length_squared():
			move = move.normalize()
			self.facing = move
			self.player.x += move.x * self.player.speed * dt
			self.player.y += move.y * self.player.speed * dt
		self.player.x = max(ARENA.left + 22, min(ARENA.right - 22, self.player.x))
		self.player.y = max(ARENA.top + 22, min(ARENA.bottom - 22, self.player.y))
		for enemy in self.enemies:
			delta = pygame.Vector2(self.player.x - enemy.x, self.player.y - enemy.y)
			distance = delta.length()
			if distance > self.player.radius + enemy.radius + 3 and distance:
				direction = delta.normalize()
				enemy.x += direction.x * enemy.speed * dt
				enemy.y += direction.y * enemy.speed * dt
			elif self.invulnerable <= 0:
				self.player.take_damage(enemy.attack_power)
				self.invulnerable = 0.72
				if not self.player.is_alive:
					self.game_over = True
					break
		for pickup in self.pickups[:]:
			pickup[2] -= dt
			if pickup[2] <= 0:
				self.pickups.remove(pickup)
			elif math.hypot(self.player.x - pickup[0], self.player.y - pickup[1]) < 30:
				if self.player.heal(22):
					self.notice = "Health restored"
					self.notice_timer = 0.8
				self.pickups.remove(pickup)
		if not self.enemies:
			if self.wave_timer <= 0:
				self.wave_timer = 1.5
				self.notice = "Arena clear"
			self.wave_timer -= dt
			if self.wave_timer <= 0:
				self.wave += 1
				self.player.heal(12)
				self.spawn_wave()

	def draw_character(self, character, player=False):
		x, y = int(character.x), int(character.y)
		pygame.draw.ellipse(self.screen, (27, 47, 41), (x - 19, y + 12, 38, 12))
		if player and self.invulnerable > 0 and int(self.invulnerable * 18) % 2:
			return
		if player:
			pygame.draw.polygon(self.screen, (102, 185, 143), ((x, y - 13), (x + 17, y + 15), (x, y + 9), (x - 17, y + 15)))
			pygame.draw.circle(self.screen, (235, 190, 132), (x, y - 8), 10)
			pygame.draw.arc(self.screen, (93, 65, 53), (x - 10, y - 19, 20, 17), 0.1, math.pi - 0.1, 5)
			pygame.draw.circle(self.screen, GOLD, (x + 6, y + 5), 3)
			pygame.draw.circle(self.screen, INK, (x + int(self.facing.x * 7) + 3, y - 8 + int(self.facing.y * 7)), 2)
		else:
			pygame.draw.polygon(self.screen, (178, 75, 65), ((x - 15, y - 2), (x - 10, y - 15), (x - 3, y - 9), (x + 4, y - 18), (x + 10, y - 8), (x + 16, y - 2), (x + 11, y + 13), (x - 11, y + 13)))
			pygame.draw.circle(self.screen, (247, 161, 112), (x, y - 2), 8)
			pygame.draw.circle(self.screen, INK, (x - 3, y - 3), 2)
			pygame.draw.circle(self.screen, INK, (x + 4, y - 3), 2)
			pygame.draw.line(self.screen, PAPER, (x - 5, y + 3), (x + 5, y + 3), 2)
			pygame.draw.rect(self.screen, INK, (x - 14, y - 27, 28, 4), border_radius=2)
			fill = int(28 * character.health / character.max_health)
			pygame.draw.rect(self.screen, CORAL, (x - 14, y - 27, fill, 4), border_radius=2)

	def draw(self):
		self.screen.fill(INK)
		pygame.draw.rect(self.screen, PANEL, ARENA.inflate(8, 8), border_radius=18)
		pygame.draw.rect(self.screen, FIELD, ARENA, border_radius=14)
		for x in range(ARENA.left + 20, ARENA.right, 42):
			pygame.draw.line(self.screen, GRID, (x, ARENA.top + 12), (x, ARENA.bottom - 12))
		for y in range(ARENA.top + 18, ARENA.bottom, 42):
			pygame.draw.line(self.screen, GRID, (ARENA.left + 12, y), (ARENA.right - 12, y))
		pygame.draw.rect(self.screen, (91, 126, 87), ARENA, 2, border_radius=14)
		for x, y, _ in self.pickups:
			pygame.draw.circle(self.screen, MINT, (int(x), int(y)), 10)
			pygame.draw.rect(self.screen, (48, 113, 78), (int(x) - 2, int(y) - 6, 4, 12), border_radius=2)
			pygame.draw.rect(self.screen, (48, 113, 78), (int(x) - 6, int(y) - 2, 12, 4), border_radius=2)
		for enemy in self.enemies:
			self.draw_character(enemy)
		if self.attack_flash:
			start = pygame.Vector2(self.player.x, self.player.y) + self.facing * 22
			end = pygame.Vector2(self.player.x, self.player.y) + self.facing * 70
			pygame.draw.line(self.screen, GOLD, start, end, 8)
			pygame.draw.circle(self.screen, PAPER, (int(end.x), int(end.y)), 5)
		self.draw_character(self.player, player=True)
		pygame.draw.line(self.screen, (58, 76, 67), (26, 82), (WIDTH - 26, 82))
		self.screen.blit(self.title.render("VERDANT ARENA", True, PAPER), (28, 12))
		self.screen.blit(self.small.render("ASTRA  /  SEEDKEEPER", True, MINT), (30, 45))
		pygame.draw.rect(self.screen, PANEL, (300, 21, 220, 17), border_radius=8)
		bar = int(216 * self.player.health / self.player.max_health)
		if bar:
			pygame.draw.rect(self.screen, MINT if self.player.health > 35 else CORAL, (302, 23, bar, 13), border_radius=7)
		self.screen.blit(self.small.render(f"VITALITY {self.player.health}/{self.player.max_health}", True, MUTED), (301, 44))
		self.screen.blit(self.ui.render(f"WAVE {self.wave:02d}", True, GOLD), (588, 20))
		self.screen.blit(self.small.render(f"{len(self.enemies)} THREATS REMAINING", True, MUTED), (588, 45))
		self.screen.blit(self.ui.render(f"{self.score:06d}", True, PAPER), (850, 20))
		self.screen.blit(self.small.render("SCORE", True, MUTED), (875, 45))
		if self.notice_timer > 0 and not self.game_over:
			text = self.ui.render(self.notice.upper(), True, PAPER)
			plate = pygame.Rect(0, 0, text.get_width() + 34, 34)
			plate.center = (WIDTH // 2, ARENA.top + 26)
			pygame.draw.rect(self.screen, PANEL, plate, border_radius=12)
			self.screen.blit(text, text.get_rect(center=plate.center))
		self.screen.blit(self.small.render("WASD / ARROWS  MOVE", True, MUTED), (28, 663))
		self.screen.blit(self.small.render("SPACE OR CLICK  STRIKE", True, MUTED), (248, 663))
		self.screen.blit(self.small.render("GREEN ORBS  HEAL", True, MUTED), (510, 663))
		self.screen.blit(self.small.render("ESC  QUIT", True, MUTED), (790, 663))
		if self.game_over:
			overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
			overlay.fill((10, 19, 18, 190))
			self.screen.blit(overlay, (0, 0))
			for message, y, font, color in (
				("THE GROVE WENT QUIET", 292, self.title, PAPER),
				(f"{self.kills} brambles cleared / score {self.score}", 333, self.ui, MINT),
				("PRESS R TO PLAY AGAIN / ESC TO LEAVE", 378, self.small, GOLD),
			):
				label = font.render(message, True, color)
				self.screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))
		pygame.display.flip()

	async def run(self):
		running = True
		while running:
			dt = min(self.clock.tick(60) / 1000, 0.04)
			running = self.events()
			self.update(dt)
			self.draw()
			await asyncio.sleep(0)
		pygame.quit()


async def main():
	await ArenaGame().run()


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		pass