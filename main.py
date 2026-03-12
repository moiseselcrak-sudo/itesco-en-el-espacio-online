import pygame
import random
import math 
import asyncio 

pygame.init()
pygame.mixer.init()

ANCHO = 800
ALTO = 600
# SIN SCALED para que el puntero del mouse no se descalibre en la web
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ITESCO EN EL ESPACIO - Equipo 2")
RELOJ = pygame.time.Clock()
FPS = 60

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
AMARILLO = (255, 255, 0)
MORADO = (128, 0, 128)
NARANJA = (255, 165, 0)
CYAN = (0, 255, 255)
GRIS = (50, 50, 50)
VERDE_CLARO = (144, 238, 144)

def cargar_fondo(nombre):
    try:
        img = pygame.image.load(nombre)
        return pygame.transform.scale(img, (ANCHO, ALTO))
    except:
        return None

def cargar_sprite(nombre, ancho, alto):
    try:
        img = pygame.image.load(nombre)
        img = pygame.transform.scale(img, (ancho, alto))
        return img.convert_alpha() 
    except:
        surf = pygame.Surface((ancho, alto))
        surf.fill(GRIS)
        return surf

img_fondo_inicio = cargar_fondo("inicio.png")
img_fondo_juego = cargar_fondo("fondo.png")
img_fondo_jefe = cargar_fondo("fondo_jefe.png")
img_fondo_win = cargar_fondo("win2.png")
img_fondo_gameover = cargar_fondo("gameover2.png")
img_itesco = cargar_fondo("itesco.png")
img_itesco_noche = cargar_fondo("itesco_noche.png")

img_nave1 = cargar_sprite("nave1.png", 50, 50)
img_nave2 = cargar_sprite("nave2.png", 50, 50)
img_nave3 = cargar_sprite("nave3.png", 50, 50) 
img_nave4 = cargar_sprite("nave4.png", 50, 50)
img_nave5 = cargar_sprite("nave5.png", 50, 50)

img_asteroide = cargar_sprite("asteroide.png", 40, 40)
img_enemigo = cargar_sprite("enemigo.png", 40, 40)
img_enemigo = pygame.transform.rotate(img_enemigo, 180)

img_jefe1 = cargar_sprite("jefe1.png", 150, 100)
img_jefe2 = cargar_sprite("jefe2.png", 150, 100)
img_moneda = cargar_sprite("moneda.png", 25, 25)

img_kenzo = cargar_sprite("kenzo.png", 120, 160)
img_dibanhi = cargar_sprite("dibanhi.png", 120, 160)
img_santiago = cargar_sprite("santiago.png", 120, 160)
img_belen = cargar_sprite("belen.png", 120, 160)
img_moises = cargar_sprite("moises.png", 120, 160)
img_kenzo_malo = cargar_sprite("kenzo_malo.png", 150, 160)
img_enemigo_intro = cargar_sprite("enemigo.png", 150, 150)

NAVES_INFO = {
    0: {"nombre": "Moises", "img": img_nave1, "color": VERDE, "vida": 100, "vel": 5, "tipo": "normal", "daño": 35, "cooldown": 400, "costo": 5},
    1: {"nombre": "Santiago", "img": img_nave2, "color": CYAN, "vida": 70, "vel": 8, "tipo": "rapida", "daño": 25, "cooldown": 300, "costo": 5},
    2: {"nombre": "Kenzo", "img": img_nave3, "color": AZUL, "vida": 250, "vel": 3, "tipo": "pesada", "daño": 45, "cooldown": 600, "costo": 8},
    3: {"nombre": "Dibanhi", "img": img_nave4, "color": NARANJA, "vida": 120, "vel": 5, "tipo": "triple", "daño": 20, "cooldown": 800, "costo": 10},
    4: {"nombre": "Belen", "img": img_nave5, "color": ROJO, "vida": 60, "vel": 6, "tipo": "laser", "daño": 150, "cooldown": 1500, "costo": 7}
}

nave_seleccionada = 0
monedas_totales = 0 
mejoras = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0} 

def cargar_sonido(nombre):
    try:
        return pygame.mixer.Sound(nombre)
    except:
        return None

sonido_explosion = cargar_sonido("explosion.ogg")
sonido_moneda = cargar_sonido("coin.ogg")
sonido_gameover = cargar_sonido("gameover.ogg")
sonido_victoria = cargar_sonido("win.ogg")
sonido_powerup = cargar_sonido("powerup.ogg")
sonido_bomba = cargar_sonido("bomba.ogg")
sonido_kenzo_malo = cargar_sonido("final.ogg")

sonidos_disparos = {
    "normal": cargar_sonido("laser_normal.ogg"),
    "rapida": cargar_sonido("laser_rapido.ogg"),
    "pesada": cargar_sonido("laser_pesado.ogg"),
    "triple": cargar_sonido("laser_escopeta.ogg"),
    "laser":  cargar_sonido("laser_sniper.ogg"),
    "auto":   cargar_sonido("laser_auto.ogg")
}

def cambiar_musica(archivo):
    try:
        if pygame.mixer.music.get_busy():
             pygame.mixer.music.fadeout(300)
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1) 
    except:
        pass

class Jugador(pygame.sprite.Sprite):
    def __init__(self, info_nave, nivel_mejora):
        super().__init__()
        self.info = info_nave
        self.nivel = nivel_mejora
        self.image = self.info["img"]
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.bottom = ALTO - 10
        
        self.vida_max = int(self.info["vida"] * (1 + self.nivel * 0.2))
        self.vida = self.vida_max
        self.velocidad = self.info["vel"] * (1 + self.nivel * 0.05)
        self.daño_actual = int(self.info["daño"] * (1 + self.nivel * 0.15))
        
        factor_reduccion = 1 - (self.nivel * 0.10)
        if factor_reduccion < 0.2: factor_reduccion = 0.2
        self.cooldown_actual = int(self.info["cooldown"] * factor_reduccion)
        
        self.monedas_partida = 0
        self.ultimo_disparo = 0
        self.bombas = 3
        self.powerup_doble = False
        self.tiempo_powerup = 0

    def update(self):
        if self.powerup_doble:
            if pygame.time.get_ticks() - self.tiempo_powerup > 5000:
                self.powerup_doble = False

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]: self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]: self.rect.x += self.velocidad
        if teclas[pygame.K_UP]: self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN]: self.rect.y += self.velocidad

        if teclas[pygame.K_SPACE]:
            self.intentar_disparar()

        if self.rect.right > ANCHO: self.rect.right = ANCHO
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.bottom > ALTO: self.rect.bottom = ALTO
        if self.rect.top < 0: self.rect.top = 0

    def intentar_disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.cooldown_actual:
            self.ultimo_disparo = ahora
            self.crear_balas()
            tipo = self.info["tipo"]
            if sounds_dict := sonidos_disparos.get(tipo):
                sounds_dict.play()

    def crear_balas(self):
        tipo = self.info["tipo"]
        d = self.daño_actual
        if self.powerup_doble:
            if tipo == "triple": 
                for i in range(-2, 3): 
                    bala = Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)
                    all_sprites.add(bala)
                    balas_jugador.add(bala)
            elif tipo == "auto": 
                bala1 = Bala(self.rect.left, self.rect.top, 0, -14, AMARILLO, d)
                bala2 = Bala(self.rect.right, self.rect.top, 0, -14, AMARILLO, d)
                all_sprites.add(bala1, bala2)
                balas_jugador.add(bala1, bala2)
            else: 
                color_bala = self.info["color"]
                bala1 = Bala(self.rect.left, self.rect.top, 0, -10, color_bala, d)
                bala2 = Bala(self.rect.right, self.rect.top, 0, -10, color_bala, d)
                all_sprites.add(bala1, bala2)
                balas_jugador.add(bala1, bala2)
        else:
            if tipo == "normal" or tipo == "rapida" or tipo == "pesada":
                bala = Bala(self.rect.centerx, self.rect.top, 0, -10, AMARILLO, d)
                all_sprites.add(bala)
                balas_jugador.add(bala)
            elif tipo == "triple": 
                for i in range(-1, 2): 
                    bala = Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)
                    all_sprites.add(bala)
                    balas_jugador.add(bala)
            elif tipo == "laser": 
                bala = Bala(self.rect.centerx, self.rect.top, 0, -25, ROJO, d)
                all_sprites.add(bala)
                balas_jugador.add(bala)
            elif tipo == "auto": 
                dispersion = random.randrange(-5, 6)
                bala = Bala(self.rect.centerx + dispersion, self.rect.top, 0, -14, AMARILLO, d)
                all_sprites.add(bala)
                balas_jugador.add(bala)
    
    def activar_doble_disparo(self):
        self.powerup_doble = True
        self.tiempo_powerup = pygame.time.get_ticks()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.tipo = random.choice(['vida', 'doble'])
        self.image = pygame.Surface((30, 30))
        if self.tipo == 'vida':
            self.image.fill(ROJO)
            pygame.draw.rect(self.image, BLANCO, (10, 5, 10, 20))
            pygame.draw.rect(self.image, BLANCO, (5, 10, 20, 10))
        else:
            self.image.fill(AZUL)
            pygame.draw.circle(self.image, BLANCO, (15, 15), 10, 2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > ALTO: self.kill()

class EnemigoBasico(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_asteroide
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.velocidad_y = random.randrange(2, 5)
        self.vida = 40 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()

class NaveEnemiga(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_enemigo
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width)
        self.rect.y = random.randrange(-150, -50)
        self.velocidad_y = random.randrange(1, 3)
        self.vida = 80 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()
        if random.randrange(0, 100) < 1: self.disparar()
    def disparar(self):
        bala = BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 5)
        all_sprites.add(bala)
        balas_enemigas.add(bala)

class Boss(pygame.sprite.Sprite):
    def __init__(self, jugador_objetivo):
        super().__init__()
        self.image = img_jefe1
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.y = -100
        self.entrando = True
        self.vida = 2500 
        self.vida_max = 2500
        self.cooldown_disparo = 0
        self.jugador = jugador_objetivo
        self.destino_x = ANCHO // 2
        self.destino_y = 100
        self.velocidad_movimiento = 2

    def update(self):
        if self.vida <= self.vida_max / 2:
            self.image = img_jefe2
            self.velocidad_movimiento = 4
            cooldown_base = 40
        else:
            self.image = img_jefe1
            self.velocidad_movimiento = 2
            cooldown_base = 60

        if self.entrando:
            self.rect.y += 2
            if self.rect.y >= 50: 
                self.entrando = False
        else:
            dx = self.destino_x - self.rect.centerx
            dy = self.destino_y - self.rect.centery
            distancia = math.sqrt(dx**2 + dy**2)
            
            if distancia > 5:
                self.rect.centerx += int(dx / distancia * self.velocidad_movimiento)
                self.rect.centery += int(dy / distancia * self.velocidad_movimiento)
            else:
                self.destino_x = random.randint(100, ANCHO - 100)
                self.destino_y = random.randint(50, ALTO // 2)

            self.cooldown_disparo += 1
            if self.cooldown_disparo >= cooldown_base:
                self.atacar()
                self.cooldown_disparo = 0
                
    def atacar(self):
        if self.vida > self.vida_max / 2:
            opciones = ["simple", "rafaga", "dirigido"]
            ataque = random.choice(opciones)
        else:
            opciones = ["rafaga", "circular", "dirigido", "circular"]
            ataque = random.choice(opciones)

        if ataque == "simple":
            bala = BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 8)
            all_sprites.add(bala)
            balas_enemigas.add(bala)
            
        elif ataque == "rafaga":
            for i in range(-2, 3):
                bala = BalaEnemigo(self.rect.centerx, self.rect.bottom, i*2, 6)
                all_sprites.add(bala)
                balas_enemigas.add(bala)
                
        elif ataque == "circular":
            num_balas = 12
            for i in range(num_balas):
                angulo = (360 / num_balas) * i
                radianes = math.radians(angulo)
                vel_x = 5 * math.cos(radianes)
                vel_y = 5 * math.sin(radianes)
                bala = BalaEnemigo(self.rect.centerx, self.rect.centery, vel_x, vel_y)
                all_sprites.add(bala)
                balas_enemigas.add(bala)
                
        elif ataque == "dirigido":
            dx = self.jugador.rect.centerx - self.rect.centerx
            dy = self.jugador.rect.centery - self.rect.centery
            distancia = math.sqrt(dx**2 + dy**2)
            if distancia > 0:
                vel_x = (dx / distancia) * 8
                vel_y = (dy / distancia) * 8
                bala = BalaEnemigo(self.rect.centerx, self.rect.centery, vel_x, vel_y)
                all_sprites.add(bala)
                balas_enemigas.add(bala)

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y, color, damage):
        super().__init__()
        self.image = pygame.Surface((6, 16))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.damage = damage 
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0: self.kill()

class BalaEnemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x, speed_y):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(NARANJA)
        self.rect = self.image.get_rect()
        self.rect.centerx = int(x)
        self.rect.top = int(y)
        self.x = float(x)
        self.y = float(y)
        self.speed_x = speed_x
        self.speed_y = speed_y
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        if (self.rect.top > ALTO or self.rect.bottom < 0 or 
            self.rect.right < 0 or self.rect.left > ANCHO):
            self.kill()

class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = img_moneda
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    def update(self):
        self.rect.y += 3
        if self.rect.top > ALTO: self.kill()

def dibujar_texto(pantalla, texto, tamaño, x, y, color=BLANCO, con_sombra=False):
    fuente = pygame.font.SysFont("arial", tamaño, bold=True)
    if con_sombra:
        sombra = fuente.render(texto, True, NEGRO)
        pantalla.blit(sombra, (x - sombra.get_width()//2 + 2, y + 2))
    superficie = fuente.render(texto, True, color)
    rect = superficie.get_rect()
    rect.midtop = (x, y)
    pantalla.blit(superficie, rect)

def dibujar_texto_con_fondo(pantalla, texto, tamaño, x, y, color=BLANCO):
    fuente = pygame.font.SysFont("arial", tamaño, bold=True)
    superficie = fuente.render(texto, True, color)
    rect_texto = superficie.get_rect()
    rect_texto.midtop = (x, y)
    fondo = pygame.Surface((rect_texto.width + 20, rect_texto.height + 10))
    fondo.fill(NEGRO)
    fondo.set_alpha(180)
    rect_fondo = fondo.get_rect(center=rect_texto.center)
    pantalla.blit(fondo, rect_fondo)
    pantalla.blit(superficie, rect_texto)

def dibujar_boton(pantalla, texto, x, y, w, h, color_base, color_hover, clic_detectado=False):
    mouse = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, w, h)
    color = color_base
    activado = False
    
    if rect.collidepoint(mouse):
        color = color_hover
        if clic_detectado:
            activado = True
            
    pygame.draw.rect(pantalla, color, rect)
    pygame.draw.rect(pantalla, BLANCO, rect, 2)
    dibujar_texto(pantalla, texto, 18, x + w//2, y + 10, NEGRO, con_sombra=False)
    return activado

def spawn_enemigos(cantidad):
    for i in range(cantidad):
        if random.random() > 0.5: e = EnemigoBasico()
        else: e = NaveEnemiga()
        all_sprites.add(e)
        enemigos.add(e)

def reiniciar_partida():
    global all_sprites, enemigos, balas_jugador, balas_enemigas, monedas, grupo_boss, powerups, jugador, score, boss_activo
    all_sprites = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()
    balas_jugador = pygame.sprite.Group()
    balas_enemigas = pygame.sprite.Group()
    monedas = pygame.sprite.Group()
    grupo_boss = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    info = NAVES_INFO[nave_seleccionada]
    nivel = mejoras[nave_seleccionada]
    jugador = Jugador(info, nivel)
    
    all_sprites.add(jugador)
    score = 0
    boss_activo = False
    spawn_enemigos(8)
    pygame.mixer.stop()

async def animacion_intro():
    guion = [
        {"texto": "Kenzo: Oigan, ¿trajeron todo para la presentación del videojuego?", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Dibanhi: Sí, pero... ¿dónde está Moy?", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Santiago: ¡No me digan que va a llegar tarde otra vez!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Belén: ¡La profe Karen nos va a reprobar si no llegamos a tiempo!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Kenzo: Esperen... ¿qué es ese ruido en el cielo?", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "ALIENS: ¡HUMANOS! ¡EL ITESCO AHORA NOS PERTENECE!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "ALIENS: ¡ENTREGUEN SUS PROYECTOS O SERÁN DESTRUIDOS!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "Santiago: ¡Rayos! ¡Van a destruir los servidores!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "Moises: ¡Oigan! Perdón por la tardanza...", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Moises: Es que vi a Bulmaro escondiendo unas cajas raras.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Moises: Lo seguí y encontré estos trajes y naves.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Moises: ¿Están cool no? ¿Oigan Por qué esas caras de susto?", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Dibanhi: ¡Moy! ¡Eres un ...!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Todos: ¡A LAS NAVES! ¡HAY QUE SALVAR EL SEMESTRE!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]}
    ]

    indice_dialogo = 0
    
    while indice_dialogo < len(guion):
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    indice_dialogo += 1

        if indice_dialogo >= len(guion): break

        escena = guion[indice_dialogo]
        activos = escena["activos"]

        if "aliens" in activos:
            if img_itesco_noche: PANTALLA.blit(img_itesco_noche, (0, 0))
            else: PANTALLA.fill(NEGRO)
        else:
            if img_itesco: PANTALLA.blit(img_itesco, (0, 0))
            else: PANTALLA.fill(GRIS)

        if "kenzo" in activos:    PANTALLA.blit(img_kenzo, (480, 300))
        if "dibanhi" in activos:  PANTALLA.blit(img_dibanhi, (180, 300))
        if "santiago" in activos: PANTALLA.blit(img_santiago, (330, 300))
        if "belen" in activos:    PANTALLA.blit(img_belen, (630, 300))
        if "moises" in activos:   PANTALLA.blit(img_moises, (30, 300))
        if "aliens" in activos:   PANTALLA.blit(img_enemigo_intro, (ANCHO//2 - 75, 50))

        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO - 100, ANCHO, 100))
        pygame.draw.rect(PANTALLA, BLANCO, (0, ALTO - 100, ANCHO, 100), 3)
        dibujar_texto(PANTALLA, escena["texto"], 20, ANCHO//2, ALTO - 70, BLANCO)
        dibujar_texto(PANTALLA, "[ESPACIO para continuar]", 16, ANCHO - 100, ALTO - 20, AMARILLO)

        pygame.display.flip()
        await asyncio.sleep(0) 

    return "seleccion"

async def animacion_jefe():
    img_jefe_grande = pygame.transform.scale(img_jefe1, (300, 200))
    guion = [
        {"texto": "BOSS: JAJAJA... ¡Patéticos estudiantes!", "habla": "jefe"},
        {"texto": "BOSS: Han derrotado a mis tropas, pero...", "habla": "jefe"},
        {"texto": "BOSS: ¡HASTA AQUÍ LLEGARON! ¡Su viaje termina ahora!", "habla": "jefe"},
        {"texto": "Moises: Uy, qué carácter... ¿no prefieres un leftcito?", "habla": "team"},
        {"texto": "Kenzo: ¡No te tenemos miedo!", "habla": "team"},
        {"texto": "Todos: ¡TE VENCEREMOS Y SALVAREMOS EL ITESCO!", "habla": "team"}
    ]

    indice = 0
    cambiar_musica("musica_jefe.ogg") 

    while indice < len(guion):
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    indice += 1

        if indice >= len(guion): break

        if img_fondo_jefe: PANTALLA.blit(img_fondo_jefe, (0, 0))
        else: PANTALLA.fill(NEGRO)

        escena = guion[indice]
        if escena["habla"] == "jefe":
            img_jefe_grande.set_alpha(255 if pygame.time.get_ticks() % 1000 < 500 else 200)
            PANTALLA.blit(img_jefe_grande, (ANCHO - 350, 150))
        elif escena["habla"] == "team":
            PANTALLA.blit(img_kenzo, (20, 300))
            PANTALLA.blit(img_dibanhi, (120, 300))
            PANTALLA.blit(img_santiago, (220, 300))
            PANTALLA.blit(img_belen, (320, 300))
            PANTALLA.blit(img_moises, (420, 300))

        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO - 120, ANCHO, 120))
        pygame.draw.rect(PANTALLA, AZUL, (0, ALTO - 120, ANCHO, 120), 4) 
        dibujar_texto(PANTALLA, escena["texto"], 28, ANCHO//2, ALTO - 80, BLANCO)
        dibujar_texto(PANTALLA, "[ESPACIO para continuar]", 18, ANCHO - 120, ALTO - 30, VERDE)

        pygame.display.flip()
        await asyncio.sleep(0) 

async def animacion_epilogo():
    cambiar_musica("final.ogg") 
    kenzo_mirando = pygame.transform.flip(img_kenzo, True, False) 
    jefe_muriendo = pygame.transform.scale(img_jefe2.copy(), (200, 150))
    jefe_muriendo.set_alpha(150) 
    zoom_kenzo = 1.0 

    guion = [
        {"texto": "Kenzo: ¡Se acabó! El ITESCO está a salvo.", "estado": "normal"},
        {"texto": "BOSS: Jejeje... ¿A salvo? Pobre criatura ignorante...", "estado": "normal"},
        {"texto": "BOSS: Mi armadura limitaba mi poder... y tú acabas de romperla.", "estado": "normal"},
        {"texto": "BOSS: He buscado por galaxias un recipiente digno...", "estado": "normal"},
        {"texto": "Kenzo: ¿De qué hablas? ¡Tu energía se desvanece!", "estado": "normal"},
        {"texto": "BOSS: Al contrario... ¡AHORA ES TUYA!", "estado": "absorcion"},
        {"texto": "Kenzo: ¡NO! ¡SAL DE MI CABEZA! ¡AAAAAGHH!", "estado": "absorcion"},
        {"texto": "...", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Silencio... Ya no hay dolor.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Kenzo era débil. Se preocupaba por exámenes y tareas.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Ya veo la verdad. Este mundo es solo combustible.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Corran, escóndanse, amigos míos...", "estado": "malo"},
        {"texto": "Kenzo (Renacido): EL VERDADERO JUEGO APENAS COMIENZA.", "estado": "malo"}
    ]

    indice = 0; alpha_negro = 0 

    while indice < len(guion):
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE or evento.key == pygame.K_RETURN:
                    indice += 1

        if indice >= len(guion): break

        escena = guion[indice]; estado = escena["estado"]

        if img_fondo_jefe: PANTALLA.blit(img_fondo_jefe, (0, 0))
        else: PANTALLA.fill(NEGRO)

        if estado == "normal":
            PANTALLA.blit(kenzo_mirando, (200, ALTO - 250))
            PANTALLA.blit(jefe_muriendo, (ANCHO - 300, 100))
        elif estado == "absorcion":
            PANTALLA.blit(kenzo_mirando, (200 + random.randint(-5, 5), ALTO - 250))
            if pygame.time.get_ticks() % 200 < 100: PANTALLA.blit(jefe_muriendo, (ANCHO - 300, 100))
            filtro_rojo = pygame.Surface((ANCHO, ALTO)); filtro_rojo.fill(ROJO); filtro_rojo.set_alpha(50)
            PANTALLA.blit(filtro_rojo, (0,0))
        elif estado == "malo":
            alpha_negro = min(200, alpha_negro + 2)
            sombra = pygame.Surface((ANCHO, ALTO)); sombra.fill(NEGRO); sombra.set_alpha(alpha_negro)
            PANTALLA.blit(sombra, (0,0))
            zoom_kenzo = min(3, zoom_kenzo + 0.005) 
            kenzo_g = pygame.transform.scale(img_kenzo_malo, (int(img_kenzo_malo.get_width() * zoom_kenzo), int(img_kenzo_malo.get_height() * zoom_kenzo)))
            PANTALLA.blit(kenzo_g, kenzo_g.get_rect(center=(ANCHO//2, ALTO//2)))

        color_borde = ROJO if estado in ["absorcion", "malo"] else AZUL
        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO - 100, ANCHO, 100))
        pygame.draw.rect(PANTALLA, color_borde, (0, ALTO - 100, ANCHO, 100), 3)
        dibujar_texto(PANTALLA, escena["texto"], 24, ANCHO//2, ALTO - 70, ROJO if estado == "malo" else BLANCO)
        dibujar_texto(PANTALLA, "[CONTINUAR]", 16, ANCHO - 100, ALTO - 20, GRIS)

        pygame.display.flip()
        await asyncio.sleep(0) 
    
    pygame.mixer.music.stop() 
    return "seleccion"

async def menu_principal():
    cambiar_musica("musica_menu.ogg") 
    while True:
        RELOJ.tick(FPS)
        clic = False 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clic = True 

        if img_fondo_inicio: PANTALLA.blit(img_fondo_inicio, (0, 0))
        else: PANTALLA.fill(NEGRO)
            
        dibujar_texto_con_fondo(PANTALLA, "ITESCO EN EL ESPACIO", 50, ANCHO//2, 100, AZUL)
        
        if dibujar_boton(PANTALLA, "INICIAR JUEGO", ANCHO//2 - 100, 250, 200, 50, VERDE, BLANCO, clic):
            return "intro" 
        if dibujar_boton(PANTALLA, "SALIR", ANCHO//2 - 100, 350, 200, 50, ROJO, BLANCO, clic):
            pygame.quit(); exit()
            
        pygame.display.flip()
        await asyncio.sleep(0) 

async def menu_seleccion():
    global nave_seleccionada, monedas_totales
    if not pygame.mixer.music.get_busy(): cambiar_musica("musica_menu.ogg") 

    while True:
        RELOJ.tick(FPS)
        clic = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clic = True

        PANTALLA.fill(NEGRO)
        dibujar_texto(PANTALLA, "TIENDA DE NAVES", 40, ANCHO//2, 10, BLANCO, con_sombra=True)
        dibujar_texto(PANTALLA, f"Tus Monedas: {monedas_totales}", 25, ANCHO - 150, 20, AMARILLO)

        for i in range(5):
            info = NAVES_INFO[i]; lvl = mejoras[i]
            x = 50 + (i % 3) * 250; y = 80 + (i // 3) * 240
            
            if i == nave_seleccionada: pygame.draw.rect(PANTALLA, BLANCO, (x-5, y-5, 210, 220), 3)
            pygame.draw.rect(PANTALLA, GRIS, (x, y, 200, 210))
            PANTALLA.blit(info["img"], info["img"].get_rect(center=(x + 100, y + 30)))
            
            dibujar_texto(PANTALLA, f"{info['nombre']} (Nvl {lvl})", 20, x + 100, y + 55, BLANCO)
            dibujar_texto(PANTALLA, f"Daño: {int(info['daño'] * (1 + lvl * 0.15))} -> {int(info['daño'] * (1 + (lvl+1) * 0.15))}", 16, x + 100, y + 80, VERDE_CLARO)
            dibujar_texto(PANTALLA, f"Rapidez: {int(info['cooldown'] * (1 - lvl * 0.10))}ms -> {int(info['cooldown'] * (1 - (lvl+1) * 0.10))}ms", 16, x + 100, y + 100, VERDE_CLARO)
            
            costo = info["costo"] * (lvl + 1)
            if dibujar_boton(PANTALLA, "Elegir", x + 10, y + 140, 80, 30, VERDE, BLANCO, clic): nave_seleccionada = i
            if dibujar_boton(PANTALLA, f"Mejorar (${costo})", x + 100, y + 140, 90, 30, AMARILLO, BLANCO, clic):
                if monedas_totales >= costo: monedas_totales -= costo; mejoras[i] += 1
        
        if dibujar_boton(PANTALLA, "¡A VOLAR!", ANCHO//2 - 100, 550, 200, 40, AZUL, BLANCO, clic):
            reiniciar_partida(); return "juego"
        
        pygame.display.flip()
        await asyncio.sleep(0) 

async def ciclo_juego():
    global score, boss_activo, boss, monedas_totales 
    
    # NUEVA VARIABLE PARA EL EFECTO FLASH SIN CONGELAR
    flash_frames = 0 

    while True:
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_b and not boss_activo:
                    await animacion_jefe() 
                    boss_activo = True; boss = Boss(jugador)
                    all_sprites.add(boss); grupo_boss.add(boss)
                    for e in enemigos: e.kill()
                    cambiar_musica("musica_jefe.ogg") 
                
                # --- AQUÍ ESTÁ LA CORRECCIÓN DE LA BOMBA ---
                if evento.key == pygame.K_t:
                    if jugador.bombas > 0:
                        jugador.bombas -= 1
                        if sonido_bomba: sonido_bomba.play()
                        
                        # En lugar de usar sleep, le decimos que pinte blanco por 3 frames
                        flash_frames = 3 
                        
                        for e in list(enemigos):
                            e.vida -= 1000
                            if e.vida <= 0: e.kill(); score += 10
                        for b in grupo_boss: b.vida -= 500
                
                if evento.key == pygame.K_f:
                    pygame.mixer.music.stop(); return "victoria"

        if boss_activo and img_fondo_jefe: PANTALLA.blit(img_fondo_jefe, (0, 0))
        elif img_fondo_juego: PANTALLA.blit(img_fondo_juego, (0, 0))
        else: PANTALLA.fill(NEGRO)

        all_sprites.update()
        if not boss_activo and len(enemigos) < 8: spawn_enemigos(8 - len(enemigos))
        if score >= 100 and not boss_activo:
            await animacion_jefe() 
            boss_activo = True; boss = Boss(jugador); all_sprites.add(boss); grupo_boss.add(boss)
            for e in enemigos: e.kill()
            cambiar_musica("musica_jefe.ogg") 

        impactos = pygame.sprite.groupcollide(enemigos, balas_jugador, False, True)
        for enemigo, lista_balas in impactos.items():
            for bala in lista_balas:
                enemigo.vida -= bala.damage
                if enemigo.vida <= 0:
                    enemigo.kill(); score += 10
                    if sonido_explosion: sonido_explosion.play()
                    if random.random() > 0.9:
                        p = PowerUp(enemigo.rect.center); all_sprites.add(p); powerups.add(p)
                    elif random.random() > 0.6:
                        m = Moneda(enemigo.rect.centerx, enemigo.rect.centery); all_sprites.add(m); monedas.add(m)

        for p in pygame.sprite.spritecollide(jugador, powerups, True):
            if sonido_powerup: sonido_powerup.play()
            if p.tipo == 'vida': jugador.vida = min(jugador.vida_max, jugador.vida + 30)
            elif p.tipo == 'doble': jugador.activar_doble_disparo()

        if boss_activo:
            for boss_obj, lista_balas in pygame.sprite.groupcollide(grupo_boss, balas_jugador, False, True).items():
                for bala in lista_balas:
                    boss_obj.vida -= bala.damage
                    if boss_obj.vida <= 0:
                        boss_obj.kill(); boss_activo = False; score += 5000; monedas_totales += jugador.monedas_partida + 200
                        pygame.mixer.music.stop(); return "victoria"

        if pygame.sprite.spritecollide(jugador, enemigos, True): jugador.vida -= 20
        if pygame.sprite.spritecollide(jugador, balas_enemigas, True): jugador.vida -= 10
        if pygame.sprite.spritecollide(jugador, grupo_boss, False): jugador.vida -= 5

        if jugador.vida <= 0: monedas_totales += jugador.monedas_partida; pygame.mixer.music.stop(); return "game_over"

        for m in pygame.sprite.spritecollide(jugador, monedas, True):
            jugador.monedas_partida += 1
            if sonido_moneda: sonido_moneda.play()

        all_sprites.draw(PANTALLA)
        
        dibujar_texto(PANTALLA, f"Nave: {jugador.info['nombre']} (Lvl {jugador.nivel})", 20, 100, 10)
        dibujar_texto(PANTALLA, f"Puntos: {score}", 20, ANCHO//2, 10)
        dibujar_texto(PANTALLA, f"Monedas: {jugador.monedas_partida}", 20, ANCHO-80, 10)
        dibujar_texto(PANTALLA, f"Bombas [T]: {jugador.bombas}", 20, 100, 40, VERDE_CLARO)
        if jugador.powerup_doble: dibujar_texto(PANTALLA, "¡DOBLE DISPARO!", 20, ANCHO//2, 40, CYAN)

        l_vida = 200; actual = (max(0, jugador.vida) / jugador.vida_max) * l_vida
        pygame.draw.rect(PANTALLA, ROJO, (10, 70, l_vida, 15)); pygame.draw.rect(PANTALLA, VERDE, (10, 70, actual, 15))
        pygame.draw.rect(PANTALLA, BLANCO, (10, 70, l_vida, 15), 2)

        if boss_activo:
            dibujar_texto(PANTALLA, "¡JEFE!", 30, ANCHO//2, 60, con_sombra=True)
            pygame.draw.rect(PANTALLA, MORADO, (ANCHO//2-100, 90, (max(0, boss.vida)/boss.vida_max)*200, 20))

        # --- MAGIA DEL EFECTO FLASH ---
        if flash_frames > 0:
            PANTALLA.fill(BLANCO)
            flash_frames -= 1

        pygame.display.flip()
        await asyncio.sleep(0) 

async def pantalla_fin(tipo):
    img_bg = img_fondo_win if tipo == "victoria" else img_fondo_gameover
    txt_titulo = "¡MISIÓN COMPLETADA!" if tipo == "victoria" else "NAVE DESTRUIDA"
    c_titulo = VERDE if tipo == "victoria" else ROJO
    if tipo == "victoria" and sonido_victoria: sonido_victoria.play()
    elif tipo != "victoria" and sonido_gameover: sonido_gameover.play()

    while True:
        RELOJ.tick(FPS)
        clic = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); exit()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                clic = True

        PANTALLA.blit(img_bg, (0, 0)) if img_bg else PANTALLA.fill(NEGRO)
        off_y = 150 if img_bg else 0 

        dibujar_texto_con_fondo(PANTALLA, txt_titulo, 50, ANCHO//2, 100 + off_y, c_titulo)
        dibujar_texto_con_fondo(PANTALLA, f"Puntaje Final: {score}", 30, ANCHO//2, 200 + off_y)
        dibujar_texto_con_fondo(PANTALLA, f"Monedas Ganadas: {jugador.monedas_partida}", 30, ANCHO//2, 250 + off_y, AMARILLO)
        
        if dibujar_boton(PANTALLA, "CONTINUAR..." if tipo == "victoria" else "IR A LA TIENDA", ANCHO//2 - 100, 350 + off_y, 200, 50, AZUL, BLANCO, clic):
             pygame.mixer.stop() 
             return "epilogo" if tipo == "victoria" else "seleccion"

        pygame.display.flip()
        await asyncio.sleep(0) 

async def main():
    estado_actual = "menu"
    while True:
        if estado_actual == "menu": estado_actual = await menu_principal()
        elif estado_actual == "seleccion": estado_actual = await menu_seleccion()
        elif estado_actual == "intro": estado_actual = await animacion_intro()
        elif estado_actual == "juego": estado_actual = await ciclo_juego()
        elif estado_actual == "game_over": estado_actual = await pantalla_fin("derrota")
        elif estado_actual == "victoria": estado_actual = await pantalla_fin("victoria")
        elif estado_actual == "epilogo": estado_actual = await animacion_epilogo()
        await asyncio.sleep(0)

asyncio.run(main())