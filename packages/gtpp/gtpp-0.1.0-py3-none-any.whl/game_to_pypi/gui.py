from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from game_to_pypi.user import User, select_pet, name_pet, get_balance, daily_reward, earn_credits
from game_to_pypi.market import Market

class GameGUI(App):
    def build(self):
        self.user = User("Player")
        self.market = Market()
        layout = BoxLayout(orientation='vertical')

        self.info_label = Label(text=f"Welcome {self.user.name}")
        layout.add_widget(self.info_label)

        btn_pet = Button(text="Select Pet")
        btn_pet.bind(on_press=self.select_pet)
        layout.add_widget(btn_pet)

        btn_market = Button(text="Show Market")
        btn_market.bind(on_press=self.show_market)
        layout.add_widget(btn_market)

        btn_daily = Button(text="Daily Reward")
        btn_daily.bind(on_press=self.daily_reward)
        layout.add_widget(btn_daily)

        return layout

    def select_pet(self, instance):
        select_pet(self.user, "cat")
        name_pet(self.user, "Fluffy")
        self.info_label.text = f"Pet: {self.user.pet_name}"

    def show_market(self, instance):
        self.market.show_items()

    def daily_reward(self, instance):
        daily_reward(self.user)

def main():
    GameGUI().run()
