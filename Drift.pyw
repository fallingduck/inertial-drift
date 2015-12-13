import pygame
import math
import random


def rot_center(image, rect, angle):
    """rotate an image while keeping its center"""
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image,rot_rect


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('./images/hero.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = 320, 240
        self.angle = 0
        self.orig_image = self.image.copy()

        self.velX = 0
        self.velY = 0


class Bullet(pygame.sprite.Sprite):

    def __init__(self, facing, scrollX, scrollY, group):
        pygame.sprite.Sprite.__init__(self)

        self.group = group
        self.angle = facing

        self.image = pygame.image.load('./images/blaster.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = 0, 0
        self.image,self.rect = rot_center(self.image, self.rect, facing)
        usefulDir = facing - 360 if facing > 180 else facing

        self.velX = math.sin(math.radians(usefulDir)) * -30
        self.velY = math.cos(math.radians(usefulDir)) * -30

        self.xPos = 320 - scrollX
        self.yPos = 240 - scrollY

        self.spawn = pygame.mixer.Sound('./music/blaster.ogg')
        self.spawn.set_volume(0.05)
        self.hit = pygame.mixer.Sound('./music/hit.ogg')
        self.hit.set_volume(0.5)
        self.spawn.play()

    def update(self, scrollX, scrollY):
        self.xPos += self.velX
        self.yPos += self.velY

        self.rect.center = scrollX + self.xPos, scrollY + self.yPos

        if 720 < self.yPos or self.yPos < -240 or 960 < self.xPos or self.xPos < -320:
            self.impact()

    def impact(self):
        self.hit.play()
        self.group.remove(self)


class Enemy(pygame.sprite.Sprite):

    def __init__(self, scrollX, scrollY, group):
        pygame.sprite.Sprite.__init__(self)

        self.group = group

        self.image = pygame.image.load('./images/enemy.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.orig_image = self.image.copy()

        self.velX = 0
        self.velY = 0
        self.angle = 0

        self.xPos = random.randrange(-320, 960)
        self.yPos = random.randrange(-240, 720)

        self.rect.center = self.xPos, self.yPos

        self.explode = pygame.mixer.Sound('./music/explosion1.ogg')

    def update(self, scrollX, scrollY):
        playerX, playerY = 320 - scrollX, 240 - scrollY
        self.angle = math.degrees(math.atan2(self.xPos - playerX, self.yPos - playerY))
        self.image, self.rect = rot_center(self.orig_image, self.rect, self.angle)

        usefulDir = self.angle - 360 if self.angle > 180 else self.angle

        if abs(self.velX + (math.sin(math.radians(usefulDir)) * 2)) <= 20:
            self.velX += math.sin(math.radians(usefulDir)) * 2
        if abs(self.velY + (math.cos(math.radians(usefulDir)) * 2)) <= 20:
            self.velY += math.cos(math.radians(usefulDir)) * 2

        self.xPos -= self.velX
        self.yPos -= self.velY

        if 700 < self.yPos:
            self.yPos = 700
        if self.yPos < -210:
            self.yPos = -210
        if 920 < self.xPos:
            self.xPos = 920
        if self.xPos < -300:
            self.xPos = -300

        self.rect.center = scrollX + self.xPos, scrollY + self.yPos

    def impact(self, score, debris_group, angle):
        self.explode.play()
        self.group.remove(self)
        for i in range(50):
            debris_group.add(Debris(self.xPos, self.yPos, angle, debris_group))
        return score + 100


class Debris(pygame.sprite.Sprite):

    def __init__(self, xPos, yPos, angle, group):
        pygame.sprite.Sprite.__init__(self)

        self.group = group

        realAngle = random.randrange(0, 360)
        usefulDir = realAngle - 360 if realAngle > 180 else realAngle
        self.velX = math.sin(math.radians(usefulDir)) * 5
        self.velY = math.cos(math.radians(usefulDir)) * 5
        self.xPos = xPos
        self.yPos = yPos

        self.image = pygame.image.load('./images/debris.png')
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.image, self.rect = rot_center(self.image, self.rect, random.randrange(0, 360))

        self.rect.center = self.xPos, self.yPos

        self.life = 21

    def update(self, scrollX, scrollY):
        self.life -= 1
        if self.life == 0:
            self.group.remove(self)
            return

        self.xPos += self.velX
        self.yPos += self.velY

        self.rect.center = scrollX + self.xPos, scrollY + self.yPos


class GoodDebris(pygame.sprite.Sprite):

    def __init__(self, xPos, yPos, angle, group):
        pygame.sprite.Sprite.__init__(self)

        self.group = group

        realAngle = random.randrange(0, 360)
        usefulDir = realAngle - 360 if realAngle > 180 else realAngle
        self.velX = math.sin(math.radians(usefulDir)) * 10
        self.velY = math.cos(math.radians(usefulDir)) * 10
        self.xPos = xPos
        self.yPos = yPos

        self.image = pygame.image.load('./images/gooddebris.png')
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.image, self.rect = rot_center(self.image, self.rect, random.randrange(0, 360))

        self.rect.center = self.xPos, self.yPos

        self.life = 21

    def update(self, scrollX, scrollY):
        self.life -= 1
        if self.life == 0:
            self.group.remove(self)
            return

        self.xPos += self.velX
        self.yPos += self.velY

        self.rect.center = scrollX + self.xPos, scrollY + self.yPos


class Background(pygame.sprite.Sprite):

    def __init__(self, (x,y)):
        pygame.sprite.Sprite.__init__(self)

        self.offsetX = x
        self.offsetY = y
        self.image = pygame.image.load('./images/grid2.png').convert()
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

    def update(self, xin, yin):
        self.rect.center = xin + self.offsetX, yin + self.offsetY


def start():
    pygame.init()
    game_over = False

    score_font = pygame.font.Font('./fonts/DejaVuSansMono.ttf', 18)
    go_font = pygame.font.Font('./fonts/DejaVuSansMono.ttf', 24)

    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Inertial Drift')

    background = pygame.image.load('./images/space.png').convert()

    scrollX = 0
    scrollY = 0

    score = 0

    tiles = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    debris = pygame.sprite.Group()
    good_debris = pygame.sprite.Group()

    player = Player()
    sprites.add(player)

    tiles.add(Background((0, 0)))
    tiles.add(Background((640, 0)))
    tiles.add(Background((0, 480)))
    tiles.add(Background((640, 480)))

    max_speed = 15
    cooldown = 0
    mouse_down = True
    enemy_countdown = 20

    running = True
    clock = pygame.time.Clock()

    pygame.mixer.music.load('./music/groove.ogg')
    pygame.mixer.music.play(-1)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_SPACE and game_over:
                    return
##            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
##                mouse_down = True
##            elif event.type == pygame.MOUSEBUTTONUP and not game_over:
##                mouse_down = False

        if mouse_down and cooldown == 0 and not game_over:
            cooldown = 2
            bullets.add(Bullet(player.angle, scrollX, scrollY, bullets))

        if cooldown > 0 and not game_over:
            cooldown -= 1

        if enemy_countdown == 0 and not game_over:
            enemy_countdown = 20
            enemies.add(Enemy(scrollX, scrollY, enemies))

        if not game_over:
            enemy_countdown -= 1

            # Rotate the ship towards the mouse
            mouseX, mouseY = pygame.mouse.get_pos()
            playerX, playerY = 320, 240
            player.angle = math.degrees(math.atan2(playerX-mouseX, playerY-mouseY))
            player.image,player.rect = rot_center(player.orig_image, player.rect, player.angle)

            # Player's velocity should be calculated here
            usefulDir = player.angle - 360 if player.angle > 180 else player.angle
            if abs(player.velX + math.sin(math.radians(usefulDir))) <= max_speed:
                player.velX += math.sin(math.radians(usefulDir))
            if abs(player.velY + math.cos(math.radians(usefulDir))) <= max_speed:
                player.velY += math.cos(math.radians(usefulDir))

            # Change scrollX and Y based on the player's velocity.
            scrollX += player.velX
            scrollY += player.velY
            scrollX = 615 if scrollX > 615 else scrollX
            scrollX = -615 if scrollX < -615 else scrollX
            scrollY = 450 if scrollY > 450 else scrollY
            scrollY = -450 if scrollY < -450 else scrollY

            # Update the position of the background tiles
            for i in tiles:
                i.update(scrollX, scrollY)

            for i in enemies:
                i.update(scrollX, scrollY)
                bullet_hits = pygame.sprite.spritecollide(i, bullets, False)
                for j in bullet_hits:
                    j.impact()
                    score = i.impact(score, debris, j.angle)
                    break

            for i in bullets:
                i.update(scrollX, scrollY)

            for i in debris:
                i.update(scrollX, scrollY)

            enemy_collisions = pygame.sprite.spritecollide(player, enemies, False)
            if enemy_collisions:
                for j in range(100):
                    good_debris.add(GoodDebris(320, 240, 0, good_debris))
                pygame.mixer.music.stop()
                game_over = True
                pygame.mixer.Sound('./music/explosion1.ogg').play()

            score += 1

        for i in good_debris:
            i.update(0, 0)

        # Draw the sprites
        screen.blit(background, (0, 0))
        if not game_over:
            tiles.draw(screen)
            debris.draw(screen)
            bullets.draw(screen)
            enemies.draw(screen)
            sprites.draw(screen)
        good_debris.draw(screen)
        score_text = score_font.render(str(score), 1, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        if game_over:
            go_text = go_font.render('GAME OVER!', 1, (255, 255, 255))
            gg_text = go_font.render('Press SPACE to Restart', 1, (255, 255, 255))
            screen.blit(go_text, (320 - (go_text.get_width() / 2),
                                  240 - (go_text.get_height() / 2)))

            screen.blit(gg_text, (320 - (gg_text.get_width() / 2),
                                  280 - (gg_text.get_height() / 2)))

        # FPS
        clock.tick(20)

        # Render graphics
        pygame.display.flip()

    pygame.quit()
    global replay
    replay = False


if __name__ == '__main__':
    replay = True
    while replay:
        start()
