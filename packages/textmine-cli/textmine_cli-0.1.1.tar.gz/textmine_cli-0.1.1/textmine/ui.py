from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from datetime import datetime
from typing import Dict, Any, List

PHOSPHOR_GREEN = "#80FFAA"
DARK_BG = "#0a0a0a"

retro_theme = Theme({
    "info": f"{PHOSPHOR_GREEN}",
    "warning": "yellow",
    "error": "red",
    "success": f"{PHOSPHOR_GREEN} bold",
    "prompt": f"{PHOSPHOR_GREEN} bold",
    "muted": "dim",
})

console = Console(theme=retro_theme)


def print_banner():
    """Display ASCII art banner."""
    banner = """
 _____ _______  _______ __  __ _____ _   _ ______ 
|_   _|__   __||__   __|  \\/  |_   _| \\ | |  ____|
  | |    | |      | |  | \\  / | | | |  \\| | |__   
  | |    | |      | |  | |\\/| | | | | . ` |  __|  
 _| |_   | |      | |  | |  | |_| |_| |\\  | |____ 
|_____|  |_|      |_|  |_|  |_|_____|_| \\_|______|
                                                   
    """
    console.print(banner, style=f"{PHOSPHOR_GREEN} bold")
    console.print("═" * 52, style=PHOSPHOR_GREEN)
    console.print()


def print_info(message: str):
    """Print info message."""
    console.print(f"[info]> {message}[/info]")


def print_success(message: str):
    """Print success message."""
    console.print(f"[success]✓ {message}[/success]")


def print_error(message: str):
    """Print error message."""
    console.print(f"[error]✗ {message}[/error]")


def print_prompt(prompt: str) -> str:
    """Display prompt and get input."""
    return console.input(f"[prompt]{prompt}[/prompt] ")


def print_password(prompt: str) -> str:
    """Display password prompt and get hidden input."""
    from getpass import getpass
    console.print(f"[prompt]{prompt}[/prompt] ", end="")
    return getpass("")


def print_user_table(users: List[Dict[str, Any]]):
    """Display users in a table."""
    if not users:
        print_info("No users found")
        return
    
    table = Table(box=box.SIMPLE, border_style=PHOSPHOR_GREEN)
    table.add_column("USERNAME", style="bold")
    table.add_column("BIO", style="dim")
    table.add_column("JOINED", style="dim")
    
    for user in users:
        joined = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
        table.add_row(
            user["username"],
            user.get("bio") or "",
            joined.strftime("%Y-%m-%d")
        )
    
    console.print(table)


def print_profile(profile: Dict[str, Any]):
    """Display user profile."""
    user = profile["user"]
    stats = profile["stats"]
    
    joined = datetime.fromisoformat(user["createdAt"].replace("Z", "+00:00"))
    
    profile_text = f"""
[bold]{user['username']}[/bold]

{user.get('bio') or '(no bio set)'}

STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Messages Sent:     {stats['messagesSent']}
Messages Received: {stats['messagesReceived']}
Joined:            {joined.strftime('%B %d, %Y')}
"""
    
    panel = Panel(
        profile_text.strip(),
        border_style=PHOSPHOR_GREEN,
        box=box.HEAVY,
        padding=(1, 2)
    )
    console.print(panel)


def print_message(msg: Dict[str, Any], current_user_id: int):
    """Display a single message."""
    timestamp = datetime.fromisoformat(msg["createdAt"].replace("Z", "+00:00"))
    time_str = timestamp.strftime("%H:%M")
    
    is_own = msg["fromUserId"] == current_user_id
    prefix = "YOU" if is_own else "THEM"
    style = "bold" if is_own else "dim"
    
    console.print(f"[{style}][{time_str}] {prefix}:[/{style}] {msg['content']}")


def print_chat_header(username: str):
    """Display chat header."""
    header = f" CHAT WITH {username.upper()} "
    console.print()
    console.print("═" * 52, style=PHOSPHOR_GREEN)
    console.print(header.center(52), style=f"{PHOSPHOR_GREEN} bold")
    console.print("═" * 52, style=PHOSPHOR_GREEN)
    console.print()
    console.print("[dim]Type /help for commands, /exit to quit[/dim]")
    console.print()


def clear_screen():
    """Clear terminal screen."""
    console.clear()
