import os
import requests
import json
import random
import string
import uuid
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.text import Text
from rich.table import Table
from rich.align import Align

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_userid(token):
    with console.status("[bold yellow]🔍 Retrieving user information...[/bold yellow]", spinner="dots"):
        url = f"https://graph.facebook.com/me?access_token={token}"
        res = requests.get(url)
        if res.status_code != 200:
            return None, None
        info = res.json()
        return info.get('id'), info.get('name')

def get_token(email, password):
    headers = {
        'authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
        'x-fb-friendly-name': 'Authenticate',
        'x-fb-connection-type': 'Unknown',
        'accept-encoding': 'gzip, deflate',
        'content-type': 'application/x-www-form-urlencoded',
        'x-fb-http-engine': 'Liger'
    }
    data = {
        'adid': ''.join(random.choices(string.hexdigits, k=16)),
        'format': 'json',
        'device_id': str(uuid.uuid4()),
        'email': email,
        'password': password,
        'generate_analytics_claims': '0',
        'credentials_type': 'password',
        'source': 'login',
        'error_detail_type': 'button_with_disabled',
        'enroll_misauth': 'false',
        'generate_session_cookies': '0',
        'generate_machine_id': '0',
        'fb_api_req_friendly_name': 'authenticate'
    }
    
    with console.status("[bold green]🔑 Authenticating with Facebook...[/bold green]", spinner="bouncingBall"):
        response = requests.post('https://b-graph.facebook.com/auth/login', data=data, headers=headers, timeout=10)
    
    if response.status_code != 200:
        console.print(Panel(f"[bold red]❌ Authentication failed: {response.text}[/bold red]", style='bold red'))
        return None
    
    result = response.json()
    return result.get('access_token')

def turn_shield(token, enable=True):
    uid, name = get_userid(token)
    if not uid:
        return
    
    data = {
        'variables': json.dumps({
            '0': {
                'is_shielded': enable,
                'session_id': str(uuid.uuid4()),
                'actor_id': uid,
                'client_mutation_id': str(uuid.uuid4())
            }
        }),
        'method': 'post',
        'doc_id': '1477043292367183'
    }
    headers = {
        'Authorization': f"OAuth {token}"
    }
    url = 'https://graph.facebook.com/graphql'
    
    action = "Activating" if enable else "Deactivating"
    with console.status(f"[bold yellow]🛡️ {action} Profile Guard for {name}...[/bold yellow]", spinner="clock"):
        res = requests.post(url, json=data, headers=headers)
    
    if res.status_code != 200:
        console.print(Panel(f"[bold red]❌ Request failed: {res.text}[/bold red]", style='bold red'))
        return

    response_text = res.text
    if '"is_shielded":true' in response_text and enable:
        console.print(Panel(f'[bold green]✅ SUCCESS! Profile Guard ACTIVATED for {name}[/bold green]', 
                           style='bold green', subtitle="🛡️"))
    elif '"is_shielded":false' in response_text and not enable:
        console.print(Panel(f'[bold yellow]⚠️ SUCCESS! Profile Guard DEACTIVATED for {name}[/bold yellow]', 
                           style='bold yellow', subtitle="⚠️"))
    else:
        console.print(Panel(f"[bold red]‼️ UNEXPECTED RESPONSE: {response_text}[/bold red]", style='bold red'))

def guard_on():
    email = console.input('\n[bold cyan]📧 Enter your Facebook Email: [/bold cyan]').strip()
    password = console.input('[bold cyan]🔑 Enter your Facebook Password: [/bold cyan]', password=True).strip()
    
    token = get_token(email, password)
    if not token:
        console.print(Panel('[bold red]❌ Failed to retrieve token. Please check credentials and try again.[/bold red]', 
                          style='bold red'))
        return

    uid, name = get_userid(token)
    if not uid:
        console.print(Panel('[bold red]❌ Invalid token. Authentication failed.[/bold red]', style='bold red'))
        return

    console.print(Panel(f"[bold green]👤 Logged in as: [cyan]{name}[/cyan] (ID: [yellow]{uid}[/yellow])[/bold green]", 
                      style='bold green'))
    
    # Create interactive menu
    table = Table.grid(padding=1)
    table.add_row("1", "🛡️ Activate Profile Guard", style="bold green")
    table.add_row("2", "⚠️ Deactivate Profile Guard", style="bold yellow")
    table.add_row("3", "🔙 Return to Main Menu", style="bold blue")
    
    console.print(Panel.fit(table, title="[bold magenta]🔒 SHIELD CONTROL PANEL[/bold magenta]", border_style="cyan"))
    
    choice = console.input('\n[bold magenta]🔢 Select an option (1/2/3): [/bold magenta]').strip()
    
    if choice == '1':
        turn_shield(token, True)
    elif choice == '2':
        turn_shield(token, False)
    elif choice == '3':
        return
    else:
        console.print(Panel('[bold red]‼️ Invalid choice, please try again.[/bold red]', style='bold red'))
    
    console.input('\n[bold cyan]Press Enter to continue...[/bold cyan]')

def main():
    """Main menu."""
    while True:
        clear_screen()
        console.print(Panel.fit("""
[bold magenta]╔══════════════════════════════════════╗
║ ██████╗ ██████╗ ██╗   ██╗�██████╗ ██████╗ ███╗   ██╗
║██╔═══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██╔═══██╗████╗  ██║
║██║   ██║██████╔╝ ╚████╔╝ ███████╗██║   ██║██╔██╗ ██║
║██║   ██║██╔══██╗  ╚██╔╝  ╚════██║██║   ██║██║╚██╗██║
║╚██████╔╝██║  ██║   ██║   ███████║╚██████╔╝██║ ╚████║
║ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
╚══════════════════════════════════════╝[/bold magenta]""", 
        style="bold cyan", subtitle="by Bryson"))
        
        menu = Table.grid(padding=(0,2))
        menu.add_row("1", "🛡️ Manage Profile Guard")
        menu.add_row("2", "🚪 Exit Program")
        
        console.print(Panel.fit(menu, title="[bold yellow]🔐 MAIN MENU[/bold yellow]", border_style="magenta"))
        
        choice = console.input('\n[bold yellow]🔢 Select an option (1/2): [/bold yellow]').strip()
        if choice == '1':
            guard_on()
        elif choice == '2':
            console.print(Panel('[bold green]👋 Thank you for using Bryson! Exiting...[/bold green]', style='bold green'))
            break
        else:
            console.print(Panel('[bold red]‼️ Invalid choice, please try again.[/bold red]', style='bold red'))
            time.sleep(1)

if __name__ == '__main__':
    main()
