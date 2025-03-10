#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 15 16:07:18 2025

@author: ahackett
"""

#!/usr/bin/env python3
import random
import time
from enum import Enum
from dataclasses import dataclass, field

# ANSI color codes for terminal output
RESET   = "\033[0m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
BOLD    = "\033[1m"

# Enums for guards, actions, wounds, and terrains
class Guard(Enum):
    HIGH = 0
    MIDDLE = 1
    LOW = 2
    NO = 3  # For resting or unready states

class ActionType(Enum):
    STRIKE = 0
    THRUST = 1
    DEFEND = 2
    FEINT = 3
    REST = 4

class Wound(Enum):
    NONE = 0
    ARM = 1
    LEG = 2
    HEAD = 3
    BODY = 4

class Terrain(Enum):
    OPEN = 0
    NARROW = 1
    ROUGH = 2

# Data classes for game elements
@dataclass
class Weapon:
    name: str
    damage: int          # Base damage
    speed: int           # Initiative bonus
    weight: int          # Affects stamina cost
    two_handed: bool
    type: str            # "slashing", "piercing", etc.
    ascii_art: str

@dataclass
class Armor:
    name: str
    defense: dict        # e.g., {"slashing": 8, "piercing": 6}
    weight: int          # Affects stamina/fatigue
    coverage: int        # Percentage chance to protect (0-100)

@dataclass
class Environment:
    type: Terrain
    obstacle_density: int  # 0-10, affects movement and dodging
    ascii_art: str

@dataclass
class Knight:
    name: str
    health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    fatigue: int = 0
    weapon: Weapon = None
    armor: Armor = None
    current_guard: Guard = Guard.MIDDLE
    wounds: list = field(default_factory=list)
    initiative: int = 10

@dataclass
class Action:
    type: ActionType
    target_guard: Guard
    starting_guard: Guard

# Upgraded ASCII graphics for guards with borders
def guard_ascii(g: Guard) -> str:
    if g == Guard.HIGH:
        return (CYAN + r"""
   .-=========-.
   | VOM TACH  |
   |           |
   '-=========-'
  / \
  | |
  |.|
  |.|
  |:|      __
,_|:|_,   /  )
  (Oo    / _I_
   +\ \  || __|
      \ \||___|
        \ /.:.\-\
         |.:. /-----\
         |___|::oOo::|
         /   |:<_T_>:|
        |_____\ ::: /
         | |  \ \:/
         | |   | |
         \ /   | \___
         / |   \_____\
         `-'
""" + RESET)
    elif g == Guard.MIDDLE:
        return (GREEN + r"""
   .-=========-.
   |           |
   |   PFLUG   |
   '-=========-'
 |\             //
 \\           _!_
  \\         /___\
   \\        [   ]
    \\    _ _\   /_ _
     \\/ (    '-'  ( )
     /( \/ | {&}   /\ \
       \  / \     / _> )
        "`   >:::;-'`""'-.
            /:::/         \
           /  /||   {&}   |
          (  / (\         /
          / /   \'-.___.-'
        _/ /     \ \
       /___|    /___|
""" + RESET)
    elif g == Guard.LOW:
        return (BLUE + r"""
   .-=========-.
   |           |
   |  ALBER    |
   '-=========-'
           __
          /  )
         / _I_
         || __|
         ||___|
         //.:.\-\
       // |.:. /-----\
      // |___|::oOo::|
     //  /   |:<_T_>:|
   ---+-|_____\ ::: /
     ||  | |  \ \:/
     ||  | |   | |
     ||  \ /   | \___
     V   / |   \_____\
         `-'
""" + RESET)
    elif g == Guard.NO:
        return (YELLOW + r"""
   .-=========-.
   |   REST    |
   |           |
   '-=========-'
              {}
             {{}}
             {{}}
              {}
            .-''-.
           /  __  \
          /.-'  '-.\
          \::.  .::/
           \'    '/
      __ ___)    (___ __
    .'   \\        //   `.
   /     | '-.__.-' |     \
   |     |  '::::'  |     |
   |    /    '::'    \    |
   |_.-;\     __     /;-._|
   \.'^`\\    \/    //`^'./
   /   _.-._ _||_ _.-._   \
  `\___\    '-..-'    /___/`
       /'---.  `\.---'\
      ||    |`\\\|    ||
      ||    | || |    ||
      |;.__.' || '.__.;|
      |       ||       |
      {{{{{{{{||}}}}}}}}
       |      ||      |
       |.-==-.||.-==-.|
       <.    .||.    .>
        \'=='/||\'=='/
        |   / || \   |
        |   | || |   |
        |   | || |   |
        /^^\| || |/^^\
       /   .' || '.   \
      /   /   ||   \   \
     (__.'    \/    '.__)
""" + RESET)
    return "Unknown Guard"

def terrain_ascii(t: Terrain) -> str:
    if t == Terrain.OPEN:
        return r"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             OPEN FIELD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
    elif t == Terrain.NARROW:
        return r"""
||===================================||
||         NARROW PASSAGE            ||
||===================================||
"""
    elif t == Terrain.ROUGH:
        return r"""
/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
       ROUGH, TREACHEROUS LAND
/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
"""
    return "Unknown Terrain"

# Upgraded ASCII art for combat actions
def action_ascii(a: Action) -> str:
    if a.type == ActionType.STRIKE:
        return (BOLD + RED + r"""
   ▄████████  ▄█  ███▄▄▄▄                ▄█    █▄       ▄████████ ███    █▄  
  ███    ███ ███  ███▀▀▀██▄             ███    ███     ███    ███ ███    ███ 
  ███    █▀  ███▌ ███   ███             ███    ███     ███    ███ ███    ███ 
 ▄███▄▄▄     ███▌ ███   ███            ▄███▄▄▄▄███▄▄   ███    ███ ███    ███ 
▀▀███▀▀▀     ███▌ ███   ███           ▀▀███▀▀▀▀███▀  ▀███████████ ███    ███ 
  ███    █▄  ███  ███   ███             ███    ███     ███    ███ ███    ███ 
  ███    ███ ███  ███   ███             ███    ███     ███    ███ ███    ███ 
  ██████████ █▀    ▀█   █▀              ███    █▀      ███    █▀  ████████▀  
                                                                             
  
      _,.
    ,` -.)
   ( _/-\\-._
  /,|`--._,-^|      ------,
  \_| |`-._/||      ----,'|
    |  `-, / |      ---/  /
    |     || |     ---/  /
     `r-._||/   __   /  /
 __,-<_     )`-/  `./  /
'  \   `---'   \   /  /
    |           |./  /
    /           //  /
\_/' \         |/  /
 |    |   _,^-'/  /
 |    , ``  (\/  /_
  \,.->._    \X-=/^
  (  /   `-._//^`
   `Y-.____(__}
    |     {__)
          ()
     
""" + RESET)
    elif a.type == ActionType.THRUST:
        return (BOLD + MAGENTA + r"""
   ▄████████     ███        ▄████████  ▄████████    ▄█    █▄       ▄████████ ███▄▄▄▄   
  ███    ███ ▀█████████▄   ███    ███ ███    ███   ███    ███     ███    ███ ███▀▀▀██▄ 
  ███    █▀     ▀███▀▀██   ███    █▀  ███    █▀    ███    ███     ███    █▀  ███   ███ 
  ███            ███   ▀  ▄███▄▄▄     ███         ▄███▄▄▄▄███▄▄  ▄███▄▄▄     ███   ███ 
▀███████████     ███     ▀▀███▀▀▀     ███        ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀     ███   ███ 
         ███     ███       ███    █▄  ███    █▄    ███    ███     ███    █▄  ███   ███ 
   ▄█    ███     ███       ███    ███ ███    ███   ███    ███     ███    ███ ███   ███ 
 ▄████████▀     ▄████▀     ██████████ ████████▀    ███    █▀      ██████████  ▀█   █▀  
                                                                                       
                            _  
                            \\                
                            ,--.                       
                          _',|| )                    
            ,.,,.,-----""' "--v-.___      |  ________   
            |,"---.--''/       /,.__"")`-:|._________>
                      /     ,."'          | 
                   _ )______;                          
                _,' |  .''''""---.              
            _,-'  ." \/,,..---/_ /                   
          ,-\,.'''            \ (                    
      _ .".--"                ( :                    
    ,- ,."                    ; !                    
___(_(."           -------....L_">


""" + RESET)
    elif a.type == ActionType.DEFEND:
        return (BOLD + BLUE + r"""
 ▄█    █▄     ▄████████    ▄████████    ▄████████    ▄████████     ███      ▄███████▄     ▄████████ ███▄▄▄▄   
███    ███   ███    ███   ███    ███   ███    ███   ███    ███ ▀█████████▄ ██▀     ▄██   ███    ███ ███▀▀▀██▄ 
███    ███   ███    █▀    ███    ███   ███    █▀    ███    █▀     ▀███▀▀██       ▄███▀   ███    █▀  ███   ███ 
███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀   ███         ▄███▄▄▄         ███   ▀  ▀█▀▄███▀▄▄  ▄███▄▄▄     ███   ███ 
███    ███ ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   ▀███████████ ▀▀███▀▀▀         ███       ▄███▀   ▀ ▀▀███▀▀▀     ███   ███ 
███    ███   ███    █▄  ▀███████████          ███   ███    █▄      ███     ▄███▀         ███    █▄  ███   ███ 
███    ███   ███    ███   ███    ███    ▄█    ███   ███    ███     ███     ███▄     ▄█   ███    ███ ███   ███ 
 ▀██████▀    ██████████   ███    ███  ▄████████▀    ██████████    ▄████▀    ▀████████▀   ██████████  ▀█   █▀  
                          ███    ███                                                                          
""" + RESET)
    elif a.type == ActionType.FEINT:
        return (BOLD + YELLOW + r"""
███▄▄▄▄      ▄████████  ▄████████    ▄█    █▄       ▄████████    ▄████████  ▄█     ▄████████    ▄████████ ███▄▄▄▄   
███▀▀▀██▄   ███    ███ ███    ███   ███    ███     ███    ███   ███    ███ ███    ███    ███   ███    ███ ███▀▀▀██▄ 
███   ███   ███    ███ ███    █▀    ███    ███     ███    ███   ███    █▀  ███▌   ███    █▀    ███    █▀  ███   ███ 
███   ███   ███    ███ ███         ▄███▄▄▄▄███▄▄  ▄███▄▄▄▄██▀  ▄███▄▄▄     ███▌   ███         ▄███▄▄▄     ███   ███ 
███   ███ ▀███████████ ███        ▀▀███▀▀▀▀███▀  ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ███▌ ▀███████████ ▀▀███▀▀▀     ███   ███ 
███   ███   ███    ███ ███    █▄    ███    ███   ▀███████████   ███    █▄  ███           ███   ███    █▄  ███   ███ 
███   ███   ███    ███ ███    ███   ███    ███     ███    ███   ███    ███ ███     ▄█    ███   ███    ███ ███   ███ 
 ▀█   █▀    ███    █▀  ████████▀    ███    █▀      ███    ███   ██████████ █▀    ▄████████▀    ██████████  ▀█   █▀  
                                                   ███    ███                                                       
""" + RESET)
    elif a.type == ActionType.REST:
        return (BOLD + GREEN + r"""
   ▄█    █▄    ███    █▄      ███        ▄████████ ███▄▄▄▄   
  ███    ███   ███    ███ ▀█████████▄   ███    ███ ███▀▀▀██▄ 
  ███    ███   ███    ███    ▀███▀▀██   ███    █▀  ███   ███ 
 ▄███▄▄▄▄███▄▄ ███    ███     ███   ▀  ▄███▄▄▄     ███   ███ 
▀▀███▀▀▀▀███▀  ███    ███     ███     ▀▀███▀▀▀     ███   ███ 
  ███    ███   ███    ███     ███       ███    █▄  ███   ███ 
  ███    ███   ███    ███     ███       ███    ███ ███   ███ 
  ███    █▀    ████████▀     ▄████▀     ██████████  ▀█   █▀  
                                                             
            {}
           {{}}
           {{}}
            {}
          .-''-.
         /  __  \
        /.-'  '-.\
        \::.  .::/
         \'    '/
    __ ___)    (___ __
  .'   \\        //   `.
 /     | '-.__.-' |     \
 |     |  '::::'  |     |
 |    /    '::'    \    |
 |_.-;\     __     /;-._|
 \.'^`\\    \/    //`^'./
 /   _.-._ _||_ _.-._   \
`\___\    '-..-'    /___/`
     /'---.  `\.---'\
    ||    |`\\\|    ||
    ||    | || |    ||
    |;.__.' || '.__.;|
    |       ||       |
    {{{{{{{{||}}}}}}}}
     |      ||      |
     |.-==-.||.-==-.|
     <.    .||.    .>
      \'=='/||\'=='/
      |   / || \   |
      |   | || |   |
      |   | || |   |
      /^^\| || |/^^\
     /   .' || '.   \
    /   /   ||   \   \
   (__.'    \/    '.__)
""" + RESET)
    return ""

def guard_to_string(g: Guard) -> str:
    if g == Guard.HIGH:
        return "High Guard (Vom Tach)"
    elif g == Guard.MIDDLE:
        return "Middle Guard (Pflug)"
    elif g == Guard.LOW:
        return "Low Guard (Alber)"
    elif g == Guard.NO:
        return "No Guard"
    return "Unknown"

def action_to_string(a: Action) -> str:
    if a.type == ActionType.STRIKE:
        return f"Strike from {guard_to_string(a.starting_guard)} to {guard_to_string(a.target_guard)}"
    elif a.type == ActionType.THRUST:
        return f"Thrust from {guard_to_string(a.starting_guard)} to {guard_to_string(a.target_guard)}"
    elif a.type == ActionType.DEFEND:
        return f"Defend in {guard_to_string(a.starting_guard)}"
    elif a.type == ActionType.FEINT:
        return f"Feint from {guard_to_string(a.starting_guard)}"
    elif a.type == ActionType.REST:
        return "Rest"
    return "Unknown Action"

def is_offensive(a_type: ActionType) -> bool:
    return a_type in (ActionType.STRIKE, ActionType.THRUST, ActionType.FEINT)

# Calculate stamina cost based on action and equipment
def calculate_stamina_cost(a: Action, knight: Knight) -> int:
    if a.type in (ActionType.STRIKE, ActionType.THRUST):
        base_cost = 15
    elif a.type == ActionType.DEFEND:
        base_cost = 8
    elif a.type == ActionType.FEINT:
        base_cost = 10
    else:  # REST
        base_cost = 0
    weight_factor = (knight.weapon.weight + knight.armor.weight) // 5
    return base_cost + weight_factor

# Apply wound effects to a knight
def apply_wound(knight: Knight, wound: Wound):
    knight.wounds.append(wound)
    if wound == Wound.ARM:
        knight.stamina = max(0, knight.stamina - 10)
        knight.max_stamina = max(50, knight.max_stamina - 5)
    elif wound == Wound.LEG:
        knight.initiative = max(0, knight.initiative - 5)
    elif wound == Wound.HEAD:
        knight.health = max(0, knight.health - 10)
        knight.fatigue = min(100, knight.fatigue + 10)
    elif wound == Wound.BODY:
        knight.health = max(0, knight.health - 5)

# Resolve an attack from one knight to another
def resolve_attack(attacker: Knight, defender: Knight, atk_action: Action, def_action: Action):
    if not is_offensive(atk_action.type):
        return

    hit = False
    damage = attacker.weapon.damage
    dmg_type = "piercing" if atk_action.type == ActionType.THRUST else "slashing"

    if atk_action.type == ActionType.FEINT:
        hit = (def_action.type == ActionType.DEFEND and random.randint(0, 99) < 50)
    else:
        if def_action.type == ActionType.DEFEND and def_action.starting_guard == atk_action.target_guard:
            hit = False  # Perfect block
        elif atk_action.target_guard != def_action.starting_guard or def_action.type == ActionType.REST:
            hit = True
            if dmg_type in defender.armor.defense:
                damage -= defender.armor.defense[dmg_type] * (defender.armor.coverage / 100)
            damage = max(1, int(damage))

    if hit:
        defender.health = max(0, defender.health - damage)
        print(BOLD + RED + "\n**** IMPACT! ****" + RESET)
        print(BOLD + f"{attacker.name} lands a {action_to_string(atk_action)} for {damage} damage!" + RESET)
        print(action_ascii(atk_action))
        if random.randint(0, 99) < 20:  # 20% chance for a wound
            wound_choice = random.choice([Wound.ARM, Wound.LEG, Wound.HEAD, Wound.BODY])
            apply_wound(defender, wound_choice)
            wound_str = ("arm" if wound_choice == Wound.ARM else
                         "leg" if wound_choice == Wound.LEG else
                         "head" if wound_choice == Wound.HEAD else "body")
            print(BOLD + RED + f"{defender.name} suffers a wound to the {wound_str}!" + RESET)
    else:
        print(BOLD + BLUE + "\n**** DEFENDED! ****" + RESET)
        print(f"{defender.name} blocks or avoids the {action_to_string(atk_action)}.")
        defense = Action(ActionType.DEFEND, Guard.NO, def_action.starting_guard)
        print(action_ascii(defense))

# Resolve the combat between player and opponent
def resolve_combat(player_action: Action, opponent_action: Action, player: Knight, opponent: Knight, env: Environment):
    player_init = player.initiative + player.weapon.speed - player.fatigue // 10
    opp_init = opponent.initiative + opponent.weapon.speed - opponent.fatigue // 10
    player_first = player_init >= opp_init

    print("\n" + BOLD + CYAN + "===== COMBAT BEGINS! =====" + RESET)
    if player_first:
        print(BOLD + GREEN + f"{player.name} moves first (Initiative: {player_init} vs {opp_init})" + RESET)
    else:
        print(BOLD + YELLOW + f"{opponent.name} moves first (Initiative: {opp_init} vs {player_init})" + RESET)

    if player_first:
        resolve_attack(player, opponent, player_action, opponent_action)
        if opponent.health > 0:
            resolve_attack(opponent, player, opponent_action, player_action)
    else:
        resolve_attack(opponent, player, opponent_action, player_action)
        if player.health > 0:
            resolve_attack(player, opponent, player_action, opponent_action)

    print(BOLD + CYAN + "===== COMBAT ENDS! =====" + RESET)

    if env.type == Terrain.ROUGH and random.randint(0, 99) < env.obstacle_density * 10:
        print(YELLOW + "\nThe rough terrain hinders movement!" + RESET)
        player.fatigue = min(100, player.fatigue + 5)
        opponent.fatigue = min(100, opponent.fatigue + 5)

# Display a status bar (health, stamina, fatigue)
def display_bar(label: str, value: int, max_value: int, bar_width: int = 20):
    filled = int(value * bar_width / max_value)
    bar = "["
    for i in range(bar_width):
        if i < filled:
            if label.lower() == "health":
                color = GREEN if value > 70 else YELLOW if value > 30 else RED
            elif label.lower() == "stamina":
                color = BLUE if value > 70 else MAGENTA if value > 30 else RED
            elif label.lower() == "fatigue":
                color = GREEN if value < 30 else YELLOW if value < 70 else RED
            else:
                color = RESET
            bar += color + "■" + RESET
        else:
            bar += " "
    bar += f"] {value}/{max_value}"
    print(f"{label}: {bar}")

def display_knight_status(knight: Knight):
    print(BOLD + CYAN + f"=== {knight.name} ===" + RESET)
    print(guard_ascii(knight.current_guard))
    display_bar("Health", knight.health, 100)
    display_bar("Stamina", knight.stamina, knight.max_stamina)
    display_bar("Fatigue", knight.fatigue, 100)
    print(f"Weapon: {BOLD}{knight.weapon.name}{RESET} ({knight.weapon.damage} dmg, {knight.weapon.speed} spd)")
    print(f"Armor:  {BOLD}{knight.armor.name}{RESET} ({knight.armor.weight} wt, {knight.armor.coverage}% coverage)")
    if knight.wounds:
        wounds_str = ", ".join(["Arm" if w == Wound.ARM else "Leg" if w == Wound.LEG else "Head" if w == Wound.HEAD else "Body" for w in knight.wounds])
        print(RED + "Wounds: " + wounds_str + RESET)
    print()

# AI decision-making for the opponent
def ai_choose_action(ai: Knight, player: Knight, env: Environment) -> Action:
    a = Action(ActionType.REST, Guard.NO, ai.current_guard)
    if ai.stamina < 20 or ai.fatigue > 80:
        a.type = ActionType.REST
        a.target_guard = Guard.NO
        return a
    choice = random.randint(0, 99)
    if choice < 40:
        a.type = ActionType.STRIKE
        a.target_guard = random.choice([Guard.HIGH, Guard.MIDDLE, Guard.LOW])
    elif choice < 60:
        a.type = ActionType.THRUST
        a.target_guard = random.choice([Guard.HIGH, Guard.MIDDLE, Guard.LOW])
    elif choice < 80:
        a.type = ActionType.DEFEND
        a.target_guard = Guard.NO
    else:
        a.type = ActionType.FEINT
        a.target_guard = random.choice([Guard.HIGH, Guard.MIDDLE, Guard.LOW])
    if player.fatigue > 50:
        a.type = random.choice([ActionType.STRIKE, ActionType.THRUST])
    if player.current_guard != Guard.NO:
        a.target_guard = player.current_guard
    return a

# Title screen with improved ASCII art
def display_title_screen():
    print(BOLD + CYAN + r"""
  █████▒▓█████  ▄████▄   ██░ ██ ▄▄▄█████▓ ███▄ ▄███▓▓█████  ██▓  ██████ ▄▄▄█████▓▓█████  ██▀███  
▓██   ▒ ▓█   ▀ ▒██▀ ▀█  ▓██░ ██▒▓  ██▒ ▓▒▓██▒▀█▀ ██▒▓█   ▀ ▓██▒▒██    ▒ ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
▒████ ░ ▒███   ▒▓█    ▄ ▒██▀▀██░▒ ▓██░ ▒░▓██    ▓██░▒███   ▒██▒░ ▓██▄   ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
░▓█▒  ░ ▒▓█  ▄ ▒▓▓▄ ▄██▒░▓█ ░██ ░ ▓██▓ ░ ▒██    ▒██ ▒▓█  ▄ ░██░  ▒   ██▒░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
░▒█░    ░▒████▒▒ ▓███▀ ░░▓█▒░██▓  ▒██▒ ░ ▒██▒   ░██▒░▒████▒░██░▒██████▒▒  ▒██▒ ░ ░▒████▒░██▓ ▒██▒
 ▒ ░    ░░ ▒░ ░░ ░▒ ▒  ░ ▒ ░░▒░▒  ▒ ░░   ░ ▒░   ░  ░░░ ▒░ ░░▓  ▒ ▒▓▒ ▒ ░  ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
 ░       ░ ░  ░  ░  ▒    ▒ ░▒░ ░    ░    ░  ░      ░ ░ ░  ░ ▒ ░░ ░▒  ░ ░    ░     ░ ░  ░  ░▒ ░ ▒░
 ░ ░       ░   ░         ░  ░░ ░  ░      ░      ░      ░    ▒ ░░  ░  ░    ░         ░     ░░   ░ 
           ░  ░░ ░       ░  ░  ░                ░      ░  ░ ░        ░              ░  ░   ░     
               ░                                                                                 
                                                                     
""" + RESET)
    print(MAGENTA + "Medieval Combat Simulation" + RESET)
    print(YELLOW + "=================================" + RESET)
    input("Press Enter to begin...")

# Victory screen with ASCII art based on outcome
def display_victory_screen(player: Knight, opponent: Knight):
    if player.health <= 0 and opponent.health <= 0:
        print(YELLOW + "Both knights have fallen! It's a draw!" + RESET)
    elif player.health <= 0:
        print(BOLD + RED + r"""
         _________ _______ _________          _______          _______  _______ 
|\     /|\__   __/(  ____ \\__   __/|\     /|(  ____ \        (  ____ \(  ____ \
| )   ( |   ) (   | (    \/   ) (   | )   ( || (    \/        | (    \/| (    \/
| |   | |   | |   | |         | |   | |   | || (_____         | (__    | (_____ 
( (   ) )   | |   | |         | |   | |   | |(_____  )        |  __)   (_____  )
 \ \_/ /    | |   | |         | |   | |   | |      ) |        | (            ) |
  \   /  ___) (___| (____/\   | |   | (___) |/\____) |        | (____/\/\____) |
   \_/   \_______/(_______/   )_(   (_______)\_______)        (_______/\_______)
                                                                                   
""" + RESET)
        print(RED + f"You have been defeated by {opponent.name}!" + RESET)
    else:
        print(BOLD + GREEN + r"""
         _________ _______ _________ _______  _______          _______  _______ 
|\     /|\__   __/(  ____ \\__   __/(  ___  )(  ____ )        (  ____ \(  ____ \
| )   ( |   ) (   | (    \/   ) (   | (   ) || (    )|        | (    \/| (    \/
| |   | |   | |   | |         | |   | |   | || (____)|        | (__    | (_____ 
( (   ) )   | |   | |         | |   | |   | ||     __)        |  __)   (_____  )
 \ \_/ /    | |   | |         | |   | |   | || (\ (           | (            ) |
  \   /  ___) (___| (____/\   | |   | (___) || ) \ \__        | (____/\/\____) |
   \_/   \_______/(_______/   )_(   (_______)|/   \__/        (_______/\_______)
                                                                                
                                                                        
""" + RESET)
        print(GREEN + f"You have defeated {opponent.name}!" + RESET)
    print(CYAN + "\nFinal Stats:" + RESET)
    print(f"Player Health: {player.health}")
    print(f"Opponent Health: {opponent.health}")

# Main game loop
def main():
    random.seed()
    display_title_screen()

    # Define weapons
    longsword = Weapon(
        name="Longsword",
        damage=12,
        speed=3,
        weight=4,
        two_handed=True,
        type="slashing",
        ascii_art="/=|===============>"
    )
    dagger = Weapon(
        name="Dagger",
        damage=6,
        speed=5,
        weight=1,
        two_handed=False,
        type="piercing",
        ascii_art="/=|==>"
    )

    # Define armors
    plate = Armor(
        name="Plate Armor",
        defense={"slashing": 8, "piercing": 6},
        weight=8,
        coverage=90
    )
    chainmail = Armor(
        name="Chainmail",
        defense={"slashing": 5, "piercing": 4},
        weight=5,
        coverage=70
    )

    # Define environment
    env = Environment(
        type=Terrain.ROUGH,
        obstacle_density=5,
        ascii_art=terrain_ascii(Terrain.ROUGH)
    )

    # Initialize knights
    player = Knight(
        name="Player",
        health=100,
        stamina=100,
        max_stamina=100,
        fatigue=0,
        weapon=longsword,
        armor=plate,
        current_guard=Guard.MIDDLE,
        initiative=10
    )
    opponent = Knight(
        name="Opponent",
        health=100,
        stamina=100,
        max_stamina=100,
        fatigue=0,
        weapon=dagger,
        armor=chainmail,
        current_guard=Guard.HIGH,
        initiative=12
    )

    print(BOLD + GREEN + "\nWelcome to the Knight Game!" + RESET)
    print("You'll face an opponent in medieval combat using historical techniques.")
    print("Choose your guard, actions, and manage your stamina and fatigue wisely!")
    print(env.ascii_art)
    print("You find yourself in rough terrain, ready to face your opponent!")

    round_num = 1
    while player.health > 0 and opponent.health > 0:
        print(BOLD + MAGENTA + f"\n========== ROUND {round_num} ==========" + RESET)
        display_knight_status(player)
        display_knight_status(opponent)

        # Player input for guard selection
        print(BOLD + "Choose your guard:" + RESET)
        print(f"1. {guard_to_string(Guard.HIGH)}")
        print(f"2. {guard_to_string(Guard.MIDDLE)}")
        print(f"3. {guard_to_string(Guard.LOW)}")
        try:
            guard_choice = int(input("Your choice: "))
        except ValueError:
            guard_choice = 2
        player.current_guard = {1: Guard.HIGH, 2: Guard.MIDDLE, 3: Guard.LOW}.get(guard_choice, Guard.MIDDLE)

        # Player input for action selection
        print(BOLD + "Choose your action:" + RESET)
        print("1. Strike - A powerful cutting blow")
        print("2. Thrust - A quick piercing attack")
        print("3. Defend - Block incoming attacks")
        print("4. Feint - Trick your opponent")
        print("5. Rest - Recover stamina")
        try:
            action_choice = int(input("Your choice: "))
        except ValueError:
            action_choice = 5
        player_action_type = {1: ActionType.STRIKE, 2: ActionType.THRUST, 3: ActionType.DEFEND,
                              4: ActionType.FEINT, 5: ActionType.REST}.get(action_choice, ActionType.REST)
        player_action = Action(type=player_action_type, starting_guard=player.current_guard, target_guard=Guard.NO)
        if is_offensive(player_action.type):
            print(BOLD + "Target which guard level:" + RESET)
            print("1. High")
            print("2. Middle")
            print("3. Low")
            try:
                target_choice = int(input("Your choice: "))
            except ValueError:
                target_choice = 2
            player_action.target_guard = {1: Guard.HIGH, 2: Guard.MIDDLE, 3: Guard.LOW}.get(target_choice, Guard.MIDDLE)

        # Check player's stamina
        stamina_cost = calculate_stamina_cost(player_action, player)
        if player.stamina < stamina_cost:
            print(RED + "Not enough stamina, forced to Rest!" + RESET)
            player_action.type = ActionType.REST
            player_action.target_guard = Guard.NO

        # AI opponent action
        opponent_action = ai_choose_action(opponent, player, env)
        opponent.current_guard = opponent_action.starting_guard

        print("\n" + CYAN + f"You: {action_to_string(player_action)}" + RESET)
        print(YELLOW + f"Opponent: {action_to_string(opponent_action)}" + RESET)

        resolve_combat(player_action, opponent_action, player, opponent, env)

        # Update stamina and fatigue
        if player_action.type != ActionType.REST:
            player.stamina = max(0, player.stamina - stamina_cost)
            player.fatigue = min(100, player.fatigue + 5)
        else:
            player.stamina = min(player.max_stamina, player.stamina + 20)
            player.fatigue = max(0, player.fatigue - 10)
        opp_stamina_cost = calculate_stamina_cost(opponent_action, opponent)
        if opponent_action.type != ActionType.REST:
            opponent.stamina = max(0, opponent.stamina - opp_stamina_cost)
            opponent.fatigue = min(100, opponent.fatigue + 5)
        else:
            opponent.stamina = min(opponent.max_stamina, opponent.stamina + 20)
            opponent.fatigue = max(0, opponent.fatigue - 10)

        # Natural stamina regeneration and fatigue effects
        player_regen = max(1, 10 - ((player.weapon.weight + player.armor.weight) // 2) - player.fatigue // 20)
        opp_regen = max(1, 10 - ((opponent.weapon.weight + opponent.armor.weight) // 2) - opponent.fatigue // 20)
        player.stamina = min(player.max_stamina, player.stamina + player_regen)
        opponent.stamina = min(opponent.max_stamina, opponent.stamina + opp_regen)
        player.max_stamina = max(50, 100 - player.fatigue // 2)
        opponent.max_stamina = max(50, 100 - opponent.fatigue // 2)

        input(BOLD + "Press Enter to continue to next round..." + RESET)
        round_num += 1

    display_victory_screen(player, opponent)

if __name__ == "__main__":
    main()
