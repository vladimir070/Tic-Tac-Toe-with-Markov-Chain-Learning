import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import json  # Добавляем import для работы с JSON

# Глобальные переменные
board = [' '] * 9
current_player = 'X'
last_computer_move = None
game_history = []
buttons = []  # Инициализируем список кнопок
heatmap_canvas = None # Инициализируем heatmap_canvas как None

winning_combinations = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
]

# Инициализация цепи Маркова
def initialize_markov_chain():  # Оставляем функцию инициализации
    chain = {}
    for i in range(9):
        chain[i] = {}
        for j in range(9):
            chain[i][j] = 1.0
    return chain

markov_chain = None # Инициализируем markov_chain как None

def load_markov_chain(filename="markov_chain.json"):
    global markov_chain
    try:
        with open(filename, 'r') as f:
            markov_chain = json.load(f)
        print("Цепь Маркова загружена из файла.")
    except FileNotFoundError:
        print("Файл не найден. Инициализирована новая цепь Маркова.")
        markov_chain = initialize_markov_chain()


# Основные функции
def reset_board():
    global board, current_player, last_computer_move, game_history
    board = [' '] * 9
    current_player = 'X'
    last_computer_move = None
    game_history = []
    if buttons: # Проверяем инициализацию кнопок
        for button in buttons:
            button.config(text=' ')
    update_heatmap()

def check_winner(board, player):
    for combo in winning_combinations:
        if all(board[i] == player for i in combo):
            return True
    return False

def is_board_full(board):
    return ' ' not in board

# Функции цепи Маркова
def update_markov_chain(prev_move, next_move, reward):
    if prev_move is None or next_move is None:
        return

    learning_rate = 0.9  # Увеличили learning_rate
    markov_chain[prev_move][next_move] += learning_rate * reward

    # Гарантируем положительные значения
    for move in markov_chain[prev_move]:
        markov_chain[prev_move][move] = max(0.01, markov_chain[prev_move][move]) # Изменили min значение

    # Нормализация
    total = sum(markov_chain[prev_move].values())
    for move in markov_chain[prev_move]:
        markov_chain[prev_move][move] /= total

def get_computer_move(board, chain, last_move):
    possible_moves = [i for i, cell in enumerate(board) if cell == ' ']
    if not possible_moves:
        return None

    if last_move is None:
        return random.choice(possible_moves)

    # Добавляем случайность
    if random.random() < 0.05: # С вероятностью 5% делаем случайный ход
        return random.choice(possible_moves)

    probs = [chain[last_move].get(move, 0.1) for move in possible_moves]
    for i, move in enumerate(possible_moves):
        temp_board = board.copy()
        temp_board[move] = 'O'
        if check_winner(temp_board, 'O'):
            probs[i] *= 5

    total = sum(probs)
    if total > 0:
        probs = [p/total for p in probs]
    else:
        probs = [1/len(possible_moves)] * len(possible_moves)

    return np.random.choice(possible_moves, p=probs)

# Визуализация
def visualize_markov_chain_tkinter(canvas, chain):
    cell_size = 30
    canvas.delete("all")
    all_values = [v for row in chain.values() for v in row.values()]
    if not all_values: # Проверка на пустой список
      return

    max_val = max(all_values) if all_values else 1
    min_val = min(all_values) if all_values else 0
    for i in range(9):
        for j in range(9):
            val = chain[i].get(j, 0)
            if max_val != min_val:
                normalized = (val - min_val) / (max_val - min_val)
            else:
                normalized = 0.5
            red = int(255 * normalized)
            green = int(255 * (1 - normalized))
            blue = 50
            color = f'#{red:02x}{green:02x}{blue:02x}'
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')
            canvas.create_text((x1+x2)/2, (y1+y2)/2,
                             text=f"{val:.2f}",
                             font=("Arial", 7))

def update_heatmap():
    if heatmap_canvas and markov_chain:
        visualize_markov_chain_tkinter(heatmap_canvas, markov_chain)


# Игровая логика
def play_move(position):
    global board, current_player, last_computer_move, game_history
    if board[position] == ' ':
        board[position] = current_player
        buttons[position].config(text=current_player)

        if check_winner(board, current_player):
            messagebox.showinfo("Игра окончена", f"{current_player} победил!")
            reset_board()
            return
        if is_board_full(board):
            messagebox.showinfo("Игра окончена", "Ничья!")
            reset_board()
            return

        if current_player == 'X':
            current_player = 'O'
            computer_move()
        else:
            current_player = 'X'
            update_heatmap()

def computer_move():
    global board, current_player, last_computer_move, game_history
    move = get_computer_move(board, markov_chain, last_computer_move)
    if move is not None:
        board[move] = current_player
        buttons[move].config(text=current_player)

        if last_computer_move is not None:
            game_history.append((last_computer_move, move))
        last_computer_move = move

        if check_winner(board, current_player):
            messagebox.showinfo("Игра окончена", f"{current_player} победил!")
            reset_board()
            return
        if is_board_full(board):
            messagebox.showinfo("Игра окончена", "Ничья!")
            reset_board()
            return

        current_player = 'X'
        update_heatmap()

def train_markov_chain(num_games=1000): # Увеличили количество игр
    global board, current_player, last_computer_move, game_history

    for _ in range(num_games):
        board = [' '] * 9
        current_player = 'X'
        last_computer_move = None
        game_history = []

        while True:
            move = get_computer_move(board, markov_chain, last_computer_move)
            if move is None:
                break

            board[move] = current_player
            if last_computer_move is not None:
                game_history.append((last_computer_move, move))
            last_computer_move = move

            if check_winner(board, current_player):
                reward = 10 if current_player == 'X' else -10
                break
            if is_board_full(board):
                reward = 0
                break

            current_player = 'O' if current_player == 'X' else 'X'

        for prev_move, next_move in game_history:
            update_markov_chain(prev_move, next_move, reward)

    update_heatmap()
    save_markov_chain()  # Сохраняем цепь Маркова после обучения

def computer_vs_computer():
    global board, current_player, last_computer_move, game_history
    train_markov_chain(100)
    reset_board()

    while True:
        if current_player == 'X':
            move = get_computer_move(board, markov_chain, last_computer_move)
            if move is None:
                messagebox.showinfo("Игра окончена", "Ничья!")
                reset_board()
                return

            board[move] = current_player
            if buttons:
                buttons[move].config(text=current_player)
            if last_computer_move is not None:
                game_history.append((last_computer_move, move))
            last_computer_move = move

        else:
            move = get_computer_move(board, markov_chain, last_computer_move)
            if move is None:
                messagebox.showinfo("Игра окончена", "Ничья!")
                reset_board()
                return

            board[move] = current_player
            if buttons:
                buttons[move].config(text=current_player)

            if last_computer_move is not None:
                game_history.append((last_computer_move, move))

            last_computer_move = move

        if check_winner(board, current_player):
            messagebox.showinfo("Игра окончена", f"{current_player} победил!")
            reset_board()
            return
        if is_board_full(board):
            messagebox.showinfo("Игра окончена", "Ничья!")
            reset_board()
            return

        current_player = 'O' if current_player == 'X' else 'X'
        root.update()
        root.after(200)

def save_markov_chain(filename="markov_chain.json"):
    with open(filename, 'w') as f:
        json.dump(markov_chain, f)
    print("Цепь Маркова сохранена в файл.")

# GUI
root = tk.Tk()
root.title("Крестики-нолики с цепью Маркова")

game_frame = tk.Frame(root)
game_frame.pack(side=tk.LEFT, padx=10, pady=10)

for i in range(9):
    button = tk.Button(game_frame, text=" ", font=("Arial", 24), width=3, height=1,
                      command=lambda pos=i: play_move(pos))
    button.grid(row=i//3, column=i%3)
    buttons.append(button)

control_frame = tk.Frame(root)
control_frame.pack(side=tk.RIGHT, padx=10, pady=10)

heatmap_canvas = tk.Canvas(control_frame, width=270, height=270, bg='white')
heatmap_canvas.pack()

# Загружаем цепь маркова после инициализации heatmap_canvas
load_markov_chain()
tk.Button(control_frame, text="Обучить (1000 игр)", command=lambda: train_markov_chain(1000)).pack(fill=tk.X)
tk.Button(control_frame, text="Сброс", command=reset_board).pack(fill=tk.X)
tk.Button(control_frame, text="Комп vs Комп", command=computer_vs_computer).pack(fill=tk.X)
tk.Button(control_frame, text="Сохранить", command=lambda: save_markov_chain()).pack(fill=tk.X)

reset_board()
root.mainloop()