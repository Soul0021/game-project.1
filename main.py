import turtle
import time
import math
import os

# Set up the game screen
W = turtle.Screen()
W.bgcolor("black")
W.title("The Labyrinth Of Soul")
W.setup(width=1.0, height=1.0)
W.tracer(0)


# Define the path to the image directory
image_dir = r"C:/Users/Angel Jane D. Labuyo/PycharmProjects/game_project/.resources"

# Register shapes using the full path
images = ["player_right.gif", "player_left.gif", "player_attack_right.gif", "player_attack_left.gif", "treasure.gif",
          "wall.gif", "enemy.gif", "exit.gif"]
for image in images:
    turtle.register_shape(os.path.join(image_dir, image))

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to node
        self.h = 0  # Heuristic cost from node to end
        self.f = 0  # Total cost

    def __eq__(self, other):
        return self.position == other.position

def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def a_star(start, end):
    start_node = Node(start)
    end_node = Node(end)

    open_list = []
    closed_list = []

    open_list.append(start_node)

    while open_list:
        current_node = min(open_list, key=lambda o: o.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]

        children = []
        for new_position in [(0, -22), (0, 22), (-22, 0), (22, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if node_position in walls:
                continue

            new_node = Node(node_position, current_node)
            children.append(new_node)

        for child in children:
            if child in closed_list:
                continue

            child.g = current_node.g + 1
            child.h = heuristic(child.position, end_node.position)
            child.f = child.g + child.h

            if child in open_list:
                existing_node = next(node for node in open_list if node == child)
                if child.g < existing_node.g:
                    existing_node.g = child.g
                    existing_node.f = child.f
                    existing_node.parent = current_node
            else:
                open_list.append(child)

class Pen(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.shape("square")
        self.color("black")
        self.penup()
        self.speed(0)


class Player(turtle.Turtle):
    def __init__(self):
        turtle.Turtle.__init__(self)
        self.shape(os.path.join(image_dir, "player_right.gif"))
        self.color("darkgreen")
        self.penup()
        self.speed(0)
        self.soul = 0
        self.speed_multiplier = 1
        self.direction = "right"
        self.attack_in_progress = False

    def run_down(self):
        move_to_x = self.xcor()
        move_to_y = self.ycor() - 22
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def run_up(self):
        move_to_x = self.xcor()
        move_to_y = self.ycor() + 22
        if (move_to_x, move_to_y) not in walls:
            self.goto(move_to_x, move_to_y)

    def run_right(self):
        move_to_x = self.xcor() + 22
        move_to_y = self.ycor()
        if (move_to_x, move_to_y) not in walls:
            self.shape(os.path.join(image_dir, "player_right.gif"))
            self.direction = "right"
            self.goto(move_to_x, move_to_y)

    def run_left(self):
        move_to_x = self.xcor() - 22
        move_to_y = self.ycor()
        if (move_to_x, move_to_y) not in walls:
            self.shape(os.path.join(image_dir, "player_left.gif"))
            self.direction = "left"
            self.goto(move_to_x, move_to_y)

    def attack(self):
        if not self.attack_in_progress:
            self.attack_in_progress = True
            attack_image = os.path.join(image_dir,
                                        "player_attack_right.gif") if self.direction == "right" else os.path.join(
                image_dir,
                "player_attack_left.gif")
            self.shape(attack_image)
            W.update()
            self.check_for_collisions()
            W.ontimer(self.end_attack, 300)  # Schedule to end attack animation after 300ms

    def check_for_collisions(self):
        for enemy in enemies:
            if self.is_collision(enemy):
                enemy.hideturtle()
                enemies.remove(enemy)
                self.soul += enemy.soul
                update_score()

    def end_attack(self):
        self.attack_in_progress = False
        self.shape(os.path.join(image_dir, f"player_{self.direction}.gif"))
        W.update()

    def is_collision(self, other):
        a = self.xcor() - other.xcor()
        b = self.ycor() - other.ycor()
        distance = math.sqrt((a ** 2) + (b ** 2))
        return distance < 20


class Treasure(turtle.Turtle):
    def __init__(self, x, y):
        turtle.Turtle.__init__(self)
        self.shape(os.path.join(image_dir, "treasure.gif"))
        self.color("grey")
        self.penup()
        self.speed(0)
        self.soul = 10
        self.goto(x, y)

    def destroy(self):
        self.goto(3000, 3000)
        self.hideturtle()

class Exit(turtle.Turtle):
    def __init__(self, x, y):
        turtle.Turtle.__init__(self)
        self.shape(os.path.join(image_dir, "exit.gif"))
        self.color("blue")
        self.penup()
        self.speed(0)
        self.goto(x, y)
        self.hideturtle()

    def show_exit(self):
        self.showturtle()

class Enemy(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.shape(os.path.join(image_dir, "enemy.gif"))
        self.color("red")
        self.penup()
        self.speed(0)
        self.soul = 1
        self.goto(x, y)
        self.path = []
        self.move_active = False

    def move(self):
        if not self.path or player.position() != self.path[-1]:
            self.path = a_star(self.position(), player.position())
        if self.path:
            next_move = self.path.pop(0)
            self.goto(next_move)

        if not self.move_active:
            self.move_active = True
            turtle.ontimer(self.activate_move, t=100)

    def activate_move(self):
        self.move_active = False
        self.move()

pen = Pen()
player = Player()

score_display = turtle.Turtle()
score_display.color("white")
score_display.penup()
score_display.hideturtle()
score_display.goto(300, 300)

walls = []
treasures = []
enemies = []
exit = None

level_1 = [
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XPOTOXXXXXXXXXXOOOOOOOOOOXXXXX",
    "XOOOOOXXXXXXXOOOOOXXXTOOOOOXXX",
    "XXOOOOOXOOOOOOOOXXXXXXOOOOOOXX",
    "XXXOOOOOOOOOOOOXXXXXOOOOOOOXXX",
    "XOOXXOOOOOOOXOOOXXXOOOOOXXXXXX",
    "XOOOXOOOOOOXXOOOOXXOOOOXXXXXXX",
    "XXOOOOOXXOOOOOOOXXXOOOOOXXXXXX",
    "XOOOOXXXXXOOOOOOXXOOOOOTOOOXXX",
    "XOOXXXXXXXOOOOOOOXOOOOOOOOOOXX",
    "XXXXXXXXXOOOOOOOOOEOOOOOOOOOOX",
    "XXOOXXXXOOOOOXXOOOOXXOOOXXOOOX",
    "XOOOXXXOOOOOXXOOOOOOXXXXXXOTOX",
    "XXOOOXXXOOOOXXOOOOOOOXXXXXOOOX",
    "XOOOXXXXOOOOOOXXXXXXXXXOOOTOOX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXOXX"
]

level_2 = [
    "XPOOOXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XOOOOOXXXXXXXOOOOOXXXOOXXXXXXX",
    "XOOOOOOXXOOOOOOOXXXXXXOOOOOOXX",
    "XOXXOOOOOOOOOOOXXXXXOOOOOOOXXX",
    "XOOXXXOOOOOOXOOOXXXOOOOOXXXXXX",
    "XXXOXOOOOOOXXOOOOXXOOOOXXXXXXX",
    "XXOOOOOXXOOOOOOOXXXOOOOOXXXXXX",
    "XOOOOXXXXXOOOOOOXXOOOOOOOOOXXX",
    "XOOXXXXXXXOOOOOOOXOOOEOOOOOOXX",
    "XOOOXXOOOOOOOOOOXXXXOOETOOOOOX",
    "XOOOXXXOOOOEOOOOOOXXOOOOOOOOOX",
    "XOOOXXXXOOOXXOOOOOOOOOOOOOOOOX",
    "XOOOXXXXXXOOOOOOOOOOOOOOOOOXXX",
    "XOOOOXXOOOOOOOOOXXXXXXXXOOXXXX",
    "XOOOOOOOXXOOOXXXXXXXXXXXXOOOXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXOXX"
]

levels = [level_1, level_2]

def setup_maze(level):
    global exit
    global walls, treasures, enemies
    walls = []
    treasures = []
    enemies = []
    for y in range(len(level)):
        for x in range(len(level[y])):
            character = level[y][x]
            screen_x = -325 + (x * 22)
            screen_y = 325 - (y * 22)

            if character == "X":
                pen.goto(screen_x, screen_y)
                pen.shape(os.path.join(image_dir, "wall.gif"))
                pen.stamp()
                walls.append((screen_x, screen_y))

            if character == "P":
                player.goto(screen_x, screen_y)

            if character == "T":
                treasures.append(Treasure(screen_x, screen_y))

            if character == "E":
                enemies.append(Enemy(screen_x, screen_y))

            if character == "O":
                exit = Exit(screen_x, screen_y)

turtle.listen()
turtle.onkey(player.run_down, "Down")
turtle.onkey(player.run_up, "Up")
turtle.onkey(player.run_right, "Right")
turtle.onkey(player.run_left, "Left")
turtle.onkey(player.attack, "space")

def display_message(message):
    message_pen = turtle.Turtle()
    message_pen.color("yellow")
    message_pen.penup()
    message_pen.hideturtle()
    message_pen.goto(0, 0)
    message_pen.write(message, align="center", font=("Arial", 36, "normal"))
    W.update()
    time.sleep(2)
    message_pen.clear()

def game_over():
    game_over_pen = turtle.Turtle()
    game_over_pen.color("red")
    game_over_pen.penup()
    game_over_pen.hideturtle()
    game_over_pen.goto(0, 0)
    game_over_pen.write("GAME OVER", align="center", font=("Arial", 36, "normal"))
    W.update()
    time.sleep(3)
    W.bye()

def update_score():
    score_display.clear()
    score_display.write("Player Souls: {}".format(player.soul), align="center", font=("Arial", 24, "normal"))
    W.update()  # Force the screen to refresh

def clear_maze():
    pen.clear()
    walls.clear()
    for treasure in treasures:
        treasure.destroy()
    treasures.clear()
    for enemy in enemies:
        enemy.hideturtle()
    enemies.clear()

level_index = 0
while True:
    setup_maze(levels[level_index])

    for enemy in enemies:
        turtle.ontimer(enemy.move, t=100)

    while True:
        for treasure in treasures:
            if player.is_collision(treasure):
                player.soul += treasure.soul
                print("Player Souls: {}".format(player.soul))
                treasure.destroy()
                treasures.remove(treasure)
                player.speed_multiplier += 0.1
                update_score()

        for enemy in enemies:
            if player.is_collision(enemy):
                game_over()
                break

        if len(treasures) == 0 and exit is not None:
            exit.show_exit()

        if exit is not None and player.is_collision(exit):
            clear_maze()
            level_index += 1
            if level_index < len(levels):
                display_message("LEVEL COMPLETED!")
            else:
                display_message("CONGRATULATIONS! YOU WIN!")
                W.bye()
                break
            break

        W.update()

turtle.done()