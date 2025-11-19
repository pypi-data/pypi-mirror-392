import click
import sys
import asyncio
from typing import Optional
from . import __version__
from .api import APIClient
from .client import WebSocketClient
from . import ui
from . import config


@click.group()
@click.version_option(version=__version__)
def main():
    """textmine - Retro terminal chat client for textmine.net"""
    pass


@main.command()
def register():
    """Register a new account (requires invite code)."""
    ui.print_banner()
    ui.print_info("TEXTMINE.NET - NEW USER REGISTRATION")
    ui.print_info("Invite code required. Contact admin for access.")
    print()
    
    username = ui.print_prompt("Username:")
    password = ui.print_password("Password:")
    invite_code = ui.print_prompt("Invite Code:")
    
    try:
        api = APIClient()
        user = api.register(username, password, invite_code)
        ui.print_success(f"Account created! Welcome, {user['username']}")
        ui.print_info("You are now logged in. Use 'textmine chat <username>' to start chatting.")
    except Exception as e:
        ui.print_error(f"Registration failed: {str(e)}")
        sys.exit(1)


@main.command()
def login():
    """Login to your account."""
    ui.print_banner()
    ui.print_info("TEXTMINE.NET - USER LOGIN")
    print()
    
    username = ui.print_prompt("Username:")
    password = ui.print_password("Password:")
    
    try:
        api = APIClient()
        user = api.login(username, password)
        ui.print_success(f"Logged in as {user['username']}")
        ui.print_info("Use 'textmine chat <username>' to start chatting.")
    except Exception as e:
        ui.print_error(f"Login failed: {str(e)}")
        sys.exit(1)


@main.command()
def logout():
    """Logout and clear session."""
    try:
        api = APIClient()
        api.logout()
        ui.print_success("Logged out successfully")
    except Exception as e:
        ui.print_error(f"Logout failed: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("query")
def search(query: str):
    """Search for users by username."""
    try:
        api = APIClient()
        
        current_user = api.get_current_user()
        if not current_user:
            ui.print_error("Not logged in. Use 'textmine login' first.")
            sys.exit(1)
        
        users = api.search_users(query)
        
        ui.print_banner()
        ui.print_info(f"SEARCH RESULTS FOR: {query}")
        print()
        ui.print_user_table(users)
    except Exception as e:
        ui.print_error(f"Search failed: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("username", required=False)
def profile(username: Optional[str] = None):
    """View user profile. If no username provided, shows your profile."""
    try:
        api = APIClient()
        
        current_user = api.get_current_user()
        if not current_user:
            ui.print_error("Not logged in. Use 'textmine login' first.")
            sys.exit(1)
        
        if username:
            users = api.search_users(username)
            if not users:
                ui.print_error(f"User '{username}' not found")
                sys.exit(1)
            
            target_user = next((u for u in users if u["username"].lower() == username.lower()), None)
            if not target_user:
                ui.print_error(f"User '{username}' not found")
                sys.exit(1)
            
            user_id = target_user["id"]
        else:
            user_id = current_user["id"]
        
        profile_data = api.get_profile(user_id)
        
        ui.print_banner()
        ui.print_profile(profile_data)
    except Exception as e:
        ui.print_error(f"Failed to load profile: {str(e)}")
        sys.exit(1)


@main.command()
@click.argument("username")
def chat(username: str):
    """Open chat with a user."""
    try:
        api = APIClient()
        
        current_user = api.get_current_user()
        if not current_user:
            ui.print_error("Not logged in. Use 'textmine login' first.")
            sys.exit(1)
        
        users = api.search_users(username)
        if not users:
            ui.print_error(f"User '{username}' not found")
            sys.exit(1)
        
        target_user = next((u for u in users if u["username"].lower() == username.lower()), None)
        if not target_user:
            ui.print_error(f"User '{username}' not found")
            sys.exit(1)
        
        asyncio.run(_chat_session(api, current_user, target_user))
    except KeyboardInterrupt:
        print()
        ui.print_info("Chat ended")
    except Exception as e:
        ui.print_error(f"Chat failed: {str(e)}")
        sys.exit(1)


async def _chat_session(api: APIClient, current_user: dict, target_user: dict):
    """Run interactive chat session with WebSocket."""
    ui.clear_screen()
    ui.print_banner()
    ui.print_chat_header(target_user["username"])
    
    result = api.get_messages(target_user["id"], limit=20)
    messages = result["messages"]
    
    for msg in messages:
        ui.print_message(msg, current_user["id"])
    
    print()
    
    def on_ws_message(data: dict):
        """Handle incoming WebSocket messages."""
        if data.get("type") == "new_message":
            msg = data["message"]
            if msg["fromUserId"] == target_user["id"] or msg["toUserId"] == target_user["id"]:
                ui.print_message(msg, current_user["id"])
    
    ws_client = WebSocketClient(on_ws_message)
    
    try:
        await ws_client.connect()
        
        listen_task = asyncio.create_task(ws_client.listen())
        
        while ws_client.running:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    ui.print_prompt,
                    ">"
                )
                
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    command = user_input[1:].lower()
                    
                    if command in ["exit", "quit"]:
                        break
                    elif command == "clear":
                        ui.clear_screen()
                        ui.print_chat_header(target_user["username"])
                    elif command == "profile":
                        profile_data = api.get_profile(target_user["id"])
                        ui.print_profile(profile_data)
                    elif command == "help":
                        ui.print_info("Commands:")
                        ui.print_info("  /exit, /quit - Leave chat")
                        ui.print_info("  /clear - Clear screen")
                        ui.print_info("  /profile - View user profile")
                        ui.print_info("  /help - Show this help")
                    else:
                        ui.print_error(f"Unknown command: /{command}")
                else:
                    msg = api.send_message(target_user["id"], user_input)
                    ui.print_message(msg, current_user["id"])
            
            except EOFError:
                break
        
        listen_task.cancel()
        await ws_client.close()
    
    except Exception as e:
        ui.print_error(f"WebSocket error: {str(e)}")
        ui.print_info("Continuing in offline mode (no real-time updates)")
        
        while True:
            try:
                user_input = ui.print_prompt(">")
                
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    command = user_input[1:].lower()
                    if command in ["exit", "quit"]:
                        break
                    elif command == "clear":
                        ui.clear_screen()
                        ui.print_chat_header(target_user["username"])
                    elif command == "profile":
                        profile_data = api.get_profile(target_user["id"])
                        ui.print_profile(profile_data)
                    elif command == "help":
                        ui.print_info("Commands:")
                        ui.print_info("  /exit, /quit - Leave chat")
                        ui.print_info("  /clear - Clear screen")
                        ui.print_info("  /profile - View user profile")
                        ui.print_info("  /help - Show this help")
                    else:
                        ui.print_error(f"Unknown command: /{command}")
                else:
                    msg = api.send_message(target_user["id"], user_input)
                    ui.print_message(msg, current_user["id"])
            
            except (EOFError, KeyboardInterrupt):
                break


if __name__ == "__main__":
    main()
