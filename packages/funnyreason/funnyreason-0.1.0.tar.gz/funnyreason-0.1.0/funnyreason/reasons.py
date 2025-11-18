import random

REASONS = [
    "Because the universe was bored.",
    "A squirrel told me to.",
    "To impress the neighbor's cat.",
    "Because destiny double-booked its schedule.",
    "My WiFi made me do it.",
    "That’s just how the cookie crumbled today.",
    "Gravity was feeling extra emotional."
]

def random_reason():
    return random.choice(REASONS)
