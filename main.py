import pygame
import random
import math 
import asyncio 

pygame.init()
pygame.mixer.init()

ANCHO = 800
ALTO = 600
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ITESCO EN EL ESPACIO - Equipo 2")
RELOJ = pygame.time.Clock()
FPS = 60

NEGRO = (0, 0, 0); BLANCO = (255, 255, 255); VERDE = (0, 255, 0)
ROJO = (255, 0, 0); AZUL = (0, 0, 255); AMARILLO = (255, 255, 0)
MORADO = (128, 0, 128); NARANJA = (255, 165, 0); CYAN = (0, 255, 255)
GRIS = (50, 50, 50); VERDE_CLARO = (144, 238, 144)

def cargar_fondo(n):
    try: return pygame.transform.scale(pygame.image.load(n), (ANCHO, ALTO))
    except: return None

def cargar_sprite(n, w, h):
    try: return pygame.transform.scale(pygame.image.load(n), (w, h)).convert_alpha() 
    except: s = pygame.Surface((w, h)); s.fill(GRIS); return s

img_fondo_inicio = cargar_fondo("inicio.png"); img_fondo_juego = cargar_fondo("fondo.png")
img_fondo_jefe = cargar_fondo("fondo_jefe.png")
img_fondo_win = cargar_fondo("win2.png")
img_fondo_win_kenzo = cargar_fondo("win_kenzo.png") 
img_fondo_gameover = cargar_fondo("gameover2.png"); img_itesco = cargar_fondo("itesco.png")
img_itesco_noche = cargar_fondo("itesco_noche.png")

img_nave1 = cargar_sprite("nave1.png", 50, 50); img_nave2 = cargar_sprite("nave2.png", 50, 50)
img_nave3 = cargar_sprite("nave3.png", 50, 50); img_nave4 = cargar_sprite("nave4.png", 50, 50)
img_nave5 = cargar_sprite("nave5.png", 50, 50)
img_nave_renacida = cargar_sprite("nave_renacida.png", 60, 60) 

img_asteroide = cargar_sprite("asteroide.png", 40, 40)
img_enemigo = pygame.transform.rotate(cargar_sprite("enemigo.png", 40, 40), 180)
img_jefe1 = cargar_sprite("jefe1.png", 150, 100); img_jefe2 = cargar_sprite("jefe2.png", 150, 100)
img_moneda = cargar_sprite("moneda.png", 25, 25)

img_kenzo = cargar_sprite("kenzo.png", 120, 160); img_dibanhi = cargar_sprite("dibanhi.png", 120, 160)
img_santiago = cargar_sprite("santiago.png", 120, 160); img_belen = cargar_sprite("belen.png", 120, 160)
img_moises = cargar_sprite("moises.png", 120, 160); img_kenzo_malo = cargar_sprite("kenzo_malo.png", 150, 160)
img_enemigo_intro = cargar_sprite("enemigo.png", 150, 150)

NAVES_INFO = {
    0: {"nombre": "Moises", "img": img_nave1, "color": VERDE, "vida": 100, "vel": 5, "tipo": "normal", "daño": 35, "cooldown": 400, "costo": 5},
    1: {"nombre": "Santiago", "img": img_nave2, "color": CYAN, "vida": 70, "vel": 8, "tipo": "rapida", "daño": 25, "cooldown": 300, "costo": 5},
    2: {"nombre": "Kenzo", "img": img_nave3, "color": AZUL, "vida": 250, "vel": 3, "tipo": "pesada", "daño": 45, "cooldown": 600, "costo": 8},
    3: {"nombre": "Dibanhi", "img": img_nave4, "color": NARANJA, "vida": 120, "vel": 5, "tipo": "triple", "daño": 20, "cooldown": 800, "costo": 10},
    4: {"nombre": "Belen", "img": img_nave5, "color": ROJO, "vida": 60, "vel": 6, "tipo": "laser", "daño": 150, "cooldown": 1500, "costo": 7}
}

nave_seleccionada = 0; monedas_totales = 0; mejoras = {0:0, 1:0, 2:0, 3:0, 4:0}
kenzo_renacido = False 

def cargar_sonido(n):
    try: return pygame.mixer.Sound(n)
    except: return None

sonido_explosion = cargar_sonido("explosion.ogg"); sonido_moneda = cargar_sonido("coin.ogg")
sonido_gameover = cargar_sonido("gameover.ogg"); sonido_victoria = cargar_sonido("win.ogg")
sonido_powerup = cargar_sonido("powerup.ogg"); sonido_bomba = cargar_sonido("bomba.ogg")
sonido_kenzo_malo = cargar_sonido("final.ogg")
sonidos_disparos = {"normal": cargar_sonido("laser_normal.ogg"), "rapida": cargar_sonido("laser_rapido.ogg"),
                    "pesada": cargar_sonido("laser_pesado.ogg"), "triple": cargar_sonido("laser_escopeta.ogg"),
                    "laser": cargar_sonido("laser_sniper.ogg"), "auto": cargar_sonido("laser_auto.ogg")}

def cambiar_musica(archivo):
    try:
        if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
        pygame.mixer.music.load(archivo)
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1) 
    except: pass

class Jugador(pygame.sprite.Sprite):
    def __init__(self, info, nivel):
        super().__init__()
        self.info = info; self.nivel = nivel; self.image = self.info["img"]
        self.rect = self.image.get_rect(); self.rect.centerx = ANCHO//2; self.rect.bottom = ALTO-10
        self.vida_max = int(self.info["vida"] * (1+self.nivel*0.2)); self.vida = self.vida_max
        self.velocidad = self.info["vel"] * (1+self.nivel*0.05); self.daño_actual = int(self.info["daño"] * (1+self.nivel*0.15))
        self.cooldown_actual = int(self.info["cooldown"] * max(0.2, 1-(self.nivel*0.10)))
        self.monedas_partida = 0; self.ultimo_disparo = 0; self.bombas = 3
        self.powerup_doble = False; self.tiempo_powerup = 0

    def update(self):
        if self.powerup_doble and pygame.time.get_ticks()-self.tiempo_powerup > 5000: self.powerup_doble = False
        t = pygame.key.get_pressed()
        if t[pygame.K_LEFT]: self.rect.x -= self.velocidad
        if t[pygame.K_RIGHT]: self.rect.x += self.velocidad
        if t[pygame.K_UP]: self.rect.y -= self.velocidad
        if t[pygame.K_DOWN]: self.rect.y += self.velocidad
        if t[pygame.K_SPACE]: self.intentar_disparar()
        if self.rect.right > ANCHO: self.rect.right = ANCHO
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.bottom > ALTO: self.rect.bottom = ALTO
        if self.rect.top < 0: self.rect.top = 0

    def intentar_disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.cooldown_actual:
            self.ultimo_disparo = ahora; self.crear_balas()
            if s := sonidos_disparos.get(self.info["tipo"]): s.play()

    def crear_balas(self):
        tipo = self.info["tipo"]; d = self.daño_actual; c = self.info["color"]
        if self.powerup_doble:
            if tipo == "triple": [balas_jugador.add(Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)) for i in range(-2, 3)]
            else: balas_jugador.add(Bala(self.rect.left, self.rect.top, 0, -14, c, d), Bala(self.rect.right, self.rect.top, 0, -14, c, d))
        else:
            if tipo in ["normal","rapida","pesada"]: balas_jugador.add(Bala(self.rect.centerx, self.rect.top, 0, -10, AMARILLO, d))
            elif tipo == "triple": [balas_jugador.add(Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)) for i in range(-1, 2)]
            elif tipo == "laser": balas_jugador.add(Bala(self.rect.centerx, self.rect.top, 0, -25, ROJO, d))
            elif tipo == "auto": balas_jugador.add(Bala(self.rect.centerx+random.randrange(-5,6), self.rect.top, 0, -14, AMARILLO, d))
        all_sprites.add(*balas_jugador.sprites())
    
    def activar_doble_disparo(self): self.powerup_doble = True; self.tiempo_powerup = pygame.time.get_ticks()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.tipo = random.choice(['vida', 'doble']); self.image = pygame.Surface((30, 30))
        if self.tipo == 'vida': self.image.fill(ROJO); pygame.draw.rect(self.image, BLANCO, (10, 5, 10, 20)); pygame.draw.rect(self.image, BLANCO, (5, 10, 20, 10))
        else: self.image.fill(AZUL); pygame.draw.circle(self.image, BLANCO, (15, 15), 10, 2)
        self.rect = self.image.get_rect(center=center); self.speedy = 3
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > ALTO: self.kill()

class EnemigoBasico(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_asteroide; self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width); self.rect.y = random.randrange(-100, -40)
        self.velocidad_y = random.randrange(2, 5); self.vida = 40 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()

class NaveEnemiga(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = img_enemigo; self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width); self.rect.y = random.randrange(-150, -50)
        self.velocidad_y = random.randrange(1, 3); self.vida = 80 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()
        if random.randrange(0, 100) < 1: 
            b = BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 5)
            all_sprites.add(b); balas_enemigas.add(b)

class Boss(pygame.sprite.Sprite):
    def __init__(self, jugador_obj, tipo="alien", info_team=None):
        super().__init__()
        self.tipo = tipo; self.jugador = jugador_obj; self.entrando = True; self.info = info_team
        
        if tipo == "alien":
            self.image = img_jefe1
            self.vida = 2500; self.vida_max = 2500; self.velocidad_movimiento = 2
        elif tipo == "kenzo":
            self.image = pygame.transform.scale(img_kenzo_malo, (130, 140))
            self.vida = 4000; self.vida_max = 4000; self.velocidad_movimiento = 3
        elif tipo == "teammate":
            img_escalada = pygame.transform.scale(info_team["img"], (70, 70))
            self.image = pygame.transform.rotate(img_escalada, 180)
            self.vida = 1000; self.vida_max = 1000; self.velocidad_movimiento = random.choice([2, 3])

        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(100, ANCHO-100) if tipo=="teammate" else ANCHO//2
        self.rect.y = -150; self.cooldown_disparo = 0; self.destino_x = self.rect.centerx; self.destino_y = random.randint(50, 150)

    def update(self):
        cooldown_base = 60
        if self.tipo == "alien":
            if self.vida <= self.vida_max / 2: self.image = img_jefe2; self.velocidad_movimiento = 4; cooldown_base = 40
        elif self.tipo == "kenzo": cooldown_base = 35
        elif self.tipo == "teammate": cooldown_base = 80

        if self.entrando:
            self.rect.y += 2
            if self.rect.y >= 50: self.entrando = False
        else:
            dx = self.destino_x - self.rect.centerx; dy = self.destino_y - self.rect.centery
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 5:
                self.rect.centerx += int(dx/dist * self.velocidad_movimiento)
                self.rect.centery += int(dy/dist * self.velocidad_movimiento)
            else:
                self.destino_x = random.randint(50, ANCHO - 50); self.destino_y = random.randint(50, ALTO // 2)
            self.cooldown_disparo += 1
            if self.cooldown_disparo >= cooldown_base: self.atacar(); self.cooldown_disparo = 0
                
    def atacar(self):
        if self.tipo == "teammate": ataque = random.choice(["simple", "dirigido"])
        elif self.tipo == "kenzo": ataque = random.choice(["rafaga", "circular", "dirigido"])
        else: ataque = random.choice(["simple", "rafaga"]) if self.vida > self.vida_max/2 else random.choice(["circular", "dirigido"])

        if ataque == "simple":
            balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 8))
        elif ataque == "rafaga":
            [balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.bottom, i*2, 6)) for i in range(-2, 3)]
        elif ataque == "circular":
            for i in range(12):
                r = math.radians((360/12)*i); balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.centery, 5*math.cos(r), 5*math.sin(r)))
        elif ataque == "dirigido":
            dx = self.jugador.rect.centerx - self.rect.centerx; dy = self.jugador.rect.centery - self.rect.centery
            d = math.sqrt(dx**2 + dy**2)
            if d > 0: balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.centery, (dx/d)*8, (dy/d)*8))
        all_sprites.add(*balas_enemigas.sprites())

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, sx, sy, c, dmg):
        super().__init__(); self.image = pygame.Surface((6, 16)); self.image.fill(c)
        self.rect = self.image.get_rect(centerx=x, bottom=y); self.sx = sx; self.sy = sy; self.damage = dmg 
    def update(self):
        self.rect.y += self.sy; self.rect.x += self.sx
        if self.rect.bottom < 0: self.kill()

class BalaEnemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, sx, sy):
        super().__init__(); self.image = pygame.Surface((8, 8)); self.image.fill(NARANJA)
        self.rect = self.image.get_rect(centerx=int(x), top=int(y)); self.x = float(x); self.y = float(y); self.sx = sx; self.sy = sy
    def update(self):
        self.x += self.sx; self.y += self.sy; self.rect.centerx = int(self.x); self.rect.centery = int(self.y)
        if not PANTALLA.get_rect().colliderect(self.rect): self.kill()

class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(); self.image = img_moneda; self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.y += 3
        if self.rect.top > ALTO: self.kill()

def dibujar_texto(pantalla, texto, tamaño, x, y, color=BLANCO, con_sombra=False):
    f = pygame.font.SysFont("arial", tamaño, bold=True)
    if con_sombra: pantalla.blit(f.render(texto, True, NEGRO), (x - f.size(texto)[0]//2 + 2, y + 2))
    s = f.render(texto, True, color); pantalla.blit(s, s.get_rect(midtop=(x, y)))

def dibujar_texto_con_fondo(pantalla, texto, tamaño, x, y, color=BLANCO):
    f = pygame.font.SysFont("arial", tamaño, bold=True); s = f.render(texto, True, color); r = s.get_rect(midtop=(x, y))
    bg = pygame.Surface((r.width + 20, r.height + 10)); bg.fill(NEGRO); bg.set_alpha(180)
    pantalla.blit(bg, bg.get_rect(center=r.center)); pantalla.blit(s, r)

def dibujar_boton(pantalla, texto, x, y, w, h, c_base, c_hover, clic=False):
    rect = pygame.Rect(x, y, w, h); hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(pantalla, c_hover if hover else c_base, rect); pygame.draw.rect(pantalla, BLANCO, rect, 2)
    dibujar_texto(pantalla, texto, 18, x + w//2, y + 10, NEGRO)
    return True if hover and clic else False

def spawn_enemigos(c):
    for _ in range(c):
        e = EnemigoBasico() if random.random() > 0.5 else NaveEnemiga()
        all_sprites.add(e); enemigos.add(e)

def reiniciar_partida():
    global all_sprites, enemigos, balas_jugador, balas_enemigas, monedas, grupo_boss, powerups, jugador, score, boss_activo
    all_sprites, enemigos, balas_jugador, balas_enemigas, monedas, grupo_boss, powerups = [pygame.sprite.Group() for _ in range(7)]
    jugador = Jugador(NAVES_INFO[nave_seleccionada], mejoras[nave_seleccionada]); all_sprites.add(jugador)
    score = 0; boss_activo = False; spawn_enemigos(8); pygame.mixer.stop()

# --- CINEMÁTICAS CON DIÁLOGOS MEJORADOS ---
async def animacion_dialogos(guion):
    i = 0
    while i < len(guion):
        RELOJ.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_SPACE, pygame.K_RETURN]: i += 1
        if i >= len(guion): break
        escena = guion[i]; act = escena["activos"]
        PANTALLA.blit(img_itesco_noche if "aliens" in act or "malo" in act else img_itesco, (0, 0))
        if "kenzo" in act: PANTALLA.blit(img_kenzo, (480, 300))
        if "dibanhi" in act: PANTALLA.blit(img_dibanhi, (180, 300))
        if "santiago" in act: PANTALLA.blit(img_santiago, (330, 300))
        if "belen" in act: PANTALLA.blit(img_belen, (630, 300))
        if "moises" in act: PANTALLA.blit(img_moises, (30, 300))
        if "aliens" in act: PANTALLA.blit(img_enemigo_intro, (ANCHO//2 - 75, 50))
        if "malo" in act: PANTALLA.blit(img_kenzo_malo, (ANCHO//2 - 75, 100))

        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO - 100, ANCHO, 100))
        pygame.draw.rect(PANTALLA, ROJO if "malo" in act else BLANCO, (0, ALTO - 100, ANCHO, 100), 3)
        dibujar_texto(PANTALLA, escena["texto"], 20, ANCHO//2, ALTO - 70, ROJO if "malo" in act else BLANCO)
        dibujar_texto(PANTALLA, "[ESPACIO para continuar]", 16, ANCHO - 100, ALTO - 20, AMARILLO)
        pygame.display.flip(); await asyncio.sleep(0)

async def animacion_intro():
    await animacion_dialogos([
        {"texto": "Kenzo: ¿Alguien vio mi USB? ¡Traigo todo el proyecto final ahí!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Dibanhi: No me digas que Moy la trae... ¡Ese wey siempre llega tarde!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Santiago: ¡Si reprobamos por su culpa lo voy a reprobar de la vida!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "Belen: ¡Cállense! ¿Qué es esa cosa enorme que está tapando el sol?", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "ALIENS: ¡ATENCIÓN HUMANOS INFERIORES! ¡LOS SERVIDORES DEL ITESCO AHORA SON NUESTROS!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "Santiago: ¡No manches! ¡Ahí estaban mis prácticas de la nube!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "Moises: ¡Banda, perdón por la tardanza! Vi al Inge Bulmaro escondiendo esto...", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Moises: Trajes espaciales y naves armadas hasta los dientes. ¿Están chidas, no?", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Dibanhi: ¡Moy, deja de jugar! ¡Los aliens nos están invadiendo!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Todos: ¡A LAS NAVES! ¡HOY NO REPROBAMOS, HOY SALVAMOS EL SEMESTRE!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]}
    ])
    return "seleccion"

async def animacion_pre_jefe_alien():
    img_grande = pygame.transform.scale(img_jefe1, (300, 200)); cambiar_musica("musica_jefe.ogg"); i = 0
    guion = [
        {"t": "BOSS: ¡JAJAJA! ¿Creen que unas navecitas de chatarra escolar pueden vencerme?", "h": "j"},
        {"t": "BOSS: ¡Soy el destructor de galaxias! ¡Su viaje termina aquí, mediocres!", "h": "j"}, 
        {"t": "Moises: Uy, qué carácter... ¿No prefieres un cafecito de la cafetería primero?", "h": "t"},
        {"t": "Todos: ¡PREPÁRATE PARA SENTIR LA IRA DEL EQUIPO 2! ¡POR EL ITESCO!", "h": "t"}
    ]
    while i < len(guion):
        RELOJ.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: i += 1
        if i >= len(guion): break
        PANTALLA.blit(img_fondo_jefe, (0, 0)) if img_fondo_jefe else PANTALLA.fill(NEGRO)
        if guion[i]["h"] == "j":
            img_grande.set_alpha(255 if pygame.time.get_ticks()%1000<500 else 200); PANTALLA.blit(img_grande, (ANCHO-350, 150))
        else:
            PANTALLA.blit(img_kenzo, (20,300)); PANTALLA.blit(img_dibanhi, (120,300)); PANTALLA.blit(img_santiago, (220,300)); PANTALLA.blit(img_moises, (420,300))
        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO-120, ANCHO, 120)); pygame.draw.rect(PANTALLA, AZUL, (0, ALTO-120, ANCHO, 120), 4) 
        dibujar_texto(PANTALLA, guion[i]["t"], 26, ANCHO//2, ALTO-80, BLANCO); pygame.display.flip(); await asyncio.sleep(0)

async def animacion_pre_jefe_equipo():
    await animacion_dialogos([
        {"texto": "Kenzo (Renacido): Vaya, vaya... Miren quiénes vinieron a arrastrarse a mis pies.", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Moises: ¡Kenzo, hermano, reacciona! ¡Ese alien te está lavando el cerebro!", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Kenzo (Renacido): ¿Cerebro? Ahora tengo el conocimiento de mil galaxias. Ustedes son insectos.", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Kenzo (Renacido): ¡PREPÁRENSE PARA SER BORRADOS DEL SISTEMA!", "activos": ["malo"]}
    ])

async def animacion_pre_jefe_kenzo():
    await animacion_dialogos([
        {"texto": "Santiago: ¡Ahí está! ¡Es la nave de Kenzo, pero emana una energía oscura!", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Kenzo (Renacido): Pobres tontos... Vienen a salvar a un amigo que ya no existe.", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Belen: ¡Te sacaremos a ese parásito a punta de láseres si es necesario, traidor!", "activos": ["malo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Kenzo (Renacido): ¡INTÉNTENLO! ¡SU DESTRUCCIÓN SERÁ MI PRIMER LOGRO!", "activos": ["malo"]}
    ])

# --- VUELVE EL EFECTO DE ACERCAMIENTO Y TEMBLOR PARA KENZO MALO ---
async def animacion_epilogo_normal():
    global kenzo_renacido
    cambiar_musica("final.ogg")
    kenzo_mirando = pygame.transform.flip(img_kenzo, True, False)
    jefe_muriendo = pygame.transform.scale(img_jefe2.copy(), (200, 150))
    jefe_muriendo.set_alpha(150)
    zoom_kenzo = 1.0
    alpha_negro = 0

    guion = [
        {"texto": "Kenzo: ¡Lo logramos! ¡El ITESCO está a salvo, podemos ir a comer tranquilos!", "estado": "normal"},
        {"texto": "BOSS: *Cof, cof*... ¿A salvo? Pobres criaturas ignorantes...", "estado": "normal"},
        {"texto": "BOSS: Mi armadura limitaba mi verdadera forma... y acaban de liberarla.", "estado": "normal"},
        {"texto": "Kenzo: ¿De qué hablas, monstruo? ¡Tu energía se está desvaneciendo!", "estado": "normal"},
        {"texto": "BOSS: ¡AL CONTRARIO! ¡AHORA TU CUERPO ES MÍO!", "estado": "absorcion"},
        {"texto": "Kenzo: ¡NO! ¡SAL DE MI CABEZA! ¡AAAAAGHHH! ¡QUEMA!", "estado": "absorcion"},
        {"texto": "...", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Silencio... Al fin, ya no hay dolor. Ni tareas, ni estrés.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Kenzo era débil. Lloraba por un simple examen.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Ahora veo la verdad. Este mundo es solo combustible.", "estado": "malo"},
        {"texto": "Kenzo (Renacido): Corran, amigos míos... EL VERDADERO JUEGO APENAS COMIENZA.", "estado": "malo"}
    ]

    indice = 0
    while indice < len(guion):
        RELOJ.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: pygame.quit(); exit()
            if evento.type == pygame.KEYDOWN and evento.key in [pygame.K_SPACE, pygame.K_RETURN]: indice += 1

        if indice >= len(guion): break
        escena = guion[indice]
        estado = escena["estado"]

        if img_fondo_jefe: PANTALLA.blit(img_fondo_jefe, (0, 0))
        else: PANTALLA.fill(NEGRO)

        if estado == "normal":
            PANTALLA.blit(kenzo_mirando, (200, ALTO - 250)); PANTALLA.blit(jefe_muriendo, (ANCHO - 300, 100))
        elif estado == "absorcion":
            # Efecto de temblor
            PANTALLA.blit(kenzo_mirando, (200 + random.randint(-8, 8), ALTO - 250 + random.randint(-8, 8)))
            if pygame.time.get_ticks() % 200 < 100: PANTALLA.blit(jefe_muriendo, (ANCHO - 300, 100))
            # Efecto de destello rojo
            filtro = pygame.Surface((ANCHO, ALTO)); filtro.fill(ROJO); filtro.set_alpha(80); PANTALLA.blit(filtro, (0,0))
        elif estado == "malo":
            # Efecto de oscurecimiento y ZOOM dramático
            alpha_negro = min(220, alpha_negro + 3)
            sombra = pygame.Surface((ANCHO, ALTO)); sombra.fill(NEGRO); sombra.set_alpha(alpha_negro); PANTALLA.blit(sombra, (0,0))
            zoom_kenzo = min(3.5, zoom_kenzo + 0.008) 
            kenzo_g = pygame.transform.scale(img_kenzo_malo, (int(img_kenzo_malo.get_width() * zoom_kenzo), int(img_kenzo_malo.get_height() * zoom_kenzo)))
            PANTALLA.blit(kenzo_g, kenzo_g.get_rect(center=(ANCHO//2, ALTO//2)))

        color_borde = ROJO if estado in ["absorcion", "malo"] else AZUL
        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO - 100, ANCHO, 100))
        pygame.draw.rect(PANTALLA, color_borde, (0, ALTO - 100, ANCHO, 100), 3)
        dibujar_texto(PANTALLA, escena["texto"], 22, ANCHO//2, ALTO - 70, ROJO if estado == "malo" else BLANCO)
        dibujar_texto(PANTALLA, "[CONTINUAR]", 16, ANCHO - 100, ALTO - 20, GRIS)
        pygame.display.flip(); await asyncio.sleep(0)

    kenzo_renacido = True
    NAVES_INFO[2]["nombre"] = "Kenzo (Renacido)"; NAVES_INFO[2]["img"] = img_nave_renacida
    NAVES_INFO[2]["vida"] = 500; NAVES_INFO[2]["daño"] = 100; NAVES_INFO[2]["cooldown"] = 300; NAVES_INFO[2]["vel"] = 6
    pygame.mixer.music.stop(); return "seleccion"

async def animacion_epilogo_salvar_kenzo():
    global kenzo_renacido; cambiar_musica("final.ogg")
    await animacion_dialogos([
        {"texto": "Moises: ¡LE DIMOS! ¡Los escudos de la nave cayeron! ¡Rápido!", "activos": ["dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Dibanhi: ¡Miren! ¡Esa asquerosa luz morada está saliendo de su cuerpo!", "activos": ["dibanhi", "santiago", "belen", "moises", "aliens"]},
        {"texto": "ALIENS: ¡MALDITOS HUMANOS! ¡ESTO NO SE QUEDARÁ ASÍ! ¡VOLVEREMOS!", "activos": ["aliens"]},
        {"texto": "Kenzo: Agh... Mi cabeza... Siento como si hubiera reprobado tutorias tres veces seguidas.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Todos: ¡KENZO! ¡ESTÁS VIVO! ¡LO LOGRAMOS!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]},
        {"texto": "Kenzo: Gracias, chicos... Creo que ahora sí merecemos ese 10 con el profe.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]}
    ])
    kenzo_renacido = False
    NAVES_INFO[2]["nombre"] = "Kenzo"; NAVES_INFO[2]["img"] = img_nave3
    NAVES_INFO[2]["vida"] = 250; NAVES_INFO[2]["daño"] = 45; NAVES_INFO[2]["cooldown"] = 600; NAVES_INFO[2]["vel"] = 3
    pygame.mixer.music.stop(); return "seleccion"

async def animacion_epilogo_kenzo_gana():
    cambiar_musica("final.ogg")
    await animacion_dialogos([
        {"texto": "Kenzo (Renacido): Patéticos... Se los advertí. Sus lazos de amistad los hicieron débiles.", "activos": ["malo"]},
        {"texto": "Kenzo (Renacido): Sus naves son chatarra. Ahora el servidor central del ITESCO me pertenece.", "activos": ["malo"]},
        {"texto": "Kenzo (Renacido): Y con esta tecnología de la Nube...", "activos": ["malo"]},
        {"texto": "Kenzo (Renacido): ¡DOMINARÉ HASTA LA ÚLTIMA ESTRELLA DE LA GALAXIA!", "activos": ["malo"]}
    ])
    pygame.mixer.music.stop(); return "seleccion"

async def menu_principal():
    cambiar_musica("musica_menu.ogg") 
    while True:
        RELOJ.tick(FPS); clic = False 
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True 
        PANTALLA.blit(img_fondo_inicio, (0, 0)) if img_fondo_inicio else PANTALLA.fill(NEGRO)
        dibujar_texto_con_fondo(PANTALLA, "ITESCO EN EL ESPACIO", 50, ANCHO//2, 100, AZUL)
        
        if dibujar_boton(PANTALLA, "INICIAR JUEGO", ANCHO//2 - 100, 250, 200, 50, VERDE, BLANCO, clic): return "intro" 
        if dibujar_boton(PANTALLA, "SALIR", ANCHO//2 - 100, 350, 200, 50, ROJO, BLANCO, clic): pygame.quit(); exit()
        pygame.display.flip(); await asyncio.sleep(0) 

async def menu_seleccion():
    global nave_seleccionada, monedas_totales
    if not pygame.mixer.music.get_busy(): cambiar_musica("musica_menu.ogg") 
    while True:
        RELOJ.tick(FPS); clic = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True
        PANTALLA.fill(NEGRO)
        dibujar_texto(PANTALLA, "TIENDA DE NAVES", 40, ANCHO//2, 10, BLANCO, con_sombra=True)
        dibujar_texto(PANTALLA, f"Tus Monedas: {monedas_totales}", 25, ANCHO - 150, 20, AMARILLO)

        for i in range(5):
            info = NAVES_INFO[i]; lvl = mejoras[i]; x = 50 + (i%3)*250; y = 80 + (i//3)*240
            if i == nave_seleccionada: pygame.draw.rect(PANTALLA, BLANCO, (x-5, y-5, 210, 220), 3)
            pygame.draw.rect(PANTALLA, GRIS, (x, y, 200, 210)); PANTALLA.blit(info["img"], info["img"].get_rect(center=(x+100, y+30)))
            
            c_nombre = ROJO if kenzo_renacido and i==2 else BLANCO
            dibujar_texto(PANTALLA, f"{info['nombre']} (Nvl {lvl})", 20, x+100, y+55, c_nombre)
            dibujar_texto(PANTALLA, f"Daño: {int(info['daño']*(1+lvl*0.15))} -> {int(info['daño']*(1+(lvl+1)*0.15))}", 16, x+100, y+80, VERDE_CLARO)
            dibujar_texto(PANTALLA, f"Rapidez: {int(info['cooldown']*max(0.2, 1-lvl*0.1))}ms -> {int(info['cooldown']*max(0.2, 1-(lvl+1)*0.1))}ms", 16, x+100, y+100, VERDE_CLARO)
            
            costo = info["costo"] * (lvl + 1)
            if dibujar_boton(PANTALLA, "Elegir", x+10, y+140, 80, 30, VERDE, BLANCO, clic): nave_seleccionada = i
            if dibujar_boton(PANTALLA, f"Mejorar (${costo})", x+100, y+140, 90, 30, AMARILLO, BLANCO, clic) and monedas_totales >= costo:
                monedas_totales -= costo; mejoras[i] += 1
        
        if dibujar_boton(PANTALLA, "¡A VOLAR!", ANCHO//2 - 100, 550, 200, 40, AZUL, BLANCO, clic): reiniciar_partida(); return "juego"
        pygame.display.flip(); await asyncio.sleep(0) 

async def ciclo_juego():
    global score, boss_activo, monedas_totales; flash_frames = 0; trigger_boss = False 

    while True:
        RELOJ.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_b and not boss_activo: trigger_boss = True 
                if e.key == pygame.K_t and jugador.bombas > 0:
                    jugador.bombas -= 1; flash_frames = 3
                    if sonido_bomba: sonido_bomba.play()
                    for en in list(enemigos):
                        en.vida -= 1000
                        if en.vida <= 0: en.kill(); score += 10
                    for b in grupo_boss: b.vida -= 500
                if e.key == pygame.K_f: 
                    pygame.mixer.music.stop()
                    if kenzo_renacido: return "victoria_kenzo_gana" if nave_seleccionada == 2 else "victoria_salvar_kenzo"
                    else: return "victoria_normal"

        PANTALLA.blit(img_fondo_jefe if boss_activo else img_fondo_juego, (0, 0)) if (img_fondo_jefe or img_fondo_juego) else PANTALLA.fill(NEGRO)
        all_sprites.update()
        if not boss_activo and len(enemigos) < 8: spawn_enemigos(8 - len(enemigos))
        
        if (trigger_boss or score >= 100) and not boss_activo:
            boss_activo = True; trigger_boss = False; para_borrar = list(enemigos)
            for en in para_borrar: en.kill() 
            
            if kenzo_renacido and nave_seleccionada == 2:
                await animacion_pre_jefe_equipo()
                for i in [0, 1, 3, 4]:
                    b = Boss(jugador, "teammate", NAVES_INFO[i]); all_sprites.add(b); grupo_boss.add(b)
            elif kenzo_renacido and nave_seleccionada != 2:
                await animacion_pre_jefe_kenzo()
                b = Boss(jugador, "kenzo"); all_sprites.add(b); grupo_boss.add(b)
            else:
                await animacion_pre_jefe_alien()
                b = Boss(jugador, "alien"); all_sprites.add(b); grupo_boss.add(b)
            cambiar_musica("musica_jefe.ogg")

        for enemigo, l_balas in pygame.sprite.groupcollide(enemigos, balas_jugador, False, True).items():
            for bala in l_balas:
                enemigo.vida -= bala.damage
                if enemigo.vida <= 0:
                    enemigo.kill(); score += 10
                    if sonido_explosion: sonido_explosion.play()
                    if random.random() > 0.9: p = PowerUp(enemigo.rect.center); all_sprites.add(p); powerups.add(p)
                    elif random.random() > 0.6: m = Moneda(enemigo.rect.centerx, enemigo.rect.centery); all_sprites.add(m); monedas.add(m)

        for p in pygame.sprite.spritecollide(jugador, powerups, True):
            if sonido_powerup: sonido_powerup.play()
            if p.tipo == 'vida': jugador.vida = min(jugador.vida_max, jugador.vida + 30)
            elif p.tipo == 'doble': jugador.activar_doble_disparo()

        if boss_activo:
            for boss_obj, l_balas in pygame.sprite.groupcollide(grupo_boss, balas_jugador, False, True).items():
                for bala in l_balas: boss_obj.vida -= bala.damage
                if boss_obj.vida <= 0: boss_obj.kill()
            
            if len(grupo_boss) == 0:
                score += 5000; monedas_totales += jugador.monedas_partida + 200; pygame.mixer.music.stop()
                if kenzo_renacido: return "victoria_kenzo_gana" if nave_seleccionada == 2 else "victoria_salvar_kenzo"
                else: return "victoria_normal"

        if pygame.sprite.spritecollide(jugador, enemigos, True): jugador.vida -= 20
        if pygame.sprite.spritecollide(jugador, balas_enemigas, True): jugador.vida -= 10
        if pygame.sprite.spritecollide(jugador, grupo_boss, False): jugador.vida -= 5

        if jugador.vida <= 0: monedas_totales += jugador.monedas_partida; pygame.mixer.music.stop(); return "game_over"

        for m in pygame.sprite.spritecollide(jugador, monedas, True):
            jugador.monedas_partida += 1; sonido_moneda.play() if sonido_moneda else None

        all_sprites.draw(PANTALLA)
        dibujar_texto(PANTALLA, f"Nave: {jugador.info['nombre']} (Lvl {jugador.nivel})", 20, 100, 10)
        dibujar_texto(PANTALLA, f"Puntos: {score}", 20, ANCHO//2, 10)
        dibujar_texto(PANTALLA, f"Monedas: {jugador.monedas_partida}", 20, ANCHO-80, 10)
        dibujar_texto(PANTALLA, f"Bombas [T]: {jugador.bombas}", 20, 100, 40, VERDE_CLARO)
        if jugador.powerup_doble: dibujar_texto(PANTALLA, "¡DOBLE DISPARO!", 20, ANCHO//2, 40, CYAN)

        l_v = 200; act = (max(0, jugador.vida) / jugador.vida_max) * l_v
        pygame.draw.rect(PANTALLA, ROJO, (10, 70, l_v, 15)); pygame.draw.rect(PANTALLA, VERDE, (10, 70, act, 15))
        pygame.draw.rect(PANTALLA, BLANCO, (10, 70, l_v, 15), 2)

        if boss_activo:
            nombre_jefe = "¡EQUIPO ENEMIGO!" if (kenzo_renacido and nave_seleccionada==2) else ("¡KENZO RENACIDO!" if kenzo_renacido else "¡JEFE ALIEN!")
            dibujar_texto(PANTALLA, nombre_jefe, 30, ANCHO//2, 60, con_sombra=True)
            if len(grupo_boss) > 0:
                b_repr = grupo_boss.sprites()[0]
                pygame.draw.rect(PANTALLA, MORADO, (ANCHO//2-100, 90, (max(0, b_repr.vida)/b_repr.vida_max)*200, 20))

        if flash_frames > 0: PANTALLA.fill(BLANCO); flash_frames -= 1

        pygame.display.flip(); await asyncio.sleep(0) 

async def pantalla_fin(tipo):
    global score
    es_vic = tipo.startswith("victoria")
    c_titulo = VERDE if es_vic else ROJO
    txt_titulo = "¡MISIÓN COMPLETADA!" if es_vic else "NAVE DESTRUIDA"
    
    if tipo == "victoria_kenzo_gana": img_bg = img_fondo_win_kenzo
    elif es_vic: img_bg = img_fondo_win
    else: img_bg = img_fondo_gameover

    if es_vic and sonido_victoria: sonido_victoria.play()
    elif not es_vic and sonido_gameover: sonido_gameover.play()

    while True:
        RELOJ.tick(FPS); clic = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True

        PANTALLA.blit(img_bg, (0, 0)) if img_bg else PANTALLA.fill(NEGRO)
        off_y = 150 if img_bg else 0 

        dibujar_texto_con_fondo(PANTALLA, txt_titulo, 50, ANCHO//2, 100+off_y, c_titulo)
        dibujar_texto_con_fondo(PANTALLA, f"Puntaje Final: {score}", 30, ANCHO//2, 200+off_y)
        dibujar_texto_con_fondo(PANTALLA, f"Monedas Ganadas: {jugador.monedas_partida}", 30, ANCHO//2, 250+off_y, AMARILLO)
        
        if dibujar_boton(PANTALLA, "CONTINUAR..." if es_vic else "IR A LA TIENDA", ANCHO//2-100, 350+off_y, 200, 50, AZUL, BLANCO, clic):
             pygame.mixer.stop() 
             if tipo == "victoria_normal": return "epilogo_normal"
             elif tipo == "victoria_kenzo_gana": return "epilogo_kenzo_gana"
             elif tipo == "victoria_salvar_kenzo": return "epilogo_salvar_kenzo"
             else: return "seleccion"

        pygame.display.flip(); await asyncio.sleep(0) 

async def main():
    estado_actual = "menu"
    while True:
        if estado_actual == "menu": estado_actual = await menu_principal()
        elif estado_actual == "seleccion": estado_actual = await menu_seleccion()
        elif estado_actual == "intro": estado_actual = await animacion_intro()
        elif estado_actual == "juego": estado_actual = await ciclo_juego()
        elif estado_actual == "game_over": estado_actual = await pantalla_fin("derrota")
        elif estado_actual == "victoria_normal": estado_actual = await pantalla_fin("victoria_normal")
        elif estado_actual == "victoria_kenzo_gana": estado_actual = await pantalla_fin("victoria_kenzo_gana")
        elif estado_actual == "victoria_salvar_kenzo": estado_actual = await pantalla_fin("victoria_salvar_kenzo")
        elif estado_actual == "epilogo_normal": estado_actual = await animacion_epilogo_normal()
        elif estado_actual == "epilogo_kenzo_gana": estado_actual = await animacion_epilogo_kenzo_gana()
        elif estado_actual == "epilogo_salvar_kenzo": estado_actual = await animacion_epilogo_salvar_kenzo()
        await asyncio.sleep(0)

asyncio.run(main())