import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from db_handler import DBHandler
import logging

kivy.require('2.0.0')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text='Логин', multiline=False)
        self.password = TextInput(hint_text='Пароль', multiline=False, password=True)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        login_button = Button(text='Войти')
        login_button.bind(on_press=self.login)
        layout.add_widget(login_button)
        register_button = Button(text='Зарегистрироваться')
        register_button.bind(on_press=self.go_to_register)
        layout.add_widget(register_button)
        self.add_widget(layout)

    def login(self, instance):
        username = self.username.text
        password = self.password.text
        try:
            user_id = self.manager.db_handler.authenticate_user(username, password)
            if user_id:
                self.manager.current_user = user_id
                self.manager.current = 'work'
            else:
                popup = Popup(title='Login Failed', content=Label(text='Неверный логин или пароль'), size_hint=(0.5, 0.5))
                popup.open()
        except Exception as e:
            logger.exception("Error during login")
            popup = Popup(title='Error', content=Label(text='Произошла ошибка при входе в систему. Проверьте логи для получения подробной информации.'), size_hint=(0.5, 0.5))
            popup.open()

    def go_to_register(self, instance):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text='Логин', multiline=False)
        self.password = TextInput(hint_text='Пароль', multiline=False, password=True)
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        register_button = Button(text='Зарегистрироваться')
        register_button.bind(on_press=self.register)
        layout.add_widget(register_button)
        self.add_widget(layout)

    def register(self, instance):
        username = self.username.text
        password = self.password.text
        try:
            success = self.manager.db_handler.register_user(username, password)
            if success:
                self.manager.current = 'login'
            else:
                popup = Popup(title='Registration Failed', content=Label(text='Такой логин уже используется'), size_hint=(0.5, 0.5))
                popup.open()
        except Exception as e:
            logger.exception("Error during registration")
            popup = Popup(title='Error', content=Label(text='Произошла ошибка при регистрации в системе. Проверьте логи для получения подробной информации.'), size_hint=(0.5, 0.5))
            popup.open()

class WorkScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.label = Label(text='Нажмите "Начать работу", чтобы начать')
        self.layout.add_widget(self.label)
        self.start_button = Button(text='Начать работу')
        self.start_button.bind(on_press=self.start_work)
        self.end_button = Button(text='Закончить работу')
        self.end_button.bind(on_press=self.end_work)
        self.layout.add_widget(self.start_button)
        self.layout.add_widget(self.end_button)
        self.add_widget(self.layout)

    def start_work(self, instance):
        try:
            self.manager.db_handler.log_start(self.manager.current_user)
            self.label.text = 'Работа началась! Нажмите "Закончить работу", чтобы получить расчёт'
        except Exception as e:
            logger.exception("Ошибка старта работы")
            popup = Popup(title='Error', content=Label(text='При запуске работы произошла ошибка. Проверьте логи для получения подробной информации.'), size_hint=(0.5, 0.5))
            popup.open()

    def end_work(self, instance):
        try:
            self.manager.db_handler.log_end(self.manager.current_user)
            salary = self.manager.db_handler.calculate_salary(self.manager.current_user)
            self.label.text = f'Работа закончена! Вы заработали: {salary:.2f} рублей'
        except Exception as e:
            logger.exception("Ошибка завершения работы")
            popup = Popup(title='Error', content=Label(text='Произошла ошибка при завершении работы. Проверьте логи для получения подробной информации.'), size_hint=(0.5, 0.5))
            popup.open()

class WorkLoggerApp(App):
    def build(self):
        self.db_handler = DBHandler()
        self.current_user = None

        sm = ScreenManager()
        sm.db_handler = self.db_handler
        sm.current_user = self.current_user

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(WorkScreen(name='work'))

        return sm

if __name__ == '__main__':
    WorkLoggerApp().run()
