#!/usr/bin/env python3
import sys
import os
import stat
import subprocess
import shlex
import readline
import glob
import atexit
import pty
import termios
import tty
import select
import signal
import fcntl
import struct
import re
import socket
from pathlib import Path
from datetime import datetime
from collections import deque
import json


PATH = os.environ.get("PATH", os.defpath)
HOME = os.environ.get("HOME", os.path.expanduser("~"))

histfile_env = os.environ.get("HISTFILE", "")
HISTORY_FILE = (
    histfile_env if histfile_env else os.path.join(HOME, ".phoenixnebula_history")
)
RCFILE = os.path.join(HOME, ".phoenixnebularc")

# Theme colors - ANSI escape codes
THEME_DIR = os.path.join(HOME, ".phoenixnebula", "themes")
CONFIG_FILE = os.path.join(HOME, ".phoenixnebula", "config.json")

last_appended_position = 0
foreground_pgid = None
shell_pgid = os.getpgrp()
shell_pid = os.getpid()

ALLOWED_COMMANDS_DIRS = ["/usr/bin", "/bin", "/usr/local/bin"]

BUILTIN_THEMES = {
    "dracula": {
        "name": "Dracula",
        "background": "#282a36",
        "foreground": "#f8f8f2",
        "cursor_color": "#f8f8f2",
        "black": "#000000",
        "red": "#ff5555",
        "green": "#50fa7b",
        "yellow": "#f1fa8c",
        "blue": "#bd93f9",
        "purple": "#ff79c6",
        "cyan": "#8be9fd",
        "white": "#bfbfbf",
        "bright_black": "#4d4d4d",
        "bright_red": "#ff6e67",
        "bright_green": "#5af78e",
        "bright_yellow": "#f4f99d",
        "bright_blue": "#caa9fa",
        "bright_purple": "#ff92df",
        "bright_cyan": "#9aedfe",
        "bright_white": "#e6e6e6",
        "prompt_user": "#50fa7b",
        "prompt_host": "#8be9fd",
        "prompt_path": "#f1fa8c",
        "prompt_symbol": "#ff79c6",
    },
    "solarized_dark": {
        "name": "Solarized Dark",
        "background": "#002b36",
        "foreground": "#839496",
        "cursor_color": "#93a1a1",
        "black": "#073642",
        "red": "#dc322f",
        "green": "#859900",
        "yellow": "#b58900",
        "blue": "#268bd2",
        "purple": "#d33682",
        "cyan": "#2aa198",
        "white": "#eee8d5",
        "bright_black": "#002b36",
        "bright_red": "#cb4b16",
        "bright_green": "#586e75",
        "bright_yellow": "#657b83",
        "bright_blue": "#839496",
        "bright_purple": "#6c71c4",
        "bright_cyan": "#93a1a1",
        "bright_white": "#fdf6e3",
        "prompt_user": "#859900",
        "prompt_host": "#268bd2",
        "prompt_path": "#b58900",
        "prompt_symbol": "#dc322f",
    },
    "nord": {
        "name": "Nord",
        "background": "#2e3440",
        "foreground": "#d8dee9",
        "cursor_color": "#eceff4",
        "black": "#3b4252",
        "red": "#bf616a",
        "green": "#a3be8c",
        "yellow": "#ebcb8b",
        "blue": "#81a1c1",
        "purple": "#b48ead",
        "cyan": "#88c0d0",
        "white": "#e5e9f0",
        "bright_black": "#4c566a",
        "bright_red": "#bf616a",
        "bright_green": "#a3be8c",
        "bright_yellow": "#ebcb8b",
        "bright_blue": "#81a1c1",
        "bright_purple": "#b48ead",
        "bright_cyan": "#8fbcbb",
        "bright_white": "#eceff4",
        "prompt_user": "#a3be8c",
        "prompt_host": "#88c0d0",
        "prompt_path": "#ebcb8b",
        "prompt_symbol": "#bf616a",
    },
    "monokai": {
        "name": "Monokai",
        "background": "#272822",
        "foreground": "#f8f8f2",
        "cursor_color": "#f8f8f0",
        "black": "#272822",
        "red": "#f92672",
        "green": "#a6e22e",
        "yellow": "#f4bf75",
        "blue": "#66d9ef",
        "purple": "#ae81ff",
        "cyan": "#a1efe4",
        "white": "#f8f8f2",
        "bright_black": "#75715e",
        "bright_red": "#f92672",
        "bright_green": "#a6e22e",
        "bright_yellow": "#f4bf75",
        "bright_blue": "#66d9ef",
        "bright_purple": "#ae81ff",
        "bright_cyan": "#a1efe4",
        "bright_white": "#f9f8f5",
        "prompt_user": "#a6e22e",
        "prompt_host": "#66d9ef",
        "prompt_path": "#f4bf75",
        "prompt_symbol": "#f92672",
    },
    "gruvbox": {
        "name": "Gruvbox Dark",
        "background": "#282828",
        "foreground": "#ebdbb2",
        "cursor_color": "#ebdbb2",
        "black": "#282828",
        "red": "#cc241d",
        "green": "#98971a",
        "yellow": "#d79921",
        "blue": "#458588",
        "purple": "#b16286",
        "cyan": "#689d6a",
        "white": "#a89984",
        "bright_black": "#928374",
        "bright_red": "#fb4934",
        "bright_green": "#b8bb26",
        "bright_yellow": "#fabd2f",
        "bright_blue": "#83a598",
        "bright_purple": "#d3869b",
        "bright_cyan": "#8ec07c",
        "bright_white": "#ebdbb2",
        "prompt_user": "#b8bb26",
        "prompt_host": "#83a598",
        "prompt_path": "#fabd2f",
        "prompt_symbol": "#fb4934",
    },
}

current_theme = "dracula"
theme_colors = {}


def hex_to_ansi(hex_color: str):
    """Convert hex color to ANSI escape code."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


def get_theme(theme_name):
    """Get theme by name, checking custom then builtin."""
    if os.path.exists(THEME_DIR):
        custom_file = os.path.join(THEME_DIR, f"{theme_name}.json")
        if os.path.exists(custom_file):
            try:
                with open(custom_file, "r") as f:
                    return json.load(f)
            except:
                pass
    return BUILTIN_THEMES.get(theme_name, BUILTIN_THEMES["dracula"])


def list_themes():
    """List all available themes."""
    themes = list(BUILTIN_THEMES.keys())
    if os.path.exists(THEME_DIR):
        try:
            for file in os.listdir(THEME_DIR):
                if file.endswith(".json"):
                    themes.append(file[:-5])
        except:
            pass

    return sorted(set(themes))


def apply_theme(theme_name):
    """Apply a theme."""
    global current_theme, theme_colors
    theme = get_theme(theme_name)
    if theme:
        current_theme = theme_name
        theme_colors = theme

        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        config = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
            except:
                pass

        config["theme"] = theme_name
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

        set_terminal_colors(theme)

        return f"Theme applied: {theme.get('name', theme_name)}"
    return "Theme not found"


def set_terminal_colors(theme):
    """Set terminal background and foreground colors."""
    bg = theme.get("background", "#282a36")
    fg = theme.get("foreground", "#f8f8f2")
    print(f"\033]11;{bg}\007", end="", flush=True)
    print(f"\033]10;{fg}\007", end="", flush=True)
    cursor = theme.get("cursor_color", fg)
    print(f"\033]12;{cursor}\007", end="", flush=True)


def save_custom_theme(theme_name, theme_data):
    """Save a custom theme."""
    os.makedirs(THEME_DIR, exist_ok=True)
    theme_file = os.path.join(THEME_DIR, f"{theme_name}.json")

    try:
        with open(theme_file, "w") as f:
            json.dump(theme_data, f, indent=2)
        return f"Theme '{theme_name}' saved successfully"
    except Exception as e:
        return f"Error saving theme: {e}"


def load_config():
    """Load shell configuration."""
    global current_theme, theme_colors

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                theme_name = config.get("theme", "dracula")
                theme_colors = get_theme(theme_name)
                current_theme = theme_name
                set_terminal_colors(theme_colors)
        except:
            theme_colors = BUILTIN_THEMES["dracula"]
            current_theme = "dracula"
    else:
        theme_colors = BUILTIN_THEMES["dracula"]
        current_theme = "dracula"


# Shell variables
shell_vars = {
    "PS1": "\\u@\\h \\w\\$ ",
    "PS2": "> ",
    "HISTSIZE": "1000",
}

# Aliases storage
aliases = {}

# Functions storage
functions = {}

# Last command exit status
last_exit_code = 0

# Background jobs management
background_jobs = {}
next_job_id = 1

# Save original terminal settings
try:
    orig_termios = termios.tcgetattr(sys.stdin)
except:
    orig_termios = None


def restore_terminal():
    """Restore terminal to original state."""
    if orig_termios:
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_termios)
        except:
            pass
    print("\033]110\007", end="", flush=True)
    print("\033]111\007", end="", flush=True)


def load_rc_file():
    """Load shell configuration file."""
    if os.path.exists(RCFILE):
        try:
            with open(RCFILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.startswith("alias "):
                            parts = line[6:].split("=", 1)
                            if len(parts) == 2:
                                aliases[parts[0].strip()] = (
                                    parts[1].strip().strip("'\"")
                                )
        except Exception as e:
            print(f"Error loading {RCFILE}: {e}")


load_config()

if HISTORY_FILE:
    try:
        readline.read_history_file(HISTORY_FILE)
    except (FileNotFoundError, OSError):
        pass

load_rc_file()

atexit.register(readline.write_history_file, HISTORY_FILE)
atexit.register(restore_terminal)


def handle_signal(sig, frame):
    """Forward signals to foreground process group or pid."""
    global foreground_pgid
    if foreground_pgid is None:
        return
    try:
        os.killpg(foreground_pgid, sig)
    except ProcessLookupError:
        try:
            os.kill(foreground_pgid, sig)
        except Exception:
            pass
    except Exception:
        pass


def handle_sigchld(sig, frame):
    """Reap zombie processes and update background job statuses.
    Also update last_exit_code when a foreground process group exits.
    """
    global background_jobs, foreground_pgid, last_exit_code
    try:
        while True:
            # wait for any child without blocking
            pid, status = os.waitpid(-1, os.WNOHANG | os.WUNTRACED | os.WCONTINUED)
            if pid == 0:
                break

            # Update background job if we know it
            handled = False
            for job_id, job in list(background_jobs.items()):
                if job.get("pid") == pid:
                    handled = True
                    if os.WIFEXITED(status):
                        job["status"] = "done"
                        job["returncode"] = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        job["status"] = "terminated"
                        job["returncode"] = os.WTERMSIG(status)
                    elif os.WIFSTOPPED(status):
                        job["status"] = "stopped"
                        job["returncode"] = os.WSTOPSIG(status)
                    elif os.WIFCONTINUED(status):
                        job["status"] = "running"
                        job["returncode"] = None
                    break

            # If not a background job, it may belong to the foreground process group.
            if not handled and foreground_pgid is not None:
                try:
                    proc_pgid = os.getpgid(pid)
                except OSError:
                    proc_pgid = None

                if proc_pgid == foreground_pgid:
                    # Foreground job changed state or exited
                    if os.WIFEXITED(status):
                        last_exit_code = os.WEXITSTATUS(status)
                    elif os.WIFSIGNALED(status):
                        last_exit_code = 128 + os.WTERMSIG(status)
                    # clear foreground pgid so shell resumes control
                    foreground_pgid = None

    except ChildProcessError:
        # no more children
        pass
    except OSError:
        # ignore transient OS errors in the handler
        pass


def handle_sigwinch(sig, frame):
    """Handle terminal resize."""
    global foreground_pgid
    if foreground_pgid is not None and foreground_pgid > 0:
        try:
            os.killpg(foreground_pgid, signal.SIGWINCH)
        except (ProcessLookupError, OSError):
            pass


if orig_termios:
    atexit.register(termios.tcsetattr, sys.stdin, termios.TCSADRAIN, orig_termios)

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTSTP, handle_signal)
signal.signal(signal.SIGQUIT, handle_signal)
signal.signal(signal.SIGCHLD, handle_sigchld)
signal.signal(signal.SIGWINCH, handle_sigwinch)
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def format_prompt(prompt_str):
    """Format shell prompt with special characters and colors."""
    user = os.environ.get("USER", "user")
    try:
        hostname = socket.gethostname()
    except:
        hostname = os.environ.get("HOSTNAME", "host")
    cwd = os.getcwd()
    home = os.path.expanduser("~")

    if cwd.startswith(home):
        cwd = "~" + cwd[len(home) :]

    reset = "\033[0m"
    user_color = hex_to_ansi(theme_colors.get("prompt_user", "#50fa7b"))
    host_color = hex_to_ansi(theme_colors.get("prompt_host", "#8be9fd"))
    path_color = hex_to_ansi(theme_colors.get("prompt_path", "#f1fa8c"))
    symbol_color = hex_to_ansi(theme_colors.get("prompt_symbol", "#ff79c6"))

    prompt_str = prompt_str.replace("\\u", f"{user_color}{user}{reset}")
    prompt_str = prompt_str.replace("\\h", f"{host_color}{hostname}{reset}")
    prompt_str = prompt_str.replace("\\w", f"{path_color}{cwd}{reset}")
    prompt_str = prompt_str.replace(
        "\\$", f"{symbol_color}{'#' if os.getuid() == 0 else '$'}{reset}"
    )
    prompt_str = prompt_str.replace("\\\\", "\\")

    return prompt_str


def run_with_pty(argv, background=False):
    """Execute command with PTY for proper interactive I/O and signal handling."""
    global foreground_pgid, last_exit_code, next_job_id, background_jobs

    try:
        pid, fd = pty.fork()
    except Exception:
        return run_subprocess(argv, background)

    if pid == 0:
        os.setsid()
        os.setpgid(0, 0)
        try:
            os.tcsetpgrp(sys.stdin.fileno(), os.getpgrp())
            os.execvp(argv[0], argv)
        except FileNotFoundError:
            print(f"{argv[0]}: command not found", file=sys.stderr)
            sys.exit(127)
        except Exception as e:
            print(f"Error executing {argv[0]}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if background:
            job_id = next_job_id
            next_job_id += 1
            background_jobs[job_id] = {
                "pid": pid,
                "cmd": " ".join(argv),
                "status": "running",
                "returncode": None,
            }
            print(f"[{job_id}] {pid}")
            last_exit_code = 0
        else:
            foreground_pgid = pid
            old_settings = None

            try:
                try:
                    os.tcsetpgrp(sys.stdin.fileno(), foreground_pgid)
                except (OSError, AttributeError):
                    pass
                try:
                    old_settings = termios.tcgetattr(sys.stdin)
                    tty.setraw(sys.stdin.fileno())
                except:
                    pass
                while True:
                    try:
                        rlist, _, _ = select.select([fd, sys.stdin], [], [])
                    except (select.error, OSError):
                        break

                    if fd in rlist:
                        try:
                            data = os.read(fd, 4096)
                            if not data:
                                break
                            os.write(sys.stdout.fileno(), data)
                        except OSError:
                            break

                    if sys.stdin in rlist:
                        try:
                            data = os.read(sys.stdin.fileno(), 4096)
                            if not data:
                                break
                            os.write(fd, data)
                        except OSError:
                            break

            finally:
                if old_settings:
                    try:
                        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    except:
                        pass

                try:
                    os.tcsetpgrp(sys.stdin.fileno(), shell_pgid)
                except (OSError, AttributeError):
                    pass

                foreground_pgid = None

                try:
                    _, status = os.waitpid(pid, 0)
                    last_exit_code = os.WEXITSTATUS(status)
                except ChildProcessError:
                    pass


def run_subprocess(argv, background=False):
    """Execute command using subprocess with proper process groups and terminal control."""
    global last_exit_code, next_job_id, background_jobs, foreground_pgid, shell_pgid
    try:
        if background:
            proc = subprocess.Popen(
                argv,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid,
            )
            job_id = next_job_id
            next_job_id += 1
            background_jobs[job_id] = {
                "pid": proc.pid,
                "cmd": " ".join(argv),
                "status": "running",
                "returncode": None,
            }
            print(f"[{job_id}] {proc.pid}")
            last_exit_code = 0
        else:
            proc = subprocess.Popen(argv, preexec_fn=os.setsid)
            fg_pgid = proc.pid
            foreground_pgid = fg_pgid
            try:
                os.tcsetpgrp(sys.stdin.fileno(), fg_pgid)
            except Exception:
                pass
            try:
                _, status = os.waitpid(proc.pid, 0)
                if os.WIFEXITED(status):
                    last_exit_code = os.WEXITSTATUS(status)
                elif os.WIFSIGNALED(status):
                    last_exit_code = 128 + os.WTERMSIG(status)
                else:
                    last_exit_code = 1
            except KeyboardInterrupt:
                pass
            except Exception:
                pass
            finally:
                try:
                    os.tcsetpgrp(sys.stdin.fileno(), shell_pgid)
                except Exception:
                    pass
                foreground_pgid = None

    except KeyboardInterrupt:
        last_exit_code = 130
    except FileNotFoundError:
        print(f"{argv[0]}: command not found")
        last_exit_code = 127
    except Exception as e:
        print(f"Error: {e}")
        last_exit_code = 1


# List of programs that should use PTY (interactive programs)
INTERACTIVE_PROGRAMS = {
    "vim",
    "vi",
    "nano",
    "emacs",
    "less",
    "more",
    "man",
    "htop",
    "top",
    "clear",
    "ncurses",
    "screen",
    "tmux",
    "git",
    "ssh",
    "telnet",
    "ftp",
    "bash",
    "sh",
    "zsh",
    "ksh",
    "python",
    "python3",
    "node",
    "ruby",
    "perl",
    "lua",
    "irb",
    "pry",
    "ipython",
    "ghci",
}


def should_use_pty(cmd):
    """Determine if command should use PTY."""
    cmd_base = os.path.basename(cmd)
    return cmd_base in INTERACTIVE_PROGRAMS or cmd_base.endswith("shell")


def get_history() -> str:
    """Return the current readline history as a single string."""
    length = readline.get_current_history_length()
    items = []
    for i in range(1, length + 1):
        item = readline.get_history_item(i)
        if item:
            items.append(item)
    return "\n".join(items) + "\n" if items else ""


def write_history_to_file(file_path: str):
    """Write the current readline history to the specified file."""
    try:
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "w") as f:
            f.write(get_history())
    except Exception as e:
        print(f"history: error writing {file_path}: {e}")


def append_history_to_file(file_path: str):
    """Append only new commands to the file."""
    global last_appended_position

    try:
        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        current_length = readline.get_current_history_length()

        with open(file_path, "a") as f:
            for i in range(last_appended_position + 1, current_length + 1):
                item = readline.get_history_item(i)
                if item:
                    f.write(item + "\n")

        last_appended_position = current_length
    except Exception as e:
        print(f"history: error appending to {file_path}: {e}")


def load_history_from_file(file_path: str):
    """Append commands from a file to readline history."""
    global last_appended_position

    if not os.path.exists(file_path):
        print(f"history: {file_path}: No such file or directory")
        return

    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.rstrip("\n\r")
                if line:
                    readline.add_history(line)
        last_appended_position = readline.get_current_history_length()
    except Exception as e:
        print(f"history: error reading {file_path}: {e}")


def show_history(n: int | None = None):
    """Display command history."""
    length = readline.get_current_history_length()
    start = 1
    if n is not None:
        start = max(1, length - n + 1)

    for i in range(start, length + 1):
        item = readline.get_history_item(i)
        if item:
            print(f"    {i}  {item}")


def is_executable(file_path):
    """Check if file is executable."""
    try:
        st = os.stat(file_path)
        return stat.S_ISREG(st.st_mode) and (
            st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        )
    except FileNotFoundError:
        return False


def find_executable(cmd):
    """Find executable in PATH."""
    for path_dir in PATH.split(os.pathsep):
        if not path_dir:
            continue
        full_path = os.path.join(path_dir, cmd)
        if is_executable(full_path):
            return full_path
    return None


def is_builtin(cmd):
    """Check if command is a shell builtin."""
    return cmd in [
        "echo",
        "exit",
        "type",
        "pwd",
        "cd",
        "history",
        "alias",
        "unalias",
        "export",
        "unset",
        "set",
        "source",
        ".",
        "true",
        "false",
        "jobs",
        "bg",
        "fg",
        "theme",
        "clear",
    ]


def run_builtin(cmd_tokens, stdin_data=None):
    """Run a builtin command and return its output."""
    global last_exit_code

    if not cmd_tokens:
        return ""

    cmd = cmd_tokens[0]
    args = cmd_tokens[1:]
    output = ""

    if cmd == "echo":
        output = " ".join(args) + "\n"
    elif cmd == "type":
        if args:
            name = args[0]
            if is_builtin(name):
                output = f"{name} is a shell builtin\n"
            else:
                executable_path = find_executable(name)
                if executable_path:
                    output = f"{name} is {executable_path}\n"
                else:
                    output = f"{name}: not found\n"
    elif cmd == "pwd":
        output = os.getcwd() + "\n"
    elif cmd == "cd":
        if not args:
            new_path = HOME
        else:
            new_path = args[0]
            if new_path == "~":
                new_path = HOME
            elif new_path == "-":
                new_path = HOME
            elif not os.path.isabs(new_path):
                new_path = os.path.normpath(os.path.join(os.getcwd(), new_path))

        if os.path.isdir(new_path):
            os.chdir(new_path)
            last_exit_code = 0
        else:
            output = f"cd: {new_path}: No such file or directory\n"
            last_exit_code = 1
    elif cmd == "exit":
        try:
            exit_code = int(args[0]) if args else last_exit_code
        except ValueError:
            exit_code = 1
        sys.exit(exit_code)
    elif cmd == "clear":
        try:
            os.system("clear")
        except:
            os.write(sys.stdout.fileno(), b"\033[2J\033[H")
    elif cmd == "true":
        last_exit_code = 0
    elif cmd == "false":
        last_exit_code = 1
    elif cmd == "theme":
        if not args:
            # List themes
            themes = list_themes()
            output = "Available themes:\n"
            for t in themes:
                marker = " (current)" if t == current_theme else ""
                output += f"  - {t}{marker}\n"
        elif args[0] == "list":
            themes = list_themes()
            for t in themes:
                marker = " *" if t == current_theme else ""
                output += f"{t}{marker}\n"
        elif args[0] == "set":
            if len(args) < 2:
                output = "usage: theme set <name>\n"
            else:
                result = apply_theme(args[1])
                output = result + "\n"
        elif args[0] == "current":
            output = f"{current_theme}\n"
        else:
            # Assume it's a theme name
            result = apply_theme(args[0])
            output = result + "\n"
    elif cmd == "alias":
        if not args:
            for name, value in sorted(aliases.items()):
                output += f"alias {name}='{value}'\n"
        else:
            for arg in args:
                if "=" in arg:
                    name, value = arg.split("=", 1)
                    aliases[name] = value.strip("'\"")
                elif arg in aliases:
                    output += f"alias {arg}='{aliases[arg]}'\n"
    elif cmd == "unalias":
        for arg in args:
            if arg in aliases:
                del aliases[arg]
    elif cmd == "export":
        for arg in args:
            if "=" in arg:
                var, val = arg.split("=", 1)
                os.environ[var] = val
            else:
                output += f"{arg}={os.environ.get(arg, '')}\n"
    elif cmd == "unset":
        for arg in args:
            if arg in os.environ:
                del os.environ[arg]
    elif cmd == "set":
        if not args:
            for key, val in sorted(shell_vars.items()):
                output += f"{key}={val}\n"
        else:
            for arg in args:
                if "=" in arg:
                    key, val = arg.split("=", 1)
                    shell_vars[key] = val
    elif cmd in ["source", "."]:
        if args:
            script_file = args[0]
            if os.path.exists(script_file):
                try:
                    with open(script_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                pass
                except Exception as e:
                    output = f"Error sourcing {script_file}: {e}\n"
    elif cmd == "jobs":
        if not background_jobs:
            output = ""
        else:
            for job_id, job in sorted(background_jobs.items()):
                status = job["status"]
                if status == "done":
                    status = f"Done({job['returncode']})"
                else:
                    status = "Running"
                output += f"[{job_id}]  {status}  {job['cmd']}\n"
    elif cmd == "bg":
        if args:
            try:
                job_id = int(args[0].lstrip("%"))
                if job_id in background_jobs:
                    job = background_jobs[job_id]
                    try:
                        os.killpg(job["pid"], signal.SIGCONT)  # resume the job
                        job["status"] = "running"
                        print(f"[{job_id}] {job['cmd']}")
                    except Exception as e:
                        print(f"bg: {e}")
                else:
                    output = f"bg: no such job\n"
            except (ValueError, IndexError):
                output = "usage: bg %jobid\n"

    elif cmd == "fg":
        if args:
            try:
                job_id = int(args[0].lstrip("%"))
                if job_id in background_jobs:
                    job = background_jobs[job_id]
                    pid = job["pid"]

                    # Give terminal control to job
                    try:
                        os.tcsetpgrp(sys.stdin.fileno(), pid)
                    except Exception:
                        pass

                    try:
                        os.killpg(pid, signal.SIGCONT)  # resume the job
                    except Exception:
                        pass

                    # Wait for it to finish
                    try:
                        _, status = os.waitpid(pid, 0)
                        job["status"] = "done"
                        job["returncode"] = os.WEXITSTATUS(status)
                    except Exception:
                        pass

                    # Restore terminal to shell
                    try:
                        os.tcsetpgrp(sys.stdin.fileno(), shell_pgid)
                    except Exception:
                        pass
                else:
                    output = f"fg: no such job\n"
            except (ValueError, IndexError):
                output = "usage: fg %jobid\n"

    return output


def expand_variables(text):
    """Expand shell variables."""

    def replace_var(match):
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    text = re.sub(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)", replace_var, text)
    return text


def expand_tilde(path):
    """Expand ~ in paths."""
    if path.startswith("~"):
        if path == "~":
            return HOME
        elif path.startswith("~/"):
            return HOME + path[1:]
    return path


def pipeline_run(cmd_strings):
    """Execute a pipeline of commands."""
    cmds = []
    for cmd_str in cmd_strings:
        cmd_str = cmd_str.strip()
        cmd_str = expand_variables(cmd_str)
        cmd_str = expand_tilde(cmd_str)

        tokens = shlex.split(cmd_str)
        if tokens:
            tokens[0] = expand_alias(tokens[0])
            cmds.append(tokens)

    if not cmds:
        return

    if len(cmds) == 1:
        cmd = cmds[0][0]
        if is_builtin(cmd):
            output = run_builtin(cmds[0])
            print(output, end="")
        else:
            executable_path = find_executable(cmd) if not os.path.isabs(cmd) else cmd
            if executable_path or os.path.exists(cmd):
                try:
                    if should_use_pty(cmd):
                        run_with_pty(cmds[0])
                    else:
                        run_subprocess(cmds[0])
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"{cmd}: command not found")
        return

    has_builtin = any(is_builtin(tokens[0]) for tokens in cmds)

    if not has_builtin:
        processes = []
        for i, cmd_tokens in enumerate(cmds):
            cmd = cmd_tokens[0]
            executable_path = find_executable(cmd) if not os.path.isabs(cmd) else cmd

            if not executable_path and not os.path.exists(cmd):
                print(f"{cmd}: command not found")
                return

            if i == 0:
                proc = subprocess.Popen(cmd_tokens, stdout=subprocess.PIPE)
            elif i == len(cmds) - 1:
                proc = subprocess.Popen(cmd_tokens, stdin=processes[-1].stdout)
            else:
                proc = subprocess.Popen(
                    cmd_tokens, stdin=processes[-1].stdout, stdout=subprocess.PIPE
                )

            if i > 0:
                processes[-1].stdout.close()

            processes.append(proc)

        try:
            processes[-1].wait()
        except KeyboardInterrupt:
            for proc in processes:
                try:
                    proc.terminate()
                except:
                    pass
    else:
        stdin_data = None

        for i, cmd_tokens in enumerate(cmds):
            cmd = cmd_tokens[0]
            is_last = i == len(cmds) - 1

            if is_builtin(cmd):
                output = run_builtin(cmd_tokens, stdin_data)
                if is_last:
                    print(output, end="")
                else:
                    stdin_data = output.encode()
            else:
                executable_path = (
                    find_executable(cmd) if not os.path.isabs(cmd) else cmd
                )

                if not executable_path and not os.path.exists(cmd):
                    print(f"{cmd}: command not found")
                    return

                try:
                    if is_last:
                        if stdin_data:
                            proc = subprocess.Popen(cmd_tokens, stdin=subprocess.PIPE)
                            proc.communicate(stdin_data)
                        else:
                            subprocess.run(cmd_tokens)
                    else:
                        if stdin_data:
                            proc = subprocess.Popen(
                                cmd_tokens,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                            )
                            stdout, _ = proc.communicate(stdin_data)
                        else:
                            proc = subprocess.Popen(cmd_tokens, stdout=subprocess.PIPE)
                            stdout, _ = proc.communicate()
                        stdin_data = stdout
                except KeyboardInterrupt:
                    break


def redirect_run(cmd_part, file_part, to_stderr=False, append=False):
    """Handle output redirection."""
    cmd_part = cmd_part.strip()
    file_part = file_part.strip()
    cmd_part = expand_variables(cmd_part)
    file_part = expand_variables(expand_tilde(file_part))

    try:
        tokens = shlex.split(cmd_part)
    except ValueError as e:
        print(f"Parse error: {e}")
        return

    if not tokens:
        return

    tokens[0] = expand_alias(tokens[0])

    try:
        parent_dir = os.path.dirname(file_part)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory: {e}")
        return

    cmd = tokens[0]
    mode = "a" if append else "w"

    if cmd == "echo":
        try:
            with open(file_part, mode) as f:
                f.write(" ".join(tokens[1:]) + "\n")
        except Exception as e:
            print(f"Error writing to {file_part}: {e}")
        return

    executable_path = find_executable(cmd) if not os.path.isabs(cmd) else cmd
    if not executable_path and not os.path.exists(cmd):
        print(f"{cmd}: command not found")
        return

    try:
        with open(file_part, mode) as f:
            if to_stderr:
                subprocess.run(tokens, stderr=f)
            else:
                subprocess.run(tokens, stdout=f)
    except Exception as e:
        print(f"Error: {e}")


# TAB completion
last_completion_text = None
tab_press_count = 0
cached_matches = []


def get_matches(text):
    """Get completion matches."""
    builtins = [
        "echo",
        "exit",
        "type",
        "pwd",
        "cd",
        "history",
        "alias",
        "export",
        "theme",
        "clear",
        "jobs",
        "bg",
        "fg",
    ]
    results = []

    for b in builtins:
        if b.startswith(text):
            results.append(b + " ")

    for path_dir in PATH.split(os.pathsep):
        if not path_dir:
            continue
        try:
            for name in os.listdir(path_dir):
                if name.startswith(text):
                    results.append(name + " ")
        except (FileNotFoundError, PermissionError):
            continue

    results.extend(glob.glob(text + "*"))
    return list(dict.fromkeys(results))


def completer(text, state):
    """Readline completer function."""
    global last_completion_text, tab_press_count, cached_matches

    if text != last_completion_text:
        last_completion_text = text
        tab_press_count = 0
        cached_matches = get_matches(text)

    if state == 0:
        tab_press_count += 1

    try:
        return cached_matches[state]
    except IndexError:
        return None


def display_matches_hook(substitution, matches, longest_match_length):
    """Display completion matches."""
    global tab_press_count

    if len(matches) <= 1:
        tab_press_count = 0
        return

    if tab_press_count == 1:
        sys.stdout.write("\a")
        sys.stdout.flush()
    else:
        display_matches = [m.rstrip() for m in matches]
        print()
        print("  ".join(display_matches))
        print(
            format_prompt(shell_vars.get("PS1", "$ ")) + readline.get_line_buffer(),
            end="",
            flush=True,
        )


readline.parse_and_bind("set enable-keypad on")
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)
readline.set_completion_display_matches_hook(display_matches_hook)
readline.set_history_length(1000)


def check_background_jobs():
    """Print status of completed background jobs."""
    global background_jobs
    completed = []
    for job_id, job in list(background_jobs.items()):
        if job["status"] == "done":
            print(f"[{job_id}]  Done({job['returncode']})  {job['cmd']}")
            completed.append(job_id)

    for job_id in completed:
        del background_jobs[job_id]


def expand_alias(cmd):
    """Expand command aliases."""
    if cmd in aliases:
        return aliases[cmd]
    return cmd


def main():
    """Main shell loop."""
    global tab_press_count, last_completion_text, last_appended_position

    last_appended_position = readline.get_current_history_length()
    print(
        f"\033[1m{hex_to_ansi(theme_colors.get('green', '#50fa7b'))}Welcome to MyShell\033[0m"
    )
    print(
        f"Current theme: {hex_to_ansi(theme_colors.get('cyan', '#8be9fd'))}{current_theme}\033[0m"
    )
    print(f"Type 'theme list' to see available themes\n")

    try:
        current_dir = os.getcwd()
    except OSError:
        current_dir = HOME

    while True:
        tab_press_count = 0
        last_completion_text = None

        check_background_jobs()

        try:
            prompt = format_prompt(shell_vars.get("PS1", "$ "))
            command = input(prompt).strip()
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        if not command:
            continue

        if command.startswith("#"):
            continue

        background = command.endswith("&")
        if background:
            command = command[:-1].strip()

        if "|" in command:
            pipeline_run(command.split("|"))
            continue

        if "2>>" in command:
            parts = command.split("2>>", 1)
            redirect_run(parts[0], parts[1], to_stderr=True, append=True)
            continue
        elif "1>>" in command:
            parts = command.split("1>>", 1)
            redirect_run(parts[0], parts[1], append=True)
            continue
        elif ">>" in command:
            parts = command.split(">>", 1)
            redirect_run(parts[0], parts[1], append=True)
            continue
        elif "2>" in command:
            parts = command.split("2>", 1)
            redirect_run(parts[0], parts[1], to_stderr=True)
            continue
        elif "1>" in command:
            parts = command.split("1>", 1)
            redirect_run(parts[0], parts[1])
            continue
        elif ">" in command:
            parts = command.split(">", 1)
            redirect_run(parts[0], parts[1])
            continue

        if command.startswith("history"):
            parts = command.split(maxsplit=2)
            if len(parts) >= 2 and parts[1] == "-r":
                if len(parts) < 3:
                    print("usage: history -r <file>")
                    continue
                load_history_from_file(parts[2])
                continue
            elif len(parts) >= 2 and parts[1] == "-w":
                if len(parts) < 3:
                    print("usage: history -w <file>")
                    continue
                write_history_to_file(parts[2])
                continue
            elif len(parts) >= 2 and parts[1] == "-a":
                if len(parts) < 3:
                    print("usage: history -a <file>")
                    continue
                append_history_to_file(parts[2])
                continue
            else:
                n = None
                if len(parts) >= 2:
                    try:
                        n = int(parts[1])
                    except ValueError:
                        pass
                show_history(n)
                continue

        try:
            tokens = shlex.split(command)
        except ValueError as e:
            print(f"Parse error: {e}")
            continue

        if not tokens:
            continue

        tokens[0] = expand_alias(tokens[0])
        tokens = [expand_variables(expand_tilde(t)) for t in tokens]

        original_executable = tokens[0]

        if is_builtin(original_executable):
            output = run_builtin(tokens)
            print(output, end="")
            continue

        if not os.path.isabs(original_executable) and not os.path.exists(
            original_executable
        ):
            path_exec = find_executable(original_executable)
            if not path_exec:
                print(f"{original_executable}: command not found")
                last_exit_code = 127
                continue

        try:
            if should_use_pty(original_executable):
                run_with_pty(tokens, background=background)
            else:
                run_subprocess(tokens, background=background)
        except FileNotFoundError:
            print(f"{original_executable}: command not found")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
