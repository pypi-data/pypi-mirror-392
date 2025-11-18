# git-year

A compact terminal heatmap showing one **year** of Git commits — similar to GitHub’s contribution graph, but optimized for **small terminal windows** using **minimal vertical bars** instead of squares.

Perfect for developers who want a clean, unobtrusive activity overview directly inside the terminal.

---

## Features

- **Shows 1 year of commit activity** for the current Git repo  
- **Green intensity gradient** based on commit volume  
- **Compact vertical bars (`|`)** instead of large squares — fits even tiny terminals  
- **Zero dependencies** (pure Python + Git)  
- **256-color ANSI output** with dark-mode-friendly palette  
- **Highlights the current weekday**  
- Works in **macOS, Linux, Windows Terminal, VS Code terminal, Git Bash**  
- Graceful message if run outside a Git repo  
- Ready for PyPI (`pip install git-year`)

---

## Installation

```
bash
pip install git-year
```

---

## Usage

Sipmly run from inside a Git repository:
```
git-year
```

You’ll see a compact 7×52 bar heatmap:

```
M ||||||||||||||||||||||||||||||
T ||||||||||||||||||||||||||||||
W ||||||||||||||||||||||||||||||
T ||||||||||||||||||||||||||||||
F ||||||||||||||||||||||||||||||
S ||||||||||||||||||||||||||||||
S ||||||||||||||||||||||||||||||
```

- Rows = weekdays (Mon–Sun)
- Columns = weeks (52 total)
- Color intensity = commit count
- The current day label is highlighted in yellow

Show the installed version:
```
git-year --version
```

---

## Requirements

- Python 3.8+
- Git available in PATH
- A terminal with ANSI color support (all modern terminals)
- On legacy cmd.exe ANSI colors may fall back to monochrome

---

## Contributing

Contributions are welcome!
Ideas, issues, and pull requests are appreciated.

---

## License

MIT License
Copyright (c) 2025 Serge Velbovets

---

Enjoy your terminal-native Git activity graph without leaving the shell — **git-year** keeps your development rhythm visible, simple, and elegant.