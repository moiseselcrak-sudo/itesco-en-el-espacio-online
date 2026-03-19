import pygame
import random
import math 
import asyncio 
import uuid 

pygame.init()
pygame.mixer.init()

ANCHO = 800
ALTO = 600
PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("DEFENDIENDO LA RED DE ITESCO")
RELOJ = pygame.time.Clock()
FPS = 60

# --- PALETA DE COLORES CIBERNETICOS ---
NEGRO = (0, 0, 0); BLANCO = (255, 255, 255); VERDE = (0, 255, 0)
ROJO = (255, 0, 0); AZUL = (0, 0, 255); AMARILLO = (255, 255, 0)
MORADO = (128, 0, 128); NARANJA = (255, 165, 0); CYAN = (0, 255, 255)
GRIS = (50, 50, 50); VERDE_CLARO = (144, 238, 144); GRIS_OSCURO = (20, 20, 35)

# =====================================================================
# 1. FUNCIONES DE DIBUJO Y PRONOMBRES DINÁMICOS
# =====================================================================
# Función para detectar género: retorna "a" para mujeres, "o" para hombres
def oa(nombre): return "a" if nombre in ["belen", "dibanhi"] else "o"
def OA(nombre): return "A" if nombre in ["belen", "dibanhi"] else "O"

def dibujar_texto(pantalla, texto, tamaño, x, y, color=BLANCO, con_sombra=False, max_width=None):
    f = pygame.font.SysFont("arial", tamaño, bold=True)
    if max_width:
        words = str(texto).split(' '); lines = []; current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if f.size(test_line)[0] <= max_width: current_line.append(word)
            else: lines.append(' '.join(current_line)); current_line = [word]
        lines.append(' '.join(current_line))
        current_y = y
        for line in lines:
            if con_sombra: pantalla.blit(f.render(line, True, NEGRO), (x - f.size(line)[0]//2 + 2, current_y + 2))
            s = f.render(line, True, color); pantalla.blit(s, s.get_rect(midtop=(x, current_y)))
            current_y += f.get_height()
    else:
        if con_sombra: pantalla.blit(f.render(texto, True, NEGRO), (x - f.size(texto)[0]//2 + 2, y + 2))
        s = f.render(texto, True, color); pantalla.blit(s, s.get_rect(midtop=(x, y)))

def dibujar_texto_con_fondo(pantalla, texto, tamaño, x, y, color=BLANCO, bg_color=NEGRO):
    f = pygame.font.SysFont("arial", tamaño, bold=True); s = f.render(texto, True, color); r = s.get_rect(midtop=(x, y))
    bg = pygame.Surface((r.width + 20, r.height + 10)); bg.fill(bg_color); bg.set_alpha(200)
    pantalla.blit(bg, bg.get_rect(center=r.center)); pantalla.blit(s, r)

def dibujar_boton(pantalla, texto, x, y, w, h, c_base, c_hover, clic=False):
    rect = pygame.Rect(x, y, w, h); hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(pantalla, c_hover if hover else c_base, rect); pygame.draw.rect(pantalla, BLANCO, rect, 2)
    dibujar_texto(pantalla, texto, 18, x + w//2, y + 10, NEGRO)
    return True if hover and clic else False

# =====================================================================
# 2. CARGA DE RECURSOS SEGURA
# =====================================================================
def cargar_fondo(n):
    try: return pygame.transform.scale(pygame.image.load(n), (ANCHO, ALTO))
    except: return None

def cargar_sprite_seguro(nombres, w, h):
    for n in nombres:
        try: return pygame.transform.scale(pygame.image.load(n), (w, h)).convert_alpha()
        except: continue
    s = pygame.Surface((w, h), pygame.SRCALPHA); s.fill((50, 50, 50, 200))
    pygame.draw.rect(s, VERDE, (0, 0, w, h), 2); f = pygame.font.SysFont("arial", 12, bold=True)
    s.blit(f.render(nombres[0][:10], True, VERDE), (5, h//2 - 6)); return s

img_fondo_inicio = cargar_fondo("inicio.png"); img_fondo_juego = cargar_fondo("fondo.png")
img_fondo_jefe = cargar_fondo("fondo_jefe.png")
img_fondo_win = cargar_fondo("win2.png")
img_fondo_win_kenzo = cargar_fondo("kenzo_win.png") 
img_fondo_win_equipo = cargar_fondo("win_equipo.png")
img_fondo_gameover = cargar_fondo("gameover2.png")
img_itesco = cargar_fondo("itesco.png")
img_itesco_noche = cargar_fondo("itesco_noche.png")
img_moneda = pygame.transform.scale(pygame.Surface((25,25)), (25,25)); img_moneda.fill(AMARILLO) 

# NUEVOS FONDOS DE FINAL ABSOLUTO
img_final_total_whitehat = cargar_fondo("whitehat_win.png")
img_final_total_blackhat = cargar_fondo("blackhat_win.png")

NOMBRES = ["moises", "santiago", "kenzo", "dibanhi", "belen"]
NAVES_ORIGINALES = ["nave1.png", "nave2.png", "nave3.png", "nave4.png", "nave5.png"]
POS_X = {"moises": 30, "dibanhi": 180, "santiago": 330, "kenzo": 480, "belen": 630}

SPRITES_SaaS = {}
for i, name in enumerate(NOMBRES):
    SPRITES_SaaS[name] = {
        "historia_normal": cargar_sprite_seguro([f"{name}.png"], 120, 160),
        "historia_blackhat": cargar_sprite_seguro([f"{name}_blackhat.png", f"{name}_malo.png", f"{name}.png"], 120, 160),
        "historia_whitehat": cargar_sprite_seguro([f"{name}_whitehat.png", f"{name}.png"], 120, 160),
        "nave_normal": cargar_sprite_seguro([NAVES_ORIGINALES[i]], 50, 50), 
        "nave_renacida": cargar_sprite_seguro([f"{name}_renacido.png", "nave_renacida.png"], 60, 60),
        # Usa la nave certificada en gameplay, dejando el cuerpo completo para cinematicas
        "nave_certificada": cargar_sprite_seguro([f"{name}_certificado.png", NAVES_ORIGINALES[i]], 50, 50)
    }

img_asteroide = cargar_sprite_seguro(["asteroide.png"], 40, 40)
img_enemigo = pygame.transform.rotate(cargar_sprite_seguro(["enemigo.png"], 40, 40), 180)
img_jefe1 = cargar_sprite_seguro(["jefe1.png"], 150, 100); img_jefe2 = cargar_sprite_seguro(["jefe2.png"], 150, 100)
img_enemigo_intro = cargar_sprite_seguro(["enemigo.png"], 150, 150) 
img_certificado = cargar_sprite_seguro(["certificado.png"], 150, 150)

def cargar_sonido(n):
    try: return pygame.mixer.Sound(n)
    except: return None

sonido_explosion = cargar_sonido("explosion.ogg"); sonido_moneda = cargar_sonido("coin.ogg")
sonido_gameover = cargar_sonido("gameover.ogg"); sonido_victoria = cargar_sonido("win.ogg")
sonido_powerup = cargar_sonido("powerup.ogg"); sonido_bomba = cargar_sonido("bomba.ogg")
sonidos_disparos = {
    "normal": cargar_sonido("laser_normal.ogg"), "rapida": cargar_sonido("laser_rapido.ogg"), 
    "pesada": cargar_sonido("laser_pesado.ogg"), "triple": cargar_sonido("laser_escopeta.ogg"), 
    "laser": cargar_sonido("laser_sniper.ogg"), "auto": cargar_sonido("laser_auto.ogg")
}

def cambiar_musica(archivo):
    try:
        if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
        pygame.mixer.music.load(archivo); pygame.mixer.music.set_volume(0.5); pygame.mixer.music.play(-1) 
    except: pass

# =====================================================================
# 3. LÓGICA DE ESTADO (SaaS STATE MANAGER AVANZADO)
# =====================================================================
STATS_BASE = {
    "normal": {"vida": 100, "daño": 35, "cooldown": 400, "vel": 5, "tipo": "normal"},
    "rapida": {"vida": 70, "daño": 25, "cooldown": 300, "vel": 8, "tipo": "rapida"},
    "pesada": {"vida": 250, "daño": 45, "cooldown": 600, "vel": 3, "tipo": "pesada"},
    "triple": {"vida": 120, "daño": 20, "cooldown": 800, "vel": 5, "tipo": "triple"},
    "laser": {"vida": 60, "daño": 150, "cooldown": 1500, "vel": 6, "tipo": "laser"}
}

NAVES_REPARTIDAS = {
    0: {"id_historia": "moises", "color": VERDE, "stats": STATS_BASE["normal"]},
    1: {"id_historia": "santiago", "color": CYAN, "stats": STATS_BASE["rapida"]},
    2: {"id_historia": "kenzo", "color": AZUL, "stats": STATS_BASE["pesada"]},
    3: {"id_historia": "dibanhi", "color": NARANJA, "stats": STATS_BASE["triple"]},
    4: {"id_historia": "belen", "color": ROJO, "stats": STATS_BASE["laser"]}
}

class SaaSStateManager:
    def __init__(self):
        self.infected_characters = set() 
        self.whitehat_characters = set() 
        self.licencia_valida = False
        self.infection_total = False 
        self.monedas_totales = 0

    def update_factions(self):
        if len(self.infected_characters) > 0:
            self.whitehat_characters = set(NOMBRES) - self.infected_characters
        else:
            self.whitehat_characters.clear()
    
    def make_blackhat(self, name):
        self.infected_characters.add(name); self.update_factions()

    def make_whitehat(self, name):
        if name in self.infected_characters: self.infected_characters.remove(name)
        self.update_factions()

    def cure_all(self):
        self.infected_characters.clear(); self.update_factions()

    def cure_ship_shop(self, name):
        if name in self.infected_characters: self.infected_characters.remove(name)
        self.update_factions()

SaaS_GLOBAL = SaaSStateManager()

def actualizar_naves_segun_estado():
    info_segun_estado = {}
    for i in range(5):
        base_data = NAVES_REPARTIDAS[i]
        char_id = base_data["id_historia"]
        stats_copy = base_data["stats"].copy()
        
        estado = "normal"; nave_img = SPRITES_SaaS[char_id]["nave_normal"]
        color = base_data["color"]; nombre_display = char_id.capitalize()
        
        if char_id in SaaS_GLOBAL.infected_characters:
            stats_copy["daño"] *= 2; stats_copy["vida"] *= 2; stats_copy["cooldown"] = max(100, stats_copy["cooldown"] - 200); stats_copy["vel"] += 1
            estado = "renacida"; nave_img = SPRITES_SaaS[char_id]["nave_renacida"]
            color = MORADO; nombre_display = f"{char_id.capitalize()} [Blackhat]"
            
        elif char_id in SaaS_GLOBAL.whitehat_characters:
            stats_copy["vida"] = int(stats_copy["vida"] * 1.5); stats_copy["daño"] = int(stats_copy["daño"] * 1.3); stats_copy["cooldown"] = max(100, stats_copy["cooldown"] - 80)
            estado = "whitehat"; nave_img = SPRITES_SaaS[char_id]["nave_certificada"] # Usa la nave certificada en gameplay
            color = CYAN; nombre_display = f"{char_id.capitalize()} [Whitehat]"

        info_segun_estado[i] = {
            "nombre": nombre_display, "id_historia": char_id, "img": nave_img,
            "color": color, "stats": stats_copy, "estado": estado,
            "costo_mejora": 5 + (10 if estado == "renacida" else 0),
            "costo_cura": 10 if estado == "renacida" else 0 
        }
    return info_segun_estado

NAVES_INFO = actualizar_naves_segun_estado()
nave_seleccionada = 0; mejoras = {0:0, 1:0, 2:0, 3:0, 4:0}

# =====================================================================
# 4. CLASES DEL JUEGO
# =====================================================================
class Jugador(pygame.sprite.Sprite):
    def __init__(self, info, nivel):
        super().__init__()
        self.info = info; self.nivel = nivel; self.image = self.info["img"]
        self.rect = self.image.get_rect(); self.rect.centerx = ANCHO//2; self.rect.bottom = ALTO-10
        self.vida_max = int(self.info["stats"]["vida"] * (1+self.nivel*0.2)); self.vida = self.vida_max
        self.velocidad = self.info["stats"]["vel"] * (1+self.nivel*0.05)
        self.daño_actual = int(self.info["stats"]["daño"] * (1+self.nivel*0.15))
        self.cooldown_actual = int(self.info["stats"]["cooldown"] * max(0.2, 1-(self.nivel*0.10)))
        self.monedas_partida = 0; self.ultimo_disparo = 0; self.bombas = 3; self.powerup_doble = False; self.tiempo_powerup = 0

    def update(self):
        if self.powerup_doble and pygame.time.get_ticks()-self.tiempo_powerup > 5000: self.powerup_doble = False
        t = pygame.key.get_pressed()
        if t[pygame.K_LEFT]: self.rect.x -= self.velocidad
        if t[pygame.K_RIGHT]: self.rect.x += self.velocidad
        if t[pygame.K_UP]: self.rect.y -= self.velocidad
        if t[pygame.K_DOWN]: self.rect.y += self.velocidad
        if t[pygame.K_SPACE]: self.intentar_disparar()
        self.rect.clamp_ip(PANTALLA.get_rect())

    def intentar_disparar(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo > self.cooldown_actual:
            self.ultimo_disparo = ahora; self.crear_balas()
            if s := sonidos_disparos.get(self.info["stats"]["tipo"]): s.play()

    def crear_balas(self):
        t = self.info["stats"]["tipo"]; d = self.daño_actual; c = self.info["color"]
        if self.powerup_doble:
            if t == "triple": [balas_jugador.add(Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)) for i in range(-2, 3)]
            else: balas_jugador.add(Bala(self.rect.left, self.rect.top, 0, -14, c, d), Bala(self.rect.right, self.rect.top, 0, -14, c, d))
        else:
            if t in ["normal","rapida","pesada"]: balas_jugador.add(Bala(self.rect.centerx, self.rect.top, 0, -10, AMARILLO, d))
            elif t == "triple": [balas_jugador.add(Bala(self.rect.centerx, self.rect.top, i*2, -9, NARANJA, d)) for i in range(-1, 2)]
            elif t == "laser": balas_jugador.add(Bala(self.rect.centerx, self.rect.top, 0, -25, ROJO, d))
            elif t == "auto": balas_jugador.add(Bala(self.rect.centerx+random.randrange(-5,6), self.rect.top, 0, -14, AMARILLO, d))
        all_sprites.add(*balas_jugador.sprites())
    
    def activar_doble_disparo(self): self.powerup_doble = True; self.tiempo_powerup = pygame.time.get_ticks()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__(); self.tipo = random.choice(['vida', 'doble']); self.image = pygame.Surface((30, 30))
        if self.tipo == 'vida': self.image.fill(ROJO); pygame.draw.rect(self.image, BLANCO, (10, 5, 10, 20)); pygame.draw.rect(self.image, BLANCO, (5, 10, 20, 10))
        else: self.image.fill(AZUL); pygame.draw.circle(self.image, BLANCO, (15, 15), 10, 2)
        self.rect = self.image.get_rect(center=center); self.speedy = 3
    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > ALTO: self.kill()

class EnemigoBasico(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(); self.image = img_asteroide; self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width); self.rect.y = random.randrange(-100, -40)
        self.velocidad_y = random.randrange(2, 5); self.vida = 40 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()

class NaveEnemiga(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(); self.image = img_enemigo; self.rect = self.image.get_rect()
        self.rect.x = random.randrange(ANCHO - self.rect.width); self.rect.y = random.randrange(-150, -50)
        self.velocidad_y = random.randrange(1, 3); self.vida = 80 
    def update(self):
        self.rect.y += self.velocidad_y
        if self.rect.top > ALTO + 10: self.kill()
        if random.randrange(0, 100) < 1: 
            b = BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 5); all_sprites.add(b); balas_enemigas.add(b)

class Boss(pygame.sprite.Sprite):
    def __init__(self, jugador_obj, tipo="malware", char_data=None):
        super().__init__(); self.tipo = tipo; self.jugador = jugador_obj; self.entrando = True
        
        if tipo == "malware":
            self.image = img_jefe1.copy()
            self.vida = 2500; self.vida_max = 2500; self.velocidad_movimiento = 2
        elif tipo == "teammate_blackhat":
            c_id = char_data["id_historia"]
            base_img = SPRITES_SaaS[c_id]["nave_renacida"]
            self.image = pygame.transform.rotate(pygame.transform.scale(base_img, (100, 100)), 180)
            self.vida = char_data["stats"]["vida"] * 4; self.vida_max = self.vida; self.velocidad_movimiento = 3
            dibujar_texto(self.image, f"BH:{c_id[:5]}", 16, 50, 60, MORADO, con_sombra=True)
        elif tipo == "teammate_whitehat":
            c_id = char_data["id_historia"]
            base_img = SPRITES_SaaS[c_id]["nave_certificada"]
            self.image = pygame.transform.rotate(pygame.transform.scale(base_img, (80, 80)), 180)
            self.vida = char_data["stats"]["vida"] * 3; self.vida_max = self.vida; self.velocidad_movimiento = 4
            dibujar_texto(self.image, f"WH:{c_id[:5]}", 16, 40, 50, CYAN, con_sombra=True)

        self.rect = self.image.get_rect(); self.rect.centerx = random.randint(100, ANCHO-100)
        self.rect.y = -150; self.cooldown_disparo = 0; self.destino_x = self.rect.centerx; self.destino_y = random.randint(50, 150)

    def update(self):
        cb = 60
        if self.tipo == "malware":
            if self.vida <= self.vida_max / 2: 
                self.image = img_jefe2.copy(); self.velocidad_movimiento = 4; cb = 40
        elif self.tipo.startswith("teammate"): cb = 35

        if self.entrando:
            self.rect.y += 2
            if self.rect.y >= 50: self.entrando = False
        else:
            dx = self.destino_x - self.rect.centerx; dy = self.destino_y - self.rect.centery; dist = math.sqrt(dx**2 + dy**2)
            if dist > 5: self.rect.centerx += int(dx/dist * self.velocidad_movimiento); self.rect.centery += int(dy/dist * self.velocidad_movimiento)
            else: self.destino_x = random.randint(50, ANCHO - 50); self.destino_y = random.randint(50, ALTO // 2)
            self.cooldown_disparo += 1
            if self.cooldown_disparo >= cb: self.atacar(); self.cooldown_disparo = 0
                
    def atacar(self):
        atq = random.choice(["rafaga", "circular", "dirigido"]) if self.tipo.startswith("teammate") else random.choice(["rafaga", "circular"] if self.vida < self.vida_max/2 else ["simple", "dirigido"])
        if atq == "simple": balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.bottom, 0, 8))
        elif atq == "rafaga": [balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.bottom, i*2, 6)) for i in range(-2, 3)]
        elif atq == "circular":
            for i in range(12): r = math.radians((360/12)*i); balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.centery, 5*math.cos(r), 5*math.sin(r)))
        elif atq == "dirigido":
            dx = self.jugador.rect.centerx - self.rect.centerx; dy = self.jugador.rect.centery - self.rect.centery; d = math.sqrt(dx**2 + dy**2)
            if d > 0: balas_enemigas.add(BalaEnemigo(self.rect.centerx, self.rect.centery, (dx/d)*8, (dy/d)*8))
        all_sprites.add(*balas_enemigas.sprites())

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, sx, sy, c, dmg):
        super().__init__(); self.image = pygame.Surface((6, 16)); self.image.fill(c); self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.sx = sx; self.sy = sy; self.damage = dmg 
    def update(self):
        self.rect.y += self.sy; self.rect.x += self.sx
        if self.rect.bottom < 0: self.kill()

class BalaEnemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, sx, sy):
        super().__init__(); self.image = pygame.Surface((8, 8)); self.image.fill(NARANJA); self.rect = self.image.get_rect(centerx=int(x), top=int(y))
        self.x = float(x); self.y = float(y); self.sx = sx; self.sy = sy
    def update(self):
        self.x += self.sx; self.y += self.sy; self.rect.centerx = int(self.x); self.rect.centery = int(self.y)
        if not PANTALLA.get_rect().colliderect(self.rect): self.kill()

class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y): super().__init__(); self.image = img_moneda; self.rect = self.image.get_rect(center=(x, y))
    def update(self):
        self.rect.y += 3
        if self.rect.top > ALTO: self.kill()

def spawn_enemigos(c):
    for _ in range(c):
        e = EnemigoBasico() if random.random() > 0.5 else NaveEnemiga()
        all_sprites.add(e); enemigos.add(e)

def reiniciar_partida():
    global all_sprites, enemigos, balas_jugador, balas_enemigas, monedas, grupo_boss, powerups, jugador, score, boss_activo
    all_sprites, enemigos, balas_jugador, balas_enemigas, monedas, grupo_boss, powerups = [pygame.sprite.Group() for _ in range(7)]
    jugador = Jugador(NAVES_INFO[nave_seleccionada], mejoras[nave_seleccionada]); all_sprites.add(jugador)
    score = 0; boss_activo = False; spawn_enemigos(8); pygame.mixer.stop()

# =====================================================================
# 5. MENÚS PRINCIPALES Y TIENDA
# =====================================================================
async def menu_principal():
    cambiar_musica("musica_menu.ogg")
    mostrar_modal = False
    pay_form = {"tarjeta": "", "vencimiento": "", "cvv": "", "focus": "tarjeta"}
    font_field = pygame.font.SysFont("arial", 20)

    while True:
        RELOJ.tick(FPS); clic = False 
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: 
                clic = True 
                if mostrar_modal:
                    if pygame.Rect(ANCHO//2-100, 245, 240, 35).collidepoint(e.pos): pay_form["focus"] = "tarjeta"
                    elif pygame.Rect(ANCHO//2-100, 305, 80, 35).collidepoint(e.pos): pay_form["focus"] = "vencimiento"
                    elif pygame.Rect(ANCHO//2+70, 305, 70, 35).collidepoint(e.pos): pay_form["focus"] = "cvv"

            if e.type == pygame.KEYDOWN:
                if mostrar_modal:
                    f = pay_form["focus"]
                    if e.key == pygame.K_BACKSPACE: pay_form[f] = pay_form[f][:-1]
                    elif e.key == pygame.K_TAB:
                        if f == "tarjeta": pay_form["focus"] = "vencimiento"
                        elif f == "vencimiento": pay_form["focus"] = "cvv"
                        elif f == "cvv": pay_form["focus"] = "tarjeta"
                    elif e.unicode.isnumeric() and len(pay_form[f]) < {"tarjeta":16, "vencimiento":5, "cvv":3}[f]:
                        if f == "vencimiento" and len(pay_form[f]) == 2: pay_form["vencimiento"] += "/"
                        pay_form[f] += e.unicode
                elif e.key == pygame.K_l and e.mod & pygame.KMOD_CTRL: 
                    SaaS_GLOBAL.licencia_valida = True; mostrar_modal = False

        PANTALLA.blit(img_fondo_inicio, (0, 0)) if img_fondo_inicio else PANTALLA.fill(NEGRO)
        dibujar_texto_con_fondo(PANTALLA, "DEFENDIENDO LA RED DE ITESCO", 50, ANCHO//2, 100, AZUL)
        
        inf_txt = f"Sistema: {'NORMAL' if not SaaS_GLOBAL.infection_total else 'TOTALMENTE ENCRIPTADO'}"
        dibujar_texto_con_fondo(PANTALLA, inf_txt, 20, 150, 10, VERDE if not SaaS_GLOBAL.infection_total else ROJO, GRIS_OSCURO)
        
        c_hist = VERDE if SaaS_GLOBAL.licencia_valida else GRIS; c_rap = AMARILLO if SaaS_GLOBAL.licencia_valida else GRIS
        txt_bl = "" if SaaS_GLOBAL.licencia_valida else " [BLOQUEADO]"
        clic_btn = clic and not mostrar_modal 

        if dibujar_boton(PANTALLA, "MODO HISTORIA" + txt_bl, ANCHO//2-150, 220, 300, 50, c_hist, BLANCO if SaaS_GLOBAL.licencia_valida else GRIS, clic_btn):
            if SaaS_GLOBAL.licencia_valida: return "intro" 
        if dibujar_boton(PANTALLA, "INICIO RÁPIDO" + txt_bl, ANCHO//2-150, 290, 300, 50, c_rap, BLANCO if SaaS_GLOBAL.licencia_valida else GRIS, clic_btn):
            if SaaS_GLOBAL.licencia_valida: return "seleccion" 
        if dibujar_boton(PANTALLA, "SALIR", ANCHO//2-150, 360, 300, 50, ROJO, BLANCO, clic_btn): pygame.quit(); exit()
            
        if not SaaS_GLOBAL.licencia_valida:
            if dibujar_boton(PANTALLA, "OBTENER LICENCIA", ANCHO//2-150, 480, 300, 50, MORADO, BLANCO, clic_btn): mostrar_modal = True

        if mostrar_modal:
            dim = pygame.Surface((ANCHO, ALTO)); dim.fill(NEGRO); dim.set_alpha(200); PANTALLA.blit(dim, (0,0))
            m_rect = pygame.Rect(150, 100, 500, 400); pygame.draw.rect(PANTALLA, (20, 20, 35), m_rect); pygame.draw.rect(PANTALLA, CYAN, m_rect, 3)
            
            dibujar_texto(PANTALLA, "CENTRO DE PAGOS", 20, ANCHO//2, 140, BLANCO)
            y_f = 245; sp = 60
            
            dibujar_texto(PANTALLA, "Tarjeta:", 18, ANCHO//2-160, y_f+5, BLANCO)
            r_t = pygame.Rect(ANCHO//2-100, y_f, 240, 35); pygame.draw.rect(PANTALLA, AMARILLO if pay_form["focus"]=="tarjeta" else GRIS, r_t, 2)
            PANTALLA.blit(font_field.render(pay_form["tarjeta"], True, VERDE_CLARO), (r_t.x+10, r_t.y+5))
            
            dibujar_texto(PANTALLA, "Exp:", 18, ANCHO//2-140, y_f+sp-10, BLANCO)
            r_v = pygame.Rect(ANCHO//2-100, y_f+sp-15, 80, 35); pygame.draw.rect(PANTALLA, AMARILLO if pay_form["focus"]=="vencimiento" else GRIS, r_v, 2)
            PANTALLA.blit(font_field.render(pay_form["vencimiento"], True, VERDE_CLARO), (r_v.x+10, r_v.y+5))
            
            dibujar_texto(PANTALLA, "CVV:", 18, ANCHO//2+30, y_f+sp-10, BLANCO)
            r_c = pygame.Rect(ANCHO//2+70, y_f+sp-15, 70, 35); pygame.draw.rect(PANTALLA, AMARILLO if pay_form["focus"]=="cvv" else GRIS, r_c, 2)
            PANTALLA.blit(font_field.render(pay_form["cvv"], True, VERDE_CLARO), (r_c.x+10, r_c.y+5))

            if len(pay_form["tarjeta"]) >= 12 and len(pay_form["vencimiento"]) == 5 and len(pay_form["cvv"]) >= 3:
                if dibujar_boton(PANTALLA, "CONFIRMAR PAGO ($9.99)", 250, 400, 300, 40, VERDE, BLANCO, clic):
                    SaaS_GLOBAL.licencia_valida = True; mostrar_modal = False
            else:
                dibujar_boton(PANTALLA, "INGRESE DATOS", 250, 400, 300, 40, GRIS, GRIS, False)

            dibujar_texto(PANTALLA, "Atajo Test: Ctrl + L", 12, ANCHO//2, 470, GRIS)

        pygame.display.flip(); await asyncio.sleep(0) 

async def menu_seleccion():
    global nave_seleccionada, NAVES_INFO
    if not pygame.mixer.music.get_busy(): cambiar_musica("musica_menu.ogg") 
    NAVES_INFO = actualizar_naves_segun_estado()

    while True:
        RELOJ.tick(FPS); clic = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True
        PANTALLA.fill(GRIS_OSCURO)
        dibujar_texto(PANTALLA, "PORTAL DE ANTIVIRUS", 40, ANCHO//2, 10, CYAN, con_sombra=True)
        dibujar_texto(PANTALLA, f"Bitcoin ITESCO: {SaaS_GLOBAL.monedas_totales}", 25, ANCHO-160, 20, AMARILLO, con_sombra=True)

        for i in range(5):
            info = NAVES_INFO[i]; lvl = mejoras[i]; x = 50 + (i%3)*250; y = 80 + (i//3)*240
            pygame.draw.rect(PANTALLA, info["color"] if i==nave_seleccionada else GRIS, (x-5, y-5, 210, 220), 4)
            pygame.draw.rect(PANTALLA, GRIS_OSCURO if info["estado"] != "renacida" else (40,0,40), (x, y, 200, 210))
            PANTALLA.blit(info["img"], info["img"].get_rect(center=(x+100, y+35)))
            
            c_nombre = info["color"]
            dibujar_texto(PANTALLA, f"{info['nombre']}", 16, x+100, y+60, c_nombre)
            s = info["stats"]; lvl_f = (1+lvl*0.15)
            dibujar_texto(PANTALLA, f"Daño: {int(s['daño']*lvl_f)} / Vida: {int(s['vida']*(1+lvl*0.2))}", 14, x+100, y+85, VERDE_CLARO)
            dibujar_texto(PANTALLA, f"CD: {s['cooldown']}ms", 14, x+100, y+100, VERDE_CLARO)
            
            costo = info["costo_mejora"] * (lvl + 1)
            if dibujar_boton(PANTALLA, "Equipar", x+10, y+125, 80, 30, info["color"], BLANCO, clic): nave_seleccionada = i
            if dibujar_boton(PANTALLA, f"Mejorar (${costo})", x+95, y+125, 95, 30, AMARILLO, BLANCO, clic) and SaaS_GLOBAL.monedas_totales >= costo:
                SaaS_GLOBAL.monedas_totales -= costo; mejoras[i] += 1
            
            if info["costo_cura"] > 0:
                cc = info["costo_cura"]
                if dibujar_boton(PANTALLA, f"Cura Antivirus (${cc})", x+10, y+165, 180, 35, ROJO, BLANCO, clic) and SaaS_GLOBAL.monedas_totales >= cc:
                    SaaS_GLOBAL.monedas_totales -= cc; SaaS_GLOBAL.cure_ship_shop(info["id_historia"])
                    if sonido_powerup: sonido_powerup.play()
                    NAVES_INFO = actualizar_naves_segun_estado()

        if dibujar_boton(PANTALLA, "VOLVER AL MENÚ", ANCHO//2-210, 550, 200, 40, ROJO, BLANCO, clic): return "menu"
        if dibujar_boton(PANTALLA, "INICIAR SESIÓN", ANCHO//2+10, 550, 200, 40, AZUL, BLANCO, clic): reiniciar_partida(); return "juego"
        pygame.display.flip(); await asyncio.sleep(0) 

# =====================================================================
# 6. CINEMÁTICAS CON POSICIONES FIJAS EN PANTALLA
# =====================================================================
async def animacion_dialogos_reescrita(guion):
    i = 0; cd_espacio = 0
    while i < len(guion):
        RELOJ.tick(FPS); cd_espacio += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if cd_espacio > 15 and e.type == pygame.KEYDOWN and e.key in [pygame.K_SPACE, pygame.K_RETURN]: i += 1; cd_espacio = 0
        if i >= len(guion): break
        esc = guion[i]; act = esc["activos"]
        PANTALLA.blit(img_itesco_noche, (0, 0)) 
        
        if "aliens" in act: PANTALLA.blit(img_enemigo_intro, (ANCHO//2-75, 50))
        if "certificado" in act: PANTALLA.blit(img_certificado, (ANCHO//2-75, 50))
        
        for act_str in act:
            c_id = act_str.split("_")[0] 
            if c_id in NOMBRES:
                char_data = SPRITES_SaaS[c_id]
                x_pos = POS_X[c_id] # POSICION FIJA
                
                if "_blackhat" in act_str: img = char_data["historia_blackhat"]
                elif "_whitehat" in act_str: img = char_data["historia_whitehat"] # Cuerpo completo cinemática
                elif "_normal" in act_str: img = char_data["historia_normal"]
                elif c_id in SaaS_GLOBAL.infected_characters: img = char_data["historia_blackhat"]
                elif c_id in SaaS_GLOBAL.whitehat_characters: img = char_data["historia_whitehat"]
                else: img = char_data["historia_normal"]
                
                PANTALLA.blit(img, (x_pos, 300))
        
        is_bad = "aliens" in act or "malo" in act or any([c.split("_")[0] in act and c.split("_")[0] in SaaS_GLOBAL.infected_characters for c in act])
        pygame.draw.rect(PANTALLA, NEGRO, (0, ALTO-120, ANCHO, 120))
        pygame.draw.rect(PANTALLA, MORADO if is_bad else CYAN, (0, ALTO-120, ANCHO, 120), 3)
        
        dibujar_texto(PANTALLA, esc["texto"], 22, ANCHO//2, ALTO-100, ROJO if is_bad else BLANCO, max_width=ANCHO-80)
        dibujar_texto(PANTALLA, "[ESPACIO]", 14, ANCHO-60, ALTO-20, AMARILLO)
        pygame.display.flip(); await asyncio.sleep(0)

async def animacion_intro():
    await animacion_dialogos_reescrita([
        {"texto": "Kenzo: ¿Alguien trajo la USB? ¡Ahí viene el código final de Ciberseguridad para Betanzos!", "activos": ["kenzo", "dibanhi", "santiago", "belen"]},
        {"texto": "¡RANSOMWARE-X DETECTADO! PAGUEN 500 BITCOINS A 'ITESC0_H4CK3D' O SUS PROYECTOS SERÁN BORRADOS.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens"]},
        {"texto": "Moises: ¡Banda! El Inge Bulmaro me dio este disco cifrado con 'Naves Antivirus'.", "activos": ["kenzo", "dibanhi", "santiago", "belen", "aliens", "moises"]},
        {"texto": "Todos: ¡A LOS TECLADOS! ¡HOY SALVAMOS LA NUBE DEL ITESCO!", "activos": ["kenzo", "dibanhi", "santiago", "belen", "moises"]}
    ])
    return "seleccion"

async def animacion_pre_jefe(char_id, modo_jefe):
    guion = []; c_disp = char_id.capitalize()
    if modo_jefe == "malware_acumulativa":
        guion = [{"texto": f"{c_disp}: He aislado la firma del Ransomware. Es hora de detener esta encriptación.", "activos": [char_id]}, 
                 {"texto": "Criaturas insignificantes... No tienen privilegios.", "activos": ["aliens"]}]
    elif modo_jefe == "blackhats_remediacion":
        guion.append({"texto": f"{c_disp} [Whitehat]: ¡He localizado la infección! Sus nodos están cifrados...", "activos": [char_id]})
        for c_id in SaaS_GLOBAL.infected_characters: 
            guion.append({"texto": f"{c_id.capitalize()} [Blackhat]: Vaya, vaya... Tarde o temprano te encriptaremos como al resto.", "activos": [f"{c_id}_blackhat"]})
        guion.append({"texto": f"{c_disp} [Whitehat]: ¡No se los permitiré! ¡Ejecutando Firewall!", "activos": [char_id]})
    elif modo_jefe == "victoria_contra_whitehats":
        guion = [{"texto": f"{c_disp} [Blackhat]: La red es débil... Es hora de eliminar a los Whitehats restantes.", "activos": [char_id]}]
    if guion: await animacion_dialogos_reescrita(guion)

# =====================================================================
# 7. CICLO DE JUEGO PRINCIPAL Y RUTAS
# =====================================================================
async def ciclo_juego():
    global score, boss_activo; flash_frames = 0; trigger_boss = False 
    char_id = NAVES_INFO[nave_seleccionada]["id_historia"]
    modo_jefe = "malware_acumulativa"; jefes_a_spawnear = []

    if char_id in SaaS_GLOBAL.infected_characters: 
        modo_jefe = "victoria_contra_whitehats" 
        for c_id in SaaS_GLOBAL.whitehat_characters:
            for k, v in NAVES_INFO.items():
                if v["id_historia"] == c_id: jefes_a_spawnear.append({"tipo": "teammate_whitehat", "data": v}); break
    elif char_id in SaaS_GLOBAL.whitehat_characters:
        modo_jefe = "blackhats_remediacion" 
        for c_id in SaaS_GLOBAL.infected_characters:
            for k, v in NAVES_INFO.items():
                if v["id_historia"] == c_id: jefes_a_spawnear.append({"tipo": "teammate_blackhat", "data": v}); break
    else: 
        jefes_a_spawnear.append({"tipo": "malware"})

    while True:
        RELOJ.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_b and not boss_activo: trigger_boss = True 
                if e.key == pygame.K_t and jugador.bombas > 0:
                    jugador.bombas -= 1; flash_frames = 3
                    if sonido_bomba: sonido_bomba.play()
                    for en in list(enemigos): en.vida -= 1000; (en.kill(), score.__add__(10)) if en.vida <= 0 else None
                    for b in grupo_boss: b.vida -= 500
                if e.key == pygame.K_f: 
                    pygame.mixer.music.stop()
                    if modo_jefe == "victoria_contra_whitehats": return "victoria_contra_whitehats"
                    elif modo_jefe == "blackhats_remediacion": return "victoria_blackhats_remediacion"
                    else: return "victoria_malware_acumulativa"

        PANTALLA.blit(img_fondo_jefe if boss_activo else img_fondo_juego, (0, 0)) if (img_fondo_jefe or img_fondo_juego) else PANTALLA.fill(NEGRO)
        all_sprites.update()
        if not boss_activo and len(enemigos) < 8: spawn_enemigos(8 - len(enemigos))
        
        if (trigger_boss or score >= 100) and not boss_activo:
            boss_activo = True; trigger_boss = False; [en.kill() for en in list(enemigos)]
            await animacion_pre_jefe(char_id, modo_jefe); cambiar_musica("musica_jefe.ogg")
            for j_data in jefes_a_spawnear:
                b = Boss(jugador, j_data["tipo"], j_data.get("data")); all_sprites.add(b); grupo_boss.add(b)

        for enemigo, l_balas in pygame.sprite.groupcollide(enemigos, balas_jugador, False, True).items():
            for bala in l_balas:
                enemigo.vida -= bala.damage
                if enemigo.vida <= 0:
                    enemigo.kill(); score += 10; sonido_explosion.play() if sonido_explosion else None
                    if random.random() > 0.9: PowerUp(enemigo.rect.center).add(all_sprites, powerups)
                    elif random.random() > 0.6: Moneda(enemigo.rect.centerx, enemigo.rect.centery).add(all_sprites, monedas)

        for p in pygame.sprite.spritecollide(jugador, powerups, True):
            sonido_powerup.play() if sonido_powerup else None
            (jugador.vida.__setattr__("vida", min(jugador.vida_max, jugador.vida + 30)), None) if p.tipo == 'vida' else jugador.activar_doble_disparo()

        if boss_activo:
            for boss_obj, l_balas in pygame.sprite.groupcollide(grupo_boss, balas_jugador, False, True).items():
                for bala in l_balas: boss_obj.vida -= bala.damage
                if boss_obj.vida <= 0: boss_obj.kill()
            if len(grupo_boss) == 0:
                score += 5000; SaaS_GLOBAL.monedas_totales += jugador.monedas_partida + 200
                pygame.mixer.music.stop()
                if modo_jefe == "victoria_contra_whitehats": return "victoria_contra_whitehats"
                elif modo_jefe == "blackhats_remediacion": return "victoria_blackhats_remediacion"
                else: return "victoria_malware_acumulativa"

        if pygame.sprite.spritecollide(jugador, enemigos, True): jugador.vida -= 20
        if pygame.sprite.spritecollide(jugador, balas_enemigas, True): jugador.vida -= 10
        if pygame.sprite.spritecollide(jugador, grupo_boss, False): jugador.vida -= 5

        if jugador.vida <= 0: 
            pygame.mixer.music.stop()
            if modo_jefe == "blackhats_remediacion": return "derrota_whitehat"
            elif modo_jefe == "victoria_contra_whitehats": return "derrota_blackhat"
            return "game_over"

        for m in pygame.sprite.spritecollide(jugador, monedas, True): jugador.monedas_partida += 1; sonido_moneda.play() if sonido_moneda else None

        all_sprites.draw(PANTALLA)
        v = VERDE_CLARO if len(SaaS_GLOBAL.infected_characters) < 5 else MORADO
        dibujar_texto(PANTALLA, f"ID: {jugador.info['nombre']}", 20, 100, 10, jugador.info["color"])
        dibujar_texto(PANTALLA, f"Datos: {score} MB", 20, ANCHO//2, 10, v)
        dibujar_texto(PANTALLA, f"Bitcoin ITESCO: {jugador.monedas_partida}", 20, ANCHO-100, 10, AMARILLO)
        dibujar_texto(PANTALLA, f"Cargas DDOS [T]: {jugador.bombas}", 16, 100, 40, v)
        if jugador.powerup_doble: dibujar_texto(PANTALLA, "¡OVERCLOCK ACTIVADO!", 16, ANCHO//2, 40, CYAN)

        l_v = 200; act = (max(0, jugador.vida) / jugador.vida_max) * l_v
        pygame.draw.rect(PANTALLA, ROJO, (10, 70, l_v, 15)); pygame.draw.rect(PANTALLA, VERDE if len(SaaS_GLOBAL.infected_characters) < 5 else MORADO, (10, 70, act, 15)); pygame.draw.rect(PANTALLA, BLANCO, (10, 70, l_v, 15), 2)

        if boss_activo:
            n_j = "¡RANSOMWARE-X DETECTADO!" if modo_jefe.startswith("malware") else "¡PROTOCOLOS ENEMIGOS!"
            dibujar_texto(PANTALLA, n_j, 24, ANCHO//2, 70, con_sombra=True, color=ROJO)
            if len(grupo_boss) > 0: b_repr = grupo_boss.sprites()[0]; pygame.draw.rect(PANTALLA, MORADO, (ANCHO//2-100, 100, (max(0, b_repr.vida)/b_repr.vida_max)*200, 20))

        if flash_frames > 0: PANTALLA.fill(BLANCO); flash_frames -= 1
        pygame.display.flip(); await asyncio.sleep(0) 

async def pantalla_fin(tipo):
    global score
    es_vic = tipo.startswith("victoria")
    
    if tipo == "victoria_contra_whitehats" or tipo == "derrota_whitehat":
        c_titulo = ROJO; txt_titulo = "SISTEMA COMPROMETIDO"
        img_bg = img_fondo_win_kenzo; cambiar_musica("kenzo_win.ogg")
    elif tipo == "victoria_blackhats_remediacion" or tipo == "derrota_blackhat":
        c_titulo = VERDE; txt_titulo = "AMENAZA NEUTRALIZADA"
        img_bg = img_fondo_win_equipo; cambiar_musica("win_equipo.ogg")
    elif tipo == "victoria_malware_acumulativa":
        c_titulo = VERDE; txt_titulo = "MALWARE DESTRUIDO"
        img_bg = img_fondo_win; sonido_victoria.play() if sonido_victoria else None
    else:
        c_titulo = ROJO; txt_titulo = "NAVE DESTRUIDA"
        img_bg = img_fondo_gameover; sonido_gameover.play() if sonido_gameover else None

    while True:
        RELOJ.tick(FPS); clic = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True

        PANTALLA.blit(img_bg, (0, 0)) if img_bg else PANTALLA.fill(NEGRO)
        off_y = 150 if img_bg else 0 

        dibujar_texto_con_fondo(PANTALLA, txt_titulo, 50, ANCHO//2, 100+off_y, c_titulo)
        dibujar_texto_con_fondo(PANTALLA, f"Datos Salvados: {score} MB", 30, ANCHO//2, 200+off_y)
        dibujar_texto_con_fondo(PANTALLA, f"Bitcoins Obtenidos: {jugador.monedas_partida}", 30, ANCHO//2, 250+off_y, AMARILLO)
        
        if dibujar_boton(PANTALLA, "CONTINUAR...", ANCHO//2-100, 350+off_y, 200, 50, AZUL, BLANCO, clic):
             if tipo == "game_over": pygame.mixer.stop(); return "seleccion"
             else: return tipo.replace("victoria_", "epilogo_").replace("derrota_", "epilogo_derrota_")
        pygame.display.flip(); await asyncio.sleep(0) 

# =====================================================================
# 8. EPÍLOGOS Rogue-Like Y PANTALLAS DE FINAL ABSOLUTO
# =====================================================================
async def pantalla_final_absoluta(bando):
    """Pantalla final definitiva sin botones, se sale con un clic."""
    pygame.mixer.stop()
    pygame.mixer.music.stop()
    
    if bando == "whitehat": img_to_blit = img_final_total_whitehat
    else: img_to_blit = img_final_total_blackhat

    # He añadido un sonido especial al entrar si existen
    if bando == "whitehat" and sonido_victoria: sonido_victoria.play()
    elif bando == "blackhat" and sonido_gameover: sonido_gameover.play()

    while True:
        RELOJ.tick(FPS)
        clic = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            # Cualquier clic de ratón sale al menú
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: clic = True

        if clic:
            # AL SALIR, REINICIAMOS FACCIÓN PARA SIGUIENTE RUN
            SaaS_GLOBAL.cure_all() 
            reiniciar_partida()
            return "menu"

        PANTALLA.blit(img_to_blit, (0, 0)) if img_to_blit else PANTALLA.fill(NEGRO)
        dibujar_texto_con_fondo(PANTALLA, "[Clic para volver al Menú Principal]", 20, ANCHO//2, ALTO-50, color=AMARILLO if bando == "whitehat" else MORADO, bg_color=GRIS_OSCURO)

        pygame.display.flip(); await asyncio.sleep(0)

async def animacion_epilogo_SaaS(modo_epilogo):
    char_id = NAVES_INFO[nave_seleccionada]["id_historia"]
    c_disp = char_id.capitalize()
    
    if modo_epilogo == "epilogo_malware_acumulativa":
        cambiar_musica("kenzo_win.ogg"); PANTALLA.blit(img_fondo_win_kenzo, (0, 0)) if img_fondo_win_kenzo else PANTALLA.fill(GRIS_OSCURO)
        dibujar_texto_con_fondo(PANTALLA, "EPÍLOGO (LA CAÍDA DEL HÉROE)", 24, ANCHO//2, 80, AMARILLO)
        
        # 1. Transformación del Héroe
        guion_hero = [
            {"texto": f"{c_disp}: ¡Ransomware-X borrado! Lo logramos...", "activos": [f"{char_id}_normal"]},
            {"texto": "ALERTA: Carga maliciosa inyectada en el sistema local.", "activos": ["aliens"]},
            # TRANSFORMACIÓN A BLACKHAT EN VIVO CON GÉNERO
            {"texto": f"{c_disp} [Blackhat]: ¿Qué me pasa? Mi código... ¡La red del ITESCO AHORA ES MÍA!", "activos": [f"{char_id}_blackhat"]},
        ]
        await animacion_dialogos_reescrita(guion_hero)
        SaaS_GLOBAL.make_blackhat(char_id) # Se actualiza el estado ANTES de la certificación
        
        # 2. ESCENA DE CERTIFICACIÓN ÉPICA (NUEVA)
        cambiar_musica("win_equipo.ogg") # Musica de esperanza
        all_others = set(NOMBRES) - {char_id}
        
        guion_cert = [{"texto": "SISTEMA: ITESCO Ciber-Defensa emitiendo Certificados Whitehat de emergencia a los usuarios restantes.", "activos": ["certificado"]}]
        
        for wh_id in all_others:
            gender = oa(wh_id)
            guion_cert.append({"texto": f"....: {wh_id.capitalize()}, ¡toma tu certificación! Te necesitamos luchando.", "activos": [f"{wh_id}_normal", "certificado"]})
            guion_cert.append({"texto": f"{wh_id.capitalize()}: Agh... ¡El parche de seguridad está entrando!", "activos": [f"{wh_id}_normal"]})
            # El sprite cambia dinámicamente en vivo en la cinemática
            guion_cert.append({"texto": f"{wh_id.capitalize()} [Whitehat]: ¡Sistemas actualizados! Estoy list{gender} para luchar contra l{OA(char_id)}s Blackhats.", "activos": [f"{wh_id}_whitehat"]})
            
        guion_cert.append({"texto": f"....: ¡No permitan que l{OA(char_id)}s Blackhats encripten la red maestra!", "activos": ["certificado"] + [f"{n}_whitehat" for n in all_others]})
        await animacion_dialogos_reescrita(guion_cert)
        # La run termina aquí y vuelve a selección
        return "seleccion"
        
    elif modo_epilogo == "epilogo_blackhats_remediacion":
        cambiar_musica("win_equipo.ogg"); PANTALLA.blit(img_fondo_win_equipo, (0, 0)) if img_fondo_win_equipo else PANTALLA.fill(GRIS_OSCURO)
        dibujar_texto_con_fondo(PANTALLA, "EPÍLOGO (DEPURACIÓN DE BLACKHATS)", 24, ANCHO//2, 80, VERDE)
        guion = [
            {"texto": f"{c_disp} [Whitehat]: ¡Ping Exitoso! He aislado los rootkits enemigos.", "activos": [f"{char_id}_whitehat"]},
            {"texto": "SISTEMA: Depuración exitosa. Restaurando usuarios a su versión de fábrica...", "activos": ["aliens"]}
        ]
        for b_id in SaaS_GLOBAL.infected_characters:
            guion.append({"texto": f"{b_id.capitalize()}: Agh... Mi cabeza. ¿Qué pasó? Gracias por salvarme.", "activos": [f"{b_id}_normal"]})
        guion.append({"texto": "SISTEMA: Amenaza neutralizada. Revocando Certificados Whitehat temporales.", "activos": ["aliens"]})
        # Al ganar Whitehat total, curamos a todos
        SaaS_GLOBAL.cure_all() 
        await animacion_dialogos_reescrita(guion)
        # AHORA LLEVA AL FINAL ABSOLUTO
        return "pantalla_final_whitehat"
        
    elif modo_epilogo == "epilogo_contra_whitehats":
        cambiar_musica("final.ogg"); PANTALLA.blit(img_itesco_noche, (0, 0)); dibujar_texto_con_fondo(PANTALLA, "EPÍLOGO CONDICIONAL (CORRUPCIÓN TOTAL)", 24, ANCHO//2, 80, ROJO)
        guion = [
            {"texto": f"{c_disp} [Blackhat]: Sus certificados no sirven de nada contra mí. ¡ESTA RED ES MÍA!", "activos": [f"{char_id}_blackhat"]},
            {"texto": "SISTEMA: Firewall maestro caído. Propagando encriptación a todos los nodos...", "activos": ["aliens"]},
        ]
        current_whs = list(SaaS_GLOBAL.whitehat_characters)
        for w_id in current_whs: SaaS_GLOBAL.make_blackhat(w_id)
        SaaS_GLOBAL.make_blackhat(char_id) 
        guion.append({"texto": "Todos [Blackhats]: Somos uno con el código... Salve el Ransomware.", "activos": [f"{n}_blackhat" for n in NOMBRES]})
        await animacion_dialogos_reescrita(guion)
        # AHORA LLEVA AL FINAL ABSOLUTO
        return "pantalla_final_blackhat"
        
    elif modo_epilogo == "epilogo_derrota_whitehat":
        cambiar_musica("kenzo_win.ogg"); PANTALLA.blit(img_itesco_noche, (0, 0)); dibujar_texto_con_fondo(PANTALLA, "EPÍLOGO CONDICIONAL (WHITEHAT CAÍDO)", 24, ANCHO//2, 80, ROJO)
        guion = [
            {"texto": f"{c_disp} [Whitehat]: ¡No! ¡Mis escudos fallaron! El código malicioso está entrando...", "activos": [f"{char_id}_whitehat"]},
            {"texto": "SISTEMA: Usuario comprometido. Certificado Whitehat revocado.", "activos": ["aliens"]},
            # Pronombre dinámico para mujeres
            {"texto": f"{c_disp} [Blackhat]: El dolor se ha ido... Me uniré a mis compañer{oa(char_id)}s caíd{oa(char_id)}s.", "activos": [f"{char_id}_blackhat"]}
        ]
        SaaS_GLOBAL.make_blackhat(char_id) 
        await animacion_dialogos_reescrita(guion)
        return "seleccion"
        
    elif modo_epilogo == "epilogo_derrota_blackhat":
        cambiar_musica("win_equipo.ogg"); PANTALLA.blit(img_fondo_win_equipo, (0, 0)) if img_fondo_win_equipo else PANTALLA.fill(GRIS_OSCURO)
        dibujar_texto_con_fondo(PANTALLA, "EPÍLOGO CONDICIONAL (BLACKHAT REDIMIDO)", 24, ANCHO//2, 80, VERDE)
        guion = [
            {"texto": f"{c_disp} [Blackhat]: ¡Ahhh! ¡Están borrando mis privilegios de Root!", "activos": [f"{char_id}_blackhat"]},
            {"texto": "SISTEMA: Malware purgado del sistema. Restaurando conectividad...", "activos": ["aliens"]},
            {"texto": f"{c_disp} [Redimid{oa(char_id)}]: Esperen... el virus se ha ido. ¡Estoy libre! Los ayudaré de nuevo.", "activos": [f"{char_id}_normal"]}
        ]
        SaaS_GLOBAL.make_whitehat(char_id) 
        await animacion_dialogos_reescrita(guion)
        return "seleccion"

    return "seleccion"

async def main():
    estado_SaaS = "menu" 
    while True:
        if estado_SaaS == "menu": estado_SaaS = await menu_principal()
        elif estado_SaaS == "seleccion": estado_SaaS = await menu_seleccion()
        elif estado_SaaS == "intro": estado_SaaS = await animacion_intro()
        elif estado_SaaS == "juego": estado_SaaS = await ciclo_juego()
        elif estado_SaaS == "game_over": estado_SaaS = await pantalla_fin("derrota")
        elif estado_SaaS.startswith("victoria_") or estado_SaaS.startswith("derrota_"): estado_SaaS = await pantalla_fin(estado_SaaS)
        elif estado_SaaS.startswith("epilogo_"): estado_SaaS = await animacion_epilogo_SaaS(estado_SaaS)
        # ESTADOS DE FINAL ABSOLUTO
        elif estado_SaaS == "pantalla_final_whitehat": estado_SaaS = await pantalla_final_absoluta("whitehat")
        elif estado_SaaS == "pantalla_final_blackhat": estado_SaaS = await pantalla_final_absoluta("blackhat")
        else: estado_SaaS = "menu"
        await asyncio.sleep(0)

asyncio.run(main())