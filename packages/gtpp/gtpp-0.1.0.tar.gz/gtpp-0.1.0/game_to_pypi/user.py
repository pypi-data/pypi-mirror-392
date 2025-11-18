import random
from datetime import datetime, timedelta

class User:
    def __init__(self, name, credits=100):
        self.name = name
        self.credits = credits
        self.pet = None
        self.pet_name = None
        self.energy = 100
        self.last_daily = datetime.utcnow()

def select_pet(user, pet_type):
    user.pet = pet_type
    print(f"Selected pet: {pet_type}")

def name_pet(user, pet_name):
    user.pet_name = pet_name
    print(f"Pet's name: {pet_name}")

def get_balance(user):
    print(f"{user.name} balance: {user.credits} credits")
    return user.credits

def daily_reward(user):
    now = datetime.utcnow()
    if now - user.last_daily >= timedelta(days=1):
        user.credits += 100
        user.last_daily = now
        print(f"{user.name} received daily reward. Balance: {user.credits}")
    else:
        print(f"{user.name} already collected daily reward today.")

def earn_credits(user, amount):
    user.credits += amount
    print(f"{user.name} earned {amount} credits. Balance: {user.credits}")

def battle(user1, user2):
    # Basit savaş mantığı: rastgele kazanır
    winner, loser = (user1, user2) if random.random() < 0.5 else (user2, user1)
    winner.credits += 50
    print(f"{winner.name} won the battle and earned 50 credits!")
