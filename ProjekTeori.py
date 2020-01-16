import random, pygame, sys, operator, os, time
from pygame.locals import *

fps = 60
window_width = 1400
window_height = 800
cell_size = 50

assert window_width % cell_size == 0
assert window_height % cell_size == 0

cell_width = int(window_width / cell_size)
cell_height = int(window_height / cell_size)

# untuk warna

WHITE     = (255, 255, 255)
GREY      = (200, 200, 200)
PINK      = (198, 134, 156)
BLACK     = ( 17,  18,  13)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
ORANGE    = (255, 155, 111)

bg_color = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0

def main():
    global fps_clock, display_surf, basic_font
    global wall_coords, soft_wall_coords

    wall_coords = []
    soft_wall_coords = []
    soft_wall_coords = findSoftWall()
    wall_coords = findWall()

    pygame.init()

    fps_clock = pygame.time.Clock()
    display_surf = pygame.display.set_mode((window_width, window_height))
    basic_font = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snake Projek Teori')

    while True:
        runGame()
        showGameOverScreen()

def runGame():
    global stalling
    stalling = False
    stalling_count = -1

    start_x = 5
    start_y = 0

    snake_coords = [
        {'x' : start_x + 6, 'y' : start_y},
        {'x' : start_x + 5, 'y' : start_y},
        {'x' : start_x + 4, 'y' : start_y},
    ]

    direction = RIGHT
    direction_list = [RIGHT]
    path = []


    apple = {'x' : start_x + 8, 'y' : start_y}
    
    last_apple = {'x' : start_x - 1, 'y' : start_y - 1}

    path = calculatePath(snake_coords, apple, True)
    direction_list = calcDirection(path)
    last_wall = 0

    while True: # loop game utama
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()

        # cek jika snake kena badan sendiri atau edge
        if snake_coords[HEAD]['x'] == -1 or snake_coords[HEAD]['x'] == cell_width or snake_coords[HEAD]['y'] == -1 or snake_coords[HEAD]['y'] == cell_height:
            terminate()
            return
        
        for snake_body in snake_coords[1:]:
            if snake_body['x'] == snake_coords[HEAD]['x'] and snake_body['y'] == snake_coords[HEAD]['y']:
                terminate()
                return

        # cek snake udah makan apel
        if snake_coords[HEAD]['x'] == apple['x'] and snake_coords[HEAD]['y'] == apple['y']:
            last_apple = apple
            apple = getRandomLocation(snake_coords)

            path = calculatePath(snake_coords,apple,True)

            if not path:
                stalling = True
                stalling_count = 10000

            elif path == 'stall':
                stalling = True
                stalling_count = int(len(snake_coords)/2)
            
            else :
                direction_list = calcDirection(path)
        
        else:
            del snake_coords[-1]
        
        last_direction = direction

        # cari next direction

        if stalling and not direction_list:
            only_direction = calcOnlyDirection(snake_coords)

            if only_direction and only_direction == last_direction:
                direction_list.append(only_direction)
            
            else:
                if safeToGo(snake_coords, direction, last_wall):
                    direction_list.append(direction)
                
                elif(not findNewHead(direction, snake_coords) in snake_coords) or (findNewHead(direction,snake_coords) in wall_coords):
                    direction_list.append(direction)

                else:
                    last_direction = direction

                    path = calculatePath(snake_coords, apple, False)

                    if path != [] and path != 'stall':
                        stalling = False
                        stalling_count = -1
                        direction_list = calcDirection(path)
                    
                    else:
                        if checkLastWall(snake_coords):
                            last_wall = checkLastWall(snake_coords)
                        
                        direction_list.extend(findBetterDirection(snake_coords, direction, last_wall))

                        if calcArea(findNewHead(direction_list[0], snake_coords), snake_coords, last_wall) < 3:
                            direction_list = [last_direction]
                
                stalling_count = stalling_count - 1

                if stalling_count < 1:
                    stalling = False
                    prev_last_wall = last_wall
                    last_wall = 0
                    direction_list.append(last_direction)
                    path = calculatePath(snake_coords, apple, True)

                    if not path:
                        stalling = True
                        stalling_count = 10000
                        last_wall = prev_last_wall
                    
                    elif path == 'stall':
                        stalling = True
                        stalling_count = int(len(snake_coords)/2)
                        last_wall = prev_last_wall
                    
                    else:
                        direction_list = calcDirection(path)
                
        next_head = findNewHead(direction_list[0], snake_coords)

        if stalling:
            if AreaIsTooSmall(cell_width, next_head, snake_coords, last_wall):
                last_wall = 0
                direction_list = findNextDirection(snake_coords, direction_list[0],0)
        
        direction = direction_list.pop(0)
        new_head = findNewHead(direction, snake_coords)
        snake_coords.insert(0, new_head)
        display_surf.fill(bg_color) # background
        drawGrid()
        drawSnake(snake_coords) # snakenya
        drawApple(apple, last_apple)
        drawScore(len(snake_coords) - 3)
        pygame.display.update()
        fps_clock.tick(fps)

def calcOnlyDirection(snake):
    count = 4
    ways = getNeighborhood(snake[0])
    true_way = 0

    for each in ways:
        if each in snake:
            count = count - 1
        else:
            true_way = each
    
    if count == 1:
        return calcDirection([snake[0], true_way])
    
    else:
        return 0

def getNextWallCoords(last_wall):
    walls = []
    loop_count = 0

    # append left right walls

    for _ in range(cell_height):
        if last_wall == RIGHT:
            walls.append({'x' : 0, 'y' : loop_count})
        
        if last_wall == LEFT:
            walls.append({'x' : cell_width - 1, 'y' : loop_count})
        
        loop_count = loop_count + 1
    
    #append top bottom walls

    loop_count = 0

    for _ in range(cell_width):
        if last_wall == DOWN:
            walls.append({'x' : loop_count, 'y' : 0})
        
        if last_wall == UP:
            walls.append({'x' : loop_count, 'y' : cell_height - 1})

        loop_count = loop_count - 1

    return walls

def safeToGo(snake, direction, last_wall):
    list_of_num = wall_coords + snake
    list_of_num.extend(getNextWallCoords(last_wall))
    
    head = snake[0]
    forward = snake[0]
    forward_left = snake[0]
    forward_right = snake[0]
    left = snake[0]
    right = snake[0]

    if direction == UP:
        new_head = {'x' : snake[HEAD]['x'], 'y' : snake[HEAD]['y'] - 1}
        forward = {'x': snake[HEAD]['x'], 'y' : snake[HEAD]['y'] - 2}
        forward_left = {'x': snake[HEAD]['x']-1, 'y' : snake[HEAD]['y'] - 1}
        forward_right = {'x': snake[HEAD]['x']+1, 'y' : snake[HEAD]['y'] - 1}
        left = {'x' : snake[HEAD]['x']-1, 'y' : snake[HEAD]['y']}
        right = {'x' : snake[HEAD]['x']+1, 'y' : snake[HEAD]['y']}
    
    elif direction == DOWN:
        new_head = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1}
        forward = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 2}
        forward_left = {'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y'] + 1}
        forward_right = {'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y'] + 1}
        left = {'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y']}
        right = {'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y']}

    elif direction == LEFT:
        new_head = {'x': snake[HEAD]['x'] - 1, 'y': snake[HEAD]['y']}
        forward = {'x': snake[HEAD]['x'] - 2, 'y': snake[HEAD]['y']}
        forward_left = {'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y'] + 1}
        forward_right = {'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y'] - 1}
        left = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']+1}
        right = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']-1}

    elif direction == RIGHT:
        new_head = {'x': snake[HEAD]['x'] + 1, 'y': snake[HEAD]['y']}
        forward = {'x': snake[HEAD]['x'] + 2, 'y': snake[HEAD]['y']}
        forward_left = {'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y'] - 1}
        forward_right = {'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y'] + 1}
        left = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']-1}
        right = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']+1}

    if(forward_left in list_of_num and not left in list_of_num) or (forward_right in list_of_num and not right in list_of_num):
        return False
    
    if new_head in list_of_num:
        return False
    
    ways_to_go = []
    ways_to_go = getNeighborhood(new_head)
    count = len(ways_to_go)

    for each in ways_to_go:
        if each in list_of_num:
            count = count - 1
    
    if count < 1:
        return False
    
    elif count < 2 and not (forward in list_of_num):
        return False
    
    else:
        return True

def checkLastWall(snake):
    x = snake[0]['x']
    y = snake[0]['y']

    if x == 0:
        return LEFT
    
    elif x == cell_width - 1:
        return RIGHT
    
    elif y == 0:
        return UP
    
    elif y == cell_height - 1:
        return DOWN
    
    else:
        return 0

def checkSmartTurn(snake, list_of_num, dir1, dir2):
    if dir1 == UP or dir1 == DOWN:
        if dir2 == RIGHT:
            if {'x': snake[HEAD]['x']+3, 'y': snake[HEAD]['y']} in list_of_num and (not {'x': snake[HEAD]['x']+2, 'y': snake[HEAD]['y']} in list_of_num):
                return True
            else:
                return False

        if dir2 == LEFT:
            if {'x': snake[HEAD]['x']-3, 'y': snake[HEAD]['y']} in list_of_num and (not {'x': snake[HEAD]['x']-2, 'y': snake[HEAD]['y']} in list_of_num):
                return True            
            else:
                return False

    if dir1 == LEFT or dir1 == RIGHT:
        if dir2 == UP:
            if {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']-3} in list_of_num and (not {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']-2} in list_of_num):
                return True
            else:
                return False

        if dir2 == DOWN:
            if {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']+3} in list_of_num and (not {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']+2} in list_of_num):
                return True
            else:
                return False

def findBetterDirection(snake, direction, last_wall):
    list_of_num = list(snake)
    smart_turn = False

    if direction == UP:
        area_left = calcArea({'x' : snake[HEAD]['x']-1, 'y' : snake[HEAD]['y']},snake,last_wall)
        area_right = calcArea({'x' : snake[HEAD]['x']+1, 'y' : snake[HEAD]['y']},snake,last_wall)

        if area_left == 0 and area_right == 0:
            return [direction]
        
        area_straight = calcArea({'x' : snake[HEAD]['x'], 'y' : snake[HEAD]['y']-1},snake,last_wall)
        max_area = max(area_left, area_right, area_straight)
        
        if max_area == area_straight:
            return [direction]
        
        elif max_area == area_left:
            if checkSmartTurn(snake, list_of_num, direction, LEFT):
                return [LEFT, LEFT]
            
            else :
                return [LEFT, DOWN]
        
        else :
            if checkSmartTurn(snake, list_of_num, direction, RIGHT):
                return [RIGHT, RIGHT]
            
            else:
                return [RIGHT, DOWN]
    
    if direction == DOWN:
        area_left = calcArea({'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y']},snake,last_wall)
        area_right = calcArea({'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y']},snake,last_wall)

        if area_left == 0 and area_right == 0:
            return [direction]
        
        area_straight = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y']+1},snake,last_wall)
        max_area = max(area_left, area_right, area_straight)

        if max_area == area_straight:
            return [direction]
        
        elif area_left == max_area:
            if checkSmartTurn(snake, list_of_num, direction, LEFT):
                return [LEFT, LEFT]
            
            else:
                return [LEFT, UP]
        
        else:
            if checkSmartTurn(snake, list_of_num, direction, RIGHT):
                return [RIGHT, RIGHT]
            
            else:
                return [RIGHT, UP]
    
    elif direction == LEFT:
        area_up = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] - 1},snake,last_wall)
        area_down = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1},snake,last_wall)

        if area_up == 0 and area_down == 0:
            return [direction]

        area_straight = calcArea({'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y']},snake,last_wall)
        max_area = max(area_straight, area_up, area_down)

        if max_area == area_straight:
            return [direction]
        
        elif max_area == area_up:
            if checkSmartTurn(snake, list_of_num, direction, UP):
                return [UP, UP]
            
            else:
                return [UP, RIGHT]
        
        else:
            if checkSmartTurn(snake, list_of_num, direction, DOWN):
                return [DOWN, DOWN]
            
            else:
                return [DOWN, RIGHT]
    
    elif direction == RIGHT:
        area_up = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] - 1},snake,last_wall)
        area_down = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1},snake,last_wall)

        if area_up == 0 and area_down == 0:
            return [direction]

        area_straight = calcArea({'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y']},snake,last_wall)
        max_area = max(area_straight, area_up, area_down)

        if max_area == area_straight:
            return [direction]
        
        elif area_up == max_area:
            if checkSmartTurn(snake, list_of_num, direction, UP):
                return [UP, UP]
            
            else:
                return [UP, LEFT]
        
        else:
            if checkSmartTurn(snake, list_of_num, direction, DOWN):
                return [DOWN, DOWN]
            
            else:
                return [DOWN, LEFT]

def findNextDirection(snake, direction, last_wall):
    list_of_num = list(snake)
    area_left = calcArea({'x': snake[HEAD]['x']-1, 'y': snake[HEAD]['y']},snake,last_wall)
    area_right = calcArea({'x': snake[HEAD]['x']+1, 'y': snake[HEAD]['y']},snake,last_wall)
    area_up = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] - 1},snake,last_wall)
    area_down = calcArea({'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1},snake,last_wall)
    max_area = max(area_left,area_right,area_up,area_down)

    if max_area == area_up:
      return [UP]

    elif max_area == area_down:
      return [DOWN]

    elif max_area == area_left:
      return [LEFT]

    else:
      return [RIGHT]

def calcArea(point, snake, last_wall):
    next_wall = getNextWallCoords(last_wall)
    if point in snake or point in wall_coords or point in next_wall:
        return 0
    tail_bonus = 0

    q = []
    search_points = []
    search_points.append(point)

    while(search_points):
        i = search_points.pop()
        for each in getNeighborhood(i):
            if not each in q:
                if not(each in snake or each in wall_coords or point in next_wall):
                    search_points.append(each)
                if each == snake[-1]:
                    tail_bonus = 200
        q.append(i)
    return len(q) + tail_bonus

def AreaIsTooSmall(bound, point, snake, last_wall):
    next_wall = getNextWallCoords(last_wall)
    if point in snake or point in wall_coords or point in next_wall:
        return True
    
    tail_bonus = 0
    q = []
    search_points = []
    search_points.append(point)

    while(search_points):
        i = search_points.pop()
        for each in getNeighborhood(i):
            if not each in q:
                if not(each in snake or each in wall_coords or point in next_wall):
                    search_points.append(each)
            
            if each == snake[-1]:
                tail_bonus = 200
        
        q.append(i)

        if(len(q) + tail_bonus) > bound:
            return False
    
    return True

def calcCost(point, snake):
    neighbors = getNeighborhood(point)
    for each in neighbors:
        if each in snake[1:]:
            return snake.index(each)
    
    return 999

def calcDirection(path):
    # mengubah point-path ke arah yang berbentuk step-by-step
    last_point = path[0]
    directions = []
    next_direction = ''
    for current_point in path:
        if(current_point['x'] > last_point['x']):
            next_direction = RIGHT
        
        elif(current_point['x'] < last_point['x']):
            next_direction = LEFT

        else:
            if(current_point['y'] > last_point['y']):
                next_direction = DOWN
            
            elif(current_point['y'] < last_point['y']):
                next_direction = UP
            
            else:
                continue
        
        last_point = current_point
        directions.append(next_direction)
    
    return directions

def calculatePath(snake, apple, softCalculation):
    old_snake = list(snake)
    path = mainCalculation(snake, apple, softCalculation)

    if not path:
        return []
    
    else:
        path_copy = list(path)
        path_copy.reverse()
        new_snake = path_copy + old_snake
        path_out = mainCalculation(new_snake, new_snake[-1], False)

        if not path_out:
            return 'stall'
        
        else:
            return path

def mainCalculation(snake, apple, softCalculation):
    points_to_path = []
    discover_edge = []
    new_points = []
    exhausted_points = []
    number_of_points = 1 # jika semua poin sudah dicoba kembali ke 1 poin
    finding_path = True
    list_of_num = getListOfNum(snake)
    soft_list_of_num = getSoftListOfNum(snake)
    soft_list_of_num.extend(soft_wall_coords)
    discover_edge.append(snake[0])
    exhausted_points.append(snake[0])
    last_point = discover_edge[-1]
    points_to_path.append(last_point)

    if(apple in soft_wall_coords) or (apple in soft_list_of_num):
        softCalculation = False

    # menghitung jalan yang ada
    while(finding_path and softCalculation):
        last_point = discover_edge[-1]
        new_points = getNeighborhood(last_point)
        new_points = sorted(new_points, key = lambda k: calcDistance(k, apple), reverse = True) # sort point baru
        number_of_points = len(new_points)

        for point in new_points:
            if point in soft_list_of_num:
                number_of_points = number_of_points - 1
            
            elif point in exhausted_points:
                number_of_points = number_of_points - 1
            
            else:
                discover_edge.append(point)
                points_to_path.append(last_point)
                exhausted_points.append(last_point)
        
        if number_of_points == 0: # backtrack
            exhausted_points.append(discover_edge.pop())
            exhausted_points.append(points_to_path.pop())
        
        if apple in discover_edge:
            finding_path = 0
        
        if not discover_edge:
            softCalculation = False
            break
    
    if not softCalculation:
        points_to_path = []
        discover_edge = []
        new_points = []
        exhausted_points = []
        number_of_points = 1
        finding_path = True
        list_of_num = getListOfNum(snake)
        discover_edge.append(snake[0])
        exhausted_points.append(snake[0])
        last_point = discover_edge[-1]
        points_to_path.append(last_point)

        # hitung path yang ada
        while(finding_path):
            last_point = discover_edge[-1]
            new_points = getNeighborhood(last_point)
            new_points = sorted(new_points, key = lambda k: calcDistance(k, apple), reverse = True) #sort point baru
            number_of_points = len(new_points)

            for point in new_points:
                if point in list_of_num:
                    number_of_points = number_of_points - 1
                
                elif point in exhausted_points:
                    number_of_points = number_of_points - 1
                
                else:
                    discover_edge.append(point)
                    points_to_path.append(last_point)
                    exhausted_points.append(last_point)
            
            if number_of_points == 0:
                exhausted_points.append(discover_edge.pop())
                exhausted_points.append(points_to_path.pop())
            
            if apple in discover_edge:
                finding_path = 0
            
            if not discover_edge:
                return []
        
    # ketika discover edge kosong, langsung cari buntut
    points_to_path.append(apple)
    return points_to_path

def getNeighborhood(point):
    neighborhood = []

    if point['x'] < cell_width:
        neighborhood.append({'x':point['x']+1,'y':point['y']})
    
    if point['x'] > 0:
        neighborhood.append({'x':point['x']-1,'y':point['y']})
    
    if point['y'] < cell_height:
        neighborhood.append({'x':point['x'],'y':point['y']+1})
    
    if point['y'] > 0:
        neighborhood.append({'x':point['x'],'y':point['y']-1})
    
    return neighborhood

def calcDistance(point, apple):
    distance = abs(point['x'] - apple['x']) + abs(point['y'] - apple['y'])
    return distance

def getSoftListOfNum(snake):
    list_of_num = []
    list_of_num.extend(getSnakeSurroundings(snake))
    return list_of_num

def getSnakeSurroundings(snake):
    list_of_num = []
    headx = snake[0]['x']
    heady = snake[0]['y']
    count = 0

    for each in snake:
        if count == 0:
            list_of_num.append(each)
        
        else:
            dist = abs(each['x'] - headx) + abs(each['y'] - heady)
            count_from_behind = len(snake) - count
            if dist < (count_from_behind + 1):
                list_of_num.append(each)
                list_of_num.append({'x':each['x']+1,'y':each['y']})
                list_of_num.append({'x':each['x']-1,'y':each['y']})
                list_of_num.append({'x':each['x'],'y':each['y']+1})
                list_of_num.append({'x':each['x'],'y':each['y']-1})
                list_of_num.append({'x':each['x']+1,'y':each['y']+1})
                list_of_num.append({'x':each['x']-1,'y':each['y']-1})
                list_of_num.append({'x':each['x']-1,'y':each['y']+1})
                list_of_num.append({'x':each['x']+1,'y':each['y']-1})
        count = count + 1
    
    seen = set()
    new_list = []

    for d in list_of_num:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_list.append(d)
    return new_list

def getListOfNum(snake):
    list_of_num = []
    headx = snake[0]['x']
    heady = snake[0]['y']
    count = 0
    
    for each in snake:
        dist = abs(each['x'] - headx) + abs(each['y'] - heady)
        count_from_behind = len(snake) - count
        count = count + 1

        if dist < (count_from_behind + 1):
            list_of_num.append(each)
    
    list_of_num.extend(wall_coords)
    return list_of_num

def findWall():
    walls = []

    # append LEFT RIGHT walls
    loopcount = 0
    for _ in range(cell_height):
        walls.append({'x' : -1, 'y' : loopcount})
        walls.append({'x' : cell_width, 'y' : loopcount})
        loopcount = loopcount + 1
    
    # append TOP BOTTOM walls
    loopcount = 0
    for _ in range(cell_width):
        walls.append({'x' : loopcount, 'y' : -1})
        walls.append({'x' : loopcount, 'y' : cell_height})
        loopcount = loopcount + 1

    return walls

def findSoftWall():
    walls = []
    
    # append LEFT RIGHT walls
    loopcount = 0
    for _ in range(cell_height):
        walls.append({'x' : 0, 'y' : loopcount})
        walls.append({'x' : cell_width-1, 'y' : loopcount})
        loopcount = loopcount + 1
    
    #append TOP BOTTOM walls
    loopcount = 0
    for _ in range(cell_width):
        walls.append({'x' : loopcount, 'y' : 0})
        walls.append({'x' : loopcount, 'y' : cell_height-1})
        loopcount = loopcount + 1

    return walls

def drawEdgeOfDiscorvery(points):
    for point in points:
        x = point['x'] * cell_size
        y = point['y'] * cell_size
        snake_segment_rect = pygame.Rect(x, y, cell_size, cell_size)
        pygame.draw.rect(display_surf, ORANGE, snake_segment_rect)
    
    last_point_rect = pygame.Rect(points[-1]['x'] * cell_size, points[-1]['y'] * cell_size, cell_size, cell_size)
    pygame.draw.rect(display_surf, (255,255,255), snake_segment_rect)

def pauseGame():
    pauseGame = True
    while (pauseGame):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    pauseGame = False


def oppositeDirection(direction):
    if direction == UP:
        return DOWN

    elif direction == DOWN:
        return UP

    elif direction == LEFT:
        return RIGHT

    elif direction == RIGHT:
        return LEFT

def findNewHead(direction, snake_coords):
    if direction == UP:
        new_head = {'x' : snake_coords[HEAD]['x'], 'y' : snake_coords[HEAD]['y'] - 1}
    
    elif direction == DOWN:
        new_head = {'x' : snake_coords[HEAD]['x'], 'y' : snake_coords[HEAD]['y'] + 1}
    
    elif direction == LEFT:
        new_head = {'x' : snake_coords[HEAD]['x'] - 1, 'y' : snake_coords[HEAD]['y']}
    
    elif direction == RIGHT:
        new_head = {'x' : snake_coords[HEAD]['x'] + 1, 'y' : snake_coords[HEAD]['y']}
    
    return new_head


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None

    if keyUpEvents[0].key == K_ESCAPE:
        terminate()

    return keyUpEvents[0].key


def terminate():
    print('You Died!')
    pauseGame()
    pygame.quit()
    sys.exit()

def getRandomLocation(snake):
    location = {'x' : random.randint(0, cell_width - 1), 'y' : random.randint(0, cell_height - 1)}

    while(location in snake):
        location = {'x' : random.randint(0, cell_width - 1), 'y' : random.randint(0, cell_height - 1)}
    
    return location

def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (window_width / 2, 10)
    overRect.midtop = (window_width / 2, gameRect.height + 10 + 25)
    display_surf.blit(gameSurf, gameRect)
    display_surf.blit(overSurf, overRect)
    
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    score_surf = basic_font.render('Score: %s' % (score), True, GREEN)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (window_width - 120, 10)
    display_surf.blit(score_surf, score_rect)

def drawSnake(snake_coords):
    for coord in snake_coords:
        x = coord['x'] * cell_size
        y = coord['y'] * cell_size
        snake_inner_segment_rect = pygame.Rect(x + 1, y + 1, cell_size - 2, cell_size - 2)
        pygame.draw.rect(display_surf, WHITE, snake_inner_segment_rect)

def drawApple(coord, last_apple):
    x = coord['x'] * cell_size
    y = coord['y'] * cell_size
    apple_rect = pygame.Rect(x, y, cell_size, cell_size)
    pygame.draw.rect(display_surf, RED, apple_rect)

def drawGrid():
    return # tidak melakukan apa2

    for x in range(0, window_width, cell_size): # gambar garis vertikal
        pygame.draw.line(display_surf, DARKGRAY, (x, 0), (x, window_height))
    
    for y in range(0, window_height, cell_size): # gambar garis horizontal
        pygame.draw.line(display_surf, DARKGRAY, (0, y), (window_width, y))

if __name__ == '__main__':
    main()
