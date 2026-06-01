import tkinter as tk
import random
import time

WIDTH = 600
HEIGHT = 600
CELL = 20
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL
MOVE_MS = 200
FRAME_MS = 16

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("貪食蛇")
        self.root.resizable(False, False)

        frame = tk.Frame(root, bg="#1a1a2e")
        frame.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(frame, width=WIDTH + 2, height=HEIGHT + 2,
                                bg="#16213e", highlightthickness=2,
                                highlightbackground="#0f3460")
        self.canvas.pack()

        bottom = tk.Frame(frame, bg="#1a1a2e")
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.score_label = tk.Label(bottom, text="分數: 0", font=("Arial", 16, "bold"),
                                    fg="#e94560", bg="#1a1a2e")
        self.score_label.pack(side=tk.LEFT, padx=5)

        tk.Label(bottom, text="  |  ", font=("Arial", 16), fg="#533483", bg="#1a1a2e").pack(side=tk.LEFT)

        self.length_label = tk.Label(bottom, text="長度: 1", font=("Arial", 16, "bold"),
                                     fg="#00b4d8", bg="#1a1a2e")
        self.length_label.pack(side=tk.LEFT, padx=5)

        tk.Button(bottom, text="重新開始", font=("Arial", 12, "bold"),
                  bg="#e94560", fg="white", bd=0, padx=15, pady=4,
                  cursor="hand2", activebackground="#c23152",
                  activeforeground="white", command=self.restart).pack(side=tk.RIGHT, padx=5)

        tk.Label(frame, text="方向鍵 ↑ ↓ ← → 控制蛇的移動",
                 font=("Arial", 11), fg="#888888", bg="#1a1a2e").pack(pady=(4, 0))

        self.build_bg()
        self.build_eyes()
        self.segs = []
        self.build_overlay()
        self.restart()
        self.canvas.focus_set()
        self.canvas.bind("<KeyPress>", self.change_dir)
        self.loop()

    def build_bg(self):
        self.canvas.create_rectangle(1, 1, WIDTH + 1, HEIGHT + 1, fill="#1a1a2e", outline="")
        for i in range(COLS + 1):
            x = i * CELL + 1
            self.canvas.create_line(x, 1, x, HEIGHT + 1, fill="#16213e", width=1)
        for i in range(ROWS + 1):
            y = i * CELL + 1
            self.canvas.create_line(1, y, WIDTH + 1, y, fill="#16213e", width=1)

        self.food_body = self.canvas.create_oval(0, 0, 0, 0, fill="#e63946",
                                                  outline="#c1121f", width=2, state="hidden")
        self.food_shine = self.canvas.create_oval(0, 0, 0, 0, fill="#ff8fa3",
                                                   outline="", state="hidden")
        self.food_stem = self.canvas.create_line(0, 0, 0, 0, fill="#5c3a21",
                                                  width=2, state="hidden")
        self.food_leaf = self.canvas.create_oval(0, 0, 0, 0, fill="#2a9d8f",
                                                  outline="", state="hidden")

    def build_eyes(self):
        self.eye_white1 = self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="", state="hidden")
        self.eye_white2 = self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="", state="hidden")
        self.eye_pupil1 = self.canvas.create_oval(0, 0, 0, 0, fill="black", outline="", state="hidden")
        self.eye_pupil2 = self.canvas.create_oval(0, 0, 0, 0, fill="black", outline="", state="hidden")

    def build_overlay(self):
        self.over_bg = self.canvas.create_rectangle(0, 0, 0, 0, fill="#1a1a2e",
                                                     outline="#e94560", width=3, state="hidden")
        self.over_title = self.canvas.create_text(0, 0, text="GAME OVER", fill="#e94560",
                                                   font=("Arial", 36, "bold"), state="hidden")
        self.over_score = self.canvas.create_text(0, 0, text="", fill="white",
                                                   font=("Arial", 18), state="hidden")
        self.over_hint = self.canvas.create_text(0, 0, text="按「重新開始」再玩一次",
                                                  fill="#888888", font=("Arial", 12), state="hidden")

    def restart(self):
        self.old_snake = [(COLS // 2, ROWS // 2)]
        self.snake = [(COLS // 2, ROWS // 2)]
        self.direction = (1, 0)
        self.move_dir = (1, 0)
        self.score = 0
        self.length_label.config(text="長度: 1")
        self.score_label.config(text="分數: 0")
        self.running = True
        self.food = None
        self.spawn_food()
        self.move_start = time.time()
        self.canvas.itemconfig(self.over_bg, state="hidden")
        self.canvas.itemconfig(self.over_title, state="hidden")
        self.canvas.itemconfig(self.over_score, state="hidden")
        self.canvas.itemconfig(self.over_hint, state="hidden")
        self.canvas.focus_set()

    def ensure_segs(self, n):
        while len(self.segs) < n:
            item = self.canvas.create_oval(0, 0, 0, 0, fill="", outline="", state="hidden")
            self.segs.append(item)

    def spawn_food(self):
        while True:
            pos = (random.randrange(COLS), random.randrange(ROWS))
            if pos not in self.snake:
                self.food = pos
                break

    def change_dir(self, event):
        key_map = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
        d = key_map.get(event.keysym)
        if d and (d[0] != -self.direction[0] or d[1] != -self.direction[1]):
            self.direction = d

    def move_snake(self):
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if (new_head[0] < 0 or new_head[0] >= COLS or
            new_head[1] < 0 or new_head[1] >= ROWS or
            new_head in self.snake):
            self.game_over()
            return

        self.old_snake = list(self.snake)
        self.move_dir = self.direction
        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"分數: {self.score}")
            self.length_label.config(text=f"長度: {len(self.snake)}")
            self.spawn_food()
        else:
            self.snake.pop()
        self.move_start = time.time()

    def loop(self):
        now = time.time()
        dt = (now - self.move_start) * 1000

        if self.running and dt >= MOVE_MS:
            self.move_snake()

        lerp = min((time.time() - self.move_start) * 1000 / MOVE_MS, 1.0)
        self.draw(lerp)
        self.root.after(FRAME_MS, self.loop)

    def draw_snake(self, lerp):
        n = len(self.snake)
        self.ensure_segs(n)

        for i in range(n):
            ox, oy = self.old_snake[i] if i < len(self.old_snake) else self.snake[i]
            nx, ny = self.snake[i]

            x = ox + (nx - ox) * lerp
            y = oy + (ny - oy) * lerp

            pad = 2
            x1 = x * CELL + pad + 1
            y1 = y * CELL + pad + 1
            x2 = (x + 1) * CELL - pad + 1
            y2 = (y + 1) * CELL - pad + 1

            t = i / max(n - 1, 1)
            r = int(30 + t * 90)
            g = int(180 - t * 60)
            b = int(30 + t * 40)
            color = f"#{r:02x}{g:02x}{b:02x}"

            self.canvas.coords(self.segs[i], x1, y1, x2, y2)
            self.canvas.itemconfig(self.segs[i], fill=color, state="normal")

        for i in range(n, len(self.segs)):
            self.canvas.itemconfig(self.segs[i], state="hidden")

        md = self.move_dir
        hx, hy = self.snake[0]
        phx = hx - md[0] * (1 - lerp)
        phy = hy - md[1] * (1 - lerp)
        cx = phx * CELL + CELL // 2 + 1
        cy = phy * CELL + CELL // 2 + 1
        eo = 4

        if md in ((1, 0), (-1, 0)):
            dx = 3 if md == (1, 0) else -3
            self.canvas.coords(self.eye_white1, cx + dx - 2, cy - eo - 2, cx + dx + 2, cy - eo + 2)
            self.canvas.coords(self.eye_white2, cx + dx - 2, cy + eo - 2, cx + dx + 2, cy + eo + 2)
            self.canvas.coords(self.eye_pupil1, cx + dx - 1, cy - eo - 1, cx + dx + 1, cy - eo + 1)
            self.canvas.coords(self.eye_pupil2, cx + dx - 1, cy + eo - 1, cx + dx + 1, cy + eo + 1)
        else:
            dy = 3 if md == (0, 1) else -3
            self.canvas.coords(self.eye_white1, cx - eo - 2, cy + dy - 2, cx - eo + 2, cy + dy + 2)
            self.canvas.coords(self.eye_white2, cx + eo - 2, cy + dy - 2, cx + eo + 2, cy + dy + 2)
            self.canvas.coords(self.eye_pupil1, cx - eo - 1, cy + dy - 1, cx - eo + 1, cy + dy + 1)
            self.canvas.coords(self.eye_pupil2, cx + eo - 1, cy + dy - 1, cx + eo + 1, cy + dy + 1)

        self.canvas.itemconfig(self.eye_white1, state="normal")
        self.canvas.itemconfig(self.eye_white2, state="normal")
        self.canvas.itemconfig(self.eye_pupil1, state="normal")
        self.canvas.itemconfig(self.eye_pupil2, state="normal")

    def draw_food(self):
        if self.running and self.food:
            fx, fy = self.food
            cx = fx * CELL + CELL // 2 + 1
            cy = fy * CELL + CELL // 2 + 1

            self.canvas.coords(self.food_body, cx - 8, cy - 7, cx + 8, cy + 8)
            self.canvas.itemconfig(self.food_body, state="normal")
            self.canvas.coords(self.food_shine, cx - 4, cy - 5, cx + 1, cy)
            self.canvas.itemconfig(self.food_shine, state="normal")
            self.canvas.coords(self.food_stem, cx + 2, cy - 8, cx + 1, cy - 12)
            self.canvas.itemconfig(self.food_stem, state="normal")
            self.canvas.coords(self.food_leaf, cx - 1, cy - 14, cx + 5, cy - 9)
            self.canvas.itemconfig(self.food_leaf, state="normal")

        if not self.running:
            self.canvas.itemconfig(self.food_body, state="hidden")
            self.canvas.itemconfig(self.food_shine, state="hidden")
            self.canvas.itemconfig(self.food_stem, state="hidden")
            self.canvas.itemconfig(self.food_leaf, state="hidden")

    def draw(self, lerp):
        self.draw_food()
        self.draw_snake(lerp)

    def game_over(self):
        self.running = False
        self.canvas.coords(self.over_bg, 80, HEIGHT // 2 - 60, WIDTH - 78, HEIGHT // 2 + 60)
        self.canvas.itemconfig(self.over_bg, state="normal")
        self.canvas.coords(self.over_title, WIDTH // 2 + 1, HEIGHT // 2 - 18)
        self.canvas.itemconfig(self.over_title, state="normal")
        self.canvas.coords(self.over_score, WIDTH // 2 + 1, HEIGHT // 2 + 22)
        self.canvas.itemconfig(self.over_score, text=f"得分: {self.score}", state="normal")
        self.canvas.coords(self.over_hint, WIDTH // 2 + 1, HEIGHT // 2 + 48)
        self.canvas.itemconfig(self.over_hint, state="normal")
        self.canvas.itemconfig(self.eye_white1, state="hidden")
        self.canvas.itemconfig(self.eye_white2, state="hidden")
        self.canvas.itemconfig(self.eye_pupil1, state="hidden")
        self.canvas.itemconfig(self.eye_pupil2, state="hidden")

if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
