import re
import os
import random

README_PATH = "README.md"

def load_readme():
    with open(README_PATH, "r", encoding="utf-8") as f:
        return f.read()

def save_readme(content):
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def parse_board(readme):
    # Search for board pattern in README
    # Format: <!-- TTT_BOARD_START --> ... <!-- TTT_BOARD_END -->
    match = re.search(r"<!-- TTT_BOARD_START -->(.*?)<!-- TTT_BOARD_END -->", readme, re.DOTALL)
    if not match:
        return [" "] * 9
    
    content = match.group(1)
    cells = []
    # Find ❌, ⭕, or 🟩 (empty cell)
    matches = re.findall(r"(❌|⭕|🟩)", content)
    for m in matches:
        if m == "❌":
            cells.append("X")
        elif m == "⭕":
            cells.append("O")
        else:
            cells.append(" ")
    
    if len(cells) != 9:
        return [" "] * 9
    return cells

def check_winner(board):
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # cols
        [0, 4, 8], [2, 4, 6]             # diags
    ]
    for w in wins:
        if board[w[0]] != " " and board[w[0]] == board[w[1]] == board[w[2]]:
            return board[w[0]]
    if " " not in board:
        return "DRAW"
    return None

def bot_move(board):
    empty = [i for i, cell in enumerate(board) if cell == " "]
    if not empty:
        return board
    # Pick winning move or block or random
    for idx in empty:
        temp = list(board)
        temp[idx] = "O"
        if check_winner(temp) == "O":
            board[idx] = "O"
            return board
    for idx in empty:
        temp = list(board)
        temp[idx] = "X"
        if check_winner(temp) == "X":
            board[idx] = "O"
            return board
    
    board[random.choice(empty)] = "O"
    return board

def generate_board_markdown(board):
    winner = check_winner(board)
    reset_link = "https://github.com/Tnembull/Tnembull/issues/new?title=TTT:+reset&body=Click+Submit+New+Issue+to+Reset+Game!"
    
    status_msg = "Your turn! Click an available 🟩 cell to make your move:"
    if winner == "X":
        status_msg = "🎉 **You Won against Linux Bot!** Click Reset to play again."
    elif winner == "O":
        status_msg = "🤖 **Linux Bot Won!** Click Reset to try again."
    elif winner == "DRAW":
        status_msg = "🤝 **It's a Draw!** Click Reset to play again."

    rows = []
    for r in range(3):
        cols = []
        for c in range(3):
            idx = r * 3 + c
            val = board[idx]
            if val == "X":
                cols.append("❌")
            elif val == "O":
                cols.append("⭕")
            else:
                if winner is not None:
                    cols.append("🟩")
                else:
                    move_link = f"https://github.com/Tnembull/Tnembull/issues/new?title=TTT:+move+{r}+{c}&body=Click+Submit+New+Issue+to+confirm+this+move!"
                    cols.append(f"[🟩]({move_link})")
        rows.append("| " + " | ".join(cols) + " |")

    table_md = f"""<!-- TTT_BOARD_START -->
<div align="center">

{status_msg}

| | | |
| :-: | :-: | :-: |
{rows[0]}
{rows[1]}
{rows[2]}

<br/>
[🔄 **Reset Game**]({reset_link})

</div>
<!-- TTT_BOARD_END -->"""
    return table_md

def main():
    issue_title = os.getenv("ISSUE_TITLE", "")
    readme = load_readme()
    board = parse_board(readme)

    if "TTT: reset" in issue_title:
        board = [" "] * 9
    elif "TTT: move" in issue_title:
        match = re.search(r"TTT:\s*move\s*(\d)\s*(\d)", issue_title)
        if match:
            r, c = int(match.group(1)), int(match.group(2))
            idx = r * 3 + c
            if 0 <= idx < 9 and board[idx] == " ":
                board[idx] = "X"
                if check_winner(board) is None:
                    board = bot_move(board)

    new_board_md = generate_board_markdown(board)
    new_readme = re.sub(
        r"<!-- TTT_BOARD_START -->.*?<!-- TTT_BOARD_END -->",
        new_board_md,
        readme,
        flags=re.DOTALL
    )
    save_readme(new_readme)

if __name__ == "__main__":
    main()
