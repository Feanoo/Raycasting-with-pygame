import pygame
from math import pi, cos, sin, sqrt, atan2
from random import randint

pygame.init()

class Obstacle:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        self.c = (255, 255, 255)

    def draw(self, surf):
        pygame.draw.line(surf, self.c, self.begin, self.end)

    def __eq__(self, obj):
        if type(obj) == Obstacle:
            return self.begin == obj.begin and self.end == obj.end
        raise TypeError()

    def __repr__(self):
        return f'{str(self.begin)} -> {str(self.end)}'

class Being(pygame.sprite.Sprite):
    def __init__(self, x, y, w = 10):
        super().__init__()
        self.x = x
        self.y = y
        self.visible = False
        self.dist = 1
        self.angle = 0
        self.width = w

    def check_visible(self, perso, murs):

        c = (self.x-perso.x)
        s = -(self.y-perso.y)
        self.angle = (atan2(s, c))
        #rajouter un deuxieme angle pour lequel on prend le cote droit de l'image, ca permet que le sprite disparait quand le cote droit disparait aussi au lieu de que le cote gauche
        a = self.angle-(pi/2)
        w = self.image.get_width()
        c = self.x + cos(a)*w - perso.x
        s = -(self.y - sin(a)*w - perso.y)
        a = (atan2(s, c))
        # print(w, s, c, a) #en gros w c'est 200 pixel mais 200 pixel sur la vue 3D c'est pas pareil que sur la vue 2D ducoup faut convertir


#reverifier ca plus tard
        # if a < perso.angle_of_view - pi/6 and self.angle > perso.angle_of_view + pi/6:
        #     self.visible = False
        #     return

        x, y = cast((perso.x, perso.y, 2*pi-self.angle), murs)[0]

        self.visible = sqrt((perso.x-x)**2 + (perso.y-y)**2) > self.dist
        # print(f"dist : {self.dist}, wall_intersect : {x} {y}, wall : {sqrt((perso.x-x)**2 + (perso.y-y)**2)}, angles : {self.angle} {a}, visible : {self.visible}")
        return x, y


    def update(self, perso, murs):
        self.dist = sqrt((self.x-perso.x)**2 + (self.y-perso.y)**2)
        x, y = self.check_visible(perso, murs)
        if self.visible:
            w, h = self.img.get_size()
            h1 = 600 - 2*(300-(6000/self.dist))
            w = max(1, (w*h1/h))
            self.image = pygame.transform.scale(self.img, (int(w),int(h1)))
        return x, y

class Exit(Being):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("exit.png")
        self.img = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.x, self.y

class A:
    def __init__(self, x,y):
        self.x = x
        self.y = y
        self.angle_of_view = 0
        self.generate_field()

    def generate_field(self):
        self.field_of_view = []
        for i in range(-100,101):
            self.field_of_view.append(self.angle_of_view-i*pi/600)

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.walls = [True, True, True, True]
        self.visited = False

    def check_neighbours(self, grid):
        neighbours = []
        if self.y > 0:
            # print(self.x)
            top = grid[self.y-1][self.x]
        else:
            top = 0
        try:
            right = grid[self.y][self.x+1]
        except:
            right = 0
        try:
            bottom = grid[self.y+1][self.x]
        except:
            bottom = 0
        if self.x > 0:
            left = grid[self.y][self.x-1]
        else:
            left = 0

        if top and not top.visited:
            neighbours.append(top)
        if right and not right.visited:
            neighbours.append(right)
        if bottom and not bottom.visited:
            neighbours.append(bottom)
        if left and not left.visited:
            neighbours.append(left)

        if neighbours != []:
            r = neighbours[randint(0,len(neighbours)-1)]
            return r
        else:
            return

def cast(line, walls):
    points = []
    ind = []
    for i in range(len(walls)):
        # print(w)
        a = intersect(line, walls[i])
        if a:
            points.append(a)
            ind.append(i)

    if points == []:
        return None

    m = sqrt((line[0]-points[0][0])**2 + (line[1]-points[0][1])**2)
    im = 0
    for i in range(1, len(points)):
        d = sqrt((line[0]-points[i][0])**2 + (line[1]-points[i][1])**2)
        if d < m:
            m = d
            im = i

    return points[im], ind[im]

def intersect(line, wall):
    x1, y1 = wall.begin
    x2, y2 = wall.end
    x3, y3 = line[0], line[1]
    x4, y4 = line[0]+cos(line[2]), line[1]+sin(line[2])

    den = (x1-x2) * (y3-y4) - (y1 - y2) * (x3-x4)
    if den == 0:
        return None

    t = ((x1-x3) * (y3-y4) - (y1-y3) * (x3-x4)) / den
    u = -((x1-x2) * (y1-y3) - (y1-y2) * (x1-x3)) / den
    if t > 0 and t < 1 and u > 0:
        vx = x1 + t * (x2 - x1)
        vy = y1 + t * (y2 - y1)
        return vx, vy
    return None

def generate_maze(w, h):
    c = [[Cell(j,i) for j in range(w)] for i in range(h)]
    current = c[0][0]
    left = w*h - 1
    stack = []
    while left > 0:
        current.visited = True
        next = current.check_neighbours(c)
        if next is not None:
            stack.append(current)
            next.visited = True
            if next.x > current.x:
                current.walls[3] = False
                next.walls[1] = False
            elif next.x < current.x:
                current.walls[1] = False
                next.walls[3] = False
            elif next.y > current.y:
                current.walls[2] = False
                next.walls[0] = False
            elif next.y < current.y:
                current.walls[0] = False
                next.walls[2] = False
            current = next
            left -= 1

        elif len(stack) > 0:
            current = stack[-1]
            stack.pop(-1)
        else:
            return c


    return c

def from_800_600_to_200_200(x,y):
    return x/800 * 200, y/600 * 200

def main():
    SCREEN = pygame.display.set_mode((1600,600))
    surf_2d = pygame.surface.Surface((800,600))
    surf_3d = pygame.surface.Surface((800,600))
    carte_surf = pygame.surface.Surface((200,200)).convert_alpha()
    carte_surf.fill((0,0,0,0))
    background_img = pygame.image.load("background.png")

    minimap = pygame.surface.Surface((200,200))

    perso = A(50,25)
    murs = []#Obstacle((0,0), (0,600)), Obstacle((0,0),(800,0)), Obstacle((0,600), (800,600)), Obstacle((800,0), (800,600)),
            # Obstacle((0,50),(400,50)),
            # Obstacle((420,50), (640,50)),
            # Obstacle((670,50), (780,50)),
            # Obstacle((780,50), (780,100)),
            # Obstacle((780,100), (800,100)),
            # Obstacle((420,50), (420,500)),
            # Obstacle((400,50), (400,500)),
            # Obstacle((640,50), (640,500)),
            # Obstacle((670,50), (670,500))]

    tile_size = 80
    l = generate_maze(800//tile_size, 600//tile_size)
    for i in range(len(l)):
        for j in range(len(l[i])):
            cell = l[i][j]
            if cell.walls[0]:
                murs.append(Obstacle((cell.x*tile_size, cell.y*tile_size), (cell.x*tile_size+tile_size, cell.y*tile_size)))
            if cell.walls[1]:
                murs.append(Obstacle((cell.x*tile_size, cell.y*tile_size), (cell.x*tile_size, cell.y*tile_size+tile_size)))
            if i == len(l)-1 and cell.walls[2]:
                murs.append(Obstacle((cell.x*tile_size, cell.y*tile_size+tile_size), (cell.x*tile_size+tile_size, cell.y*tile_size+tile_size)))
            if j == len(l[i])-1 and cell.walls[3]:
                murs.append(Obstacle((cell.x*tile_size+tile_size, cell.y*tile_size), (cell.x*tile_size+tile_size, cell.y*tile_size+tile_size)))
            # if cell.y == len(l)-1 and cell.walls[2]:
            #     murs.append(Obstacle((cell.x*tile_size, cell.y*tile_size+tile_size), (cell.x*tile_size+tile_size, cell.y*tile_size+tile_size)))
            # if cell.x == len(l[0])-1 and cell.walls[3]:
            #     murs.append(Obstacle((cell.x*tile_size+tile_size, cell.y*tile_size), (cell.x*tile_size+tile_size, cell.y*tile_size+tile_size)))

    # for i in range(10):
    #     murs.append(Obstacle((randint(0, 800), randint(0, 600)), (randint(0, 800), randint(0, 600))))


    print(len(murs))
    for i in range(len(murs)-1, -1, -1):
        for j in range(i-1, -1, -1):
            if murs[i] == murs[j]:
                murs.pop(i)
                break

            x, y = murs[i].begin
            x1, y1 = murs[i].end
            a, b = murs[j].begin
            a1, b1 = murs[j].end

            change = False
            if x == x1 == a == a1:
                if y == b:
                    murs[j].begin = murs[i].end
                    murs.pop(i)
                    change = True
                elif y == b1:
                    murs[j].end = murs[i].end
                    murs.pop(i)
                    change = True
                elif y1 == b:
                    murs[j].begin = murs[i].begin
                    murs.pop(i)
                    change = True
                elif y1 == b1:
                    murs[j].end = murs[i].begin
                    murs.pop(i)
                    change = True

            if y == y1 and b == b1 and y == b:
                if x == a:
                    murs[j].begin = murs[i].end
                    murs.pop(i)
                    change = True
                elif x == a1:
                    murs[j].end = murs[i].end
                    murs.pop(i)
                    change = True
                elif x1 == a:
                    murs[j].begin = murs[i].begin
                    murs.pop(i)
                    change = True
                elif x1 == a1:
                    murs[j].end = murs[i].begin
                    murs.pop(i)
                    change = True

            if change:
                # print(murs[j])
                break

    print(len(murs))

    collide = [False for i in range(len(perso.field_of_view))]
    dist_list = [0 for i in range(len(perso.field_of_view))]
    pos_liste = [(0,0)]
    perso_speed = 1

    beings_sprites = pygame.sprite.Group()
    # Exit(800 - tile_size//2, 600 - tile_size//2).add(beings_sprites)
    Exit(25, 50).add(beings_sprites)

    keys = pygame.key.get_pressed()
    pygame.mouse.set_visible(False)
    C = pygame.time.Clock()
    while True:
        # print(pygame.time.get_ticks(), end=' > ')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_z:
                    perso.angle_of_view += pi/20
                    perso.angle_of_view %= pi*2
                    perso.generate_field()
                elif event.key == pygame.K_s:
                    perso.angle_of_view -= pi/20
                    perso.angle_of_view %= pi*2
                    perso.generate_field()
            elif event.type == pygame.KEYUP:
                keys = pygame.key.get_pressed()
            elif event.type == pygame.MOUSEMOTION:
                perso.angle_of_view += (event.rel[0]/200)
                perso.angle_of_view %= 2*pi
                perso.generate_field()
                pygame.event.set_blocked(pygame.MOUSEMOTION)
                pygame.mouse.set_pos((400,300))
                pygame.event.set_allowed(pygame.MOUSEMOTION)
                # print(event.rel)
            #     x,y = pygame.mouse.get_pos()
            #     d = sqrt((x-perso.x)**2 + (y-perso.y)**2)
            #     c = (x-perso.x)/d
            #     s = -((y-perso.y)/d)
            #     a = -atan2(s, c)
            #     perso.angle_of_view = a
            #     perso.generate_field()


        if keys[pygame.K_UP]:
            perso.x += cos(perso.angle_of_view)*perso_speed
            perso.y += sin(perso.angle_of_view)*perso_speed
            l = len(collide)//2
            for i in range(l):
                if collide[l-i]:
                    perso.x -= cos(perso.field_of_view[l-i])*perso_speed
                    perso.y -= sin(perso.field_of_view[l-i])*perso_speed
                    break
                elif collide[l+i]:
                    perso.x -= cos(perso.field_of_view[l+i])*perso_speed
                    perso.y -= sin(perso.field_of_view[l+i])*perso_speed
                    break

            x = perso.x // tile_size
            y = perso.y // tile_size
            if (x,y) not in pos_liste:
                x, y = (x*tile_size + (tile_size//2), y*tile_size + (tile_size//2))
                x, y = from_800_600_to_200_200(x, y)
                pos_liste.append((x,y))
                pygame.draw.line(carte_surf, (255,0,0), pos_liste[-1], pos_liste[-2], 1)

        # if keys[pygame.K_DOWN]:
        #     perso.x -= cos(perso.angle_of_view)
        #     perso.y -= sin(perso.angle_of_view)
        #     a = 2
        #     l = len(collide)//2
        #     for i in range(l):
        #         if collide[l-i]:
        #             perso.x += cos(perso.field_of_view[l-i])
        #             perso.y += sin(perso.field_of_view[l-i])
        #             break
        #         elif collide[l+i]:
        #             perso.x += cos(perso.field_of_view[l+i])
        #             perso.y += sin(perso.field_of_view[l+i])
        #             break


            # if surf_2d.get_at((int(perso.x), int(perso.y))) == (255,255,255,255):
                # perso.x += cos(perso.angle_of_view)
                # perso.y += sin(perso.angle_of_view)

        # if keys[pygame.K_LEFT]:
        #     perso.x += cos(perso.angle_of_view - (pi/4))
        #     perso.y += sin(perso.angle_of_view - (pi/4))
        #     perso.generate_field()
        # elif keys[pygame.K_RIGHT]:
        #     perso.x += cos(perso.angle_of_view + (pi/4))
        #     perso.y += sin(perso.angle_of_view + (pi/4))
        #     perso.generate_field()

        # SCREEN.fill((0,0,0))

##	      2D
        # pygame.draw.circle(SCREEN, (255,255,255), (int(perso.x), int(perso.y)), 2)
        surf_2d.fill((0,0,0))
        for l in perso.field_of_view:
            a = cast((perso.x, perso.y, l), murs)
            if a:
                pygame.draw.line(surf_2d, (255,255,255), (perso.x, perso.y), a[0])
        for m in murs:
            m.draw(surf_2d)

##      3D
        surf_3d.blit(background_img, (0, 0))
        for i in range(len(perso.field_of_view)):
            a = cast((perso.x, perso.y, perso.field_of_view[i]), murs)
            if a:
                x,y = a[0]
                d = cos(perso.angle_of_view - perso.field_of_view[i]) * sqrt((perso.x-x)**2 + (perso.y-y)**2)
                dist_list[i] = d
                if d < 10:
                    collide[i] = True
                    # print(i)
                else:
                    collide[i] = False
                # color = int((255/d) * 15) # ça c'est plutot bien
                # color = min(max(color, 0), 200)
                lum = int(255/d*10)
                lum = min(max(lum, 20), 200)
                dx = murs[a[1]].end[0] - murs[a[1]].begin[0]
                dy = murs[a[1]].end[1] - murs[a[1]].begin[1]

                angle = atan2(dy, dx)
                # r = lum/5
                # g = max(0, lum + int((abs(sin(angle))-0.5) * amp))
                # b = max(0, lum + int((0.5 - abs(sin(angle))) * amp))
                c = lum + (-abs(sin(angle)))*10
                # print(angle, r, g, b)
                #pygame.draw.line(surf_3d, (color, color, color), (i, 0), (i, 600))
                h = 300 - (4000/d)# * min(300,d)
                h = max(h, 0)
                if not i:
                    pygame.draw.rect(surf_3d, (int(c*0.8), int(c*0.8), int(c*0.9)), ((200-i)*4, h, 4, 600-(2*h)))
                else:
                    pygame.draw.rect(surf_3d, (int(c*0.8), int(c*0.8), int(c*0.9)), ((200-i)*4, h, 4, 600-(2*h)))
                    # h2 = max(0, 300 - (4000/dist_list[i-1]))
                    # pygame.draw.polygon(surf_3d, (int(c*0.8), int(c*0.8), int(c*0.9)), [((200-i)*4, h), ((201-i)*4, h2), ((201-i)*4, 600-2*h2), ((20-i)*4, 600-2*h)])


        for sprite in beings_sprites:
            X, Y = sprite.update(perso, murs)
            pygame.draw.circle(surf_2d, (255, 0, 0), (sprite.x, sprite.y), 2)
            if sprite.visible:
                # x = int(400 - (400*(perso.angle_of_view - sprite.angle)) / (perso.angle_of_view - perso.field_of_view[-1]))
                # a = (sprite.angle - perso.field_of_view) #si abs(a) < pi/6, sprite est dans le champ de vision => TODO : check visible avec ca
                # a = 400*(sprite.angle - perso.angle_of_view)/(pi/6)
                # x = 400 + a

                a = 400 * ((sprite.angle%(2*pi)) - (2*pi-perso.angle_of_view))/(pi/6)
                x = 400 - a

                # print(2*pi-perso.angle_of_view, sprite.angle, a, x)
                y = int(max(0, 300-(6000/sprite.dist)))
                surf_3d.blit(sprite.image, (x, y))
                # print(x,y, sprite.image.get_size())
            pygame.draw.line(surf_2d, (255, 0, 0), (perso.x, perso.y), (X, Y))


##      carte
        x, y = (perso.x//tile_size * tile_size + (tile_size//2), perso.y//tile_size * tile_size + (tile_size//2))
        x, y = from_800_600_to_200_200(x, y)
        minimap.fill((0,0,0))
        pygame.draw.rect(minimap, (170,185,75), (0,0,200,200), 2)

        pygame.draw.circle(minimap, (150,150,175), (int(x), int(y)), 2)
        minimap.blit(carte_surf, (0,0))

        # pygame.draw.line(surf_2d, (255,0,0), (0,280), (800,280))
        SCREEN.blit(surf_2d, (800,0))
        SCREEN.blit(surf_3d, (0,0))
        SCREEN.blit(minimap, (600,400))
        pygame.display.update()
        C.tick(60)

if __name__ == "__main__":
    main()
