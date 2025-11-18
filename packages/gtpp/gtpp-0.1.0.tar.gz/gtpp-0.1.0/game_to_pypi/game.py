class Game:
    def __init__(self, users):
        self.users = users

    def start_battle(self):
        if len(self.users) < 2:
            print("Not enough players to battle.")
            return
        from random import choice
        user1, user2 = choice(self.users), choice(self.users)
        while user1 == user2:
            user2 = choice(self.users)
        from game_to_pypi.user import battle
        battle(user1, user2)
