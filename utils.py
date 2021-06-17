import random

class Botler():
    def __init__(self):
        self.botlers = ['Maureen','Moyin','Kayode','Chioma','Ayo','Jeff','Ebuka','Lateefat','Rose','Jason']

    def get(self):
        return self.botlers[random.randint(0,len(self.botlers))]







class MyMessage():
    def __init__(self):
        self.subjects = ['Mathematics','English','Chemistry','Physics','Commerce',
        'Accounting','Government','Geography','English Lit','Biology','CRK','Economics','IRK','Insurance']

    def get(self, name, botler):
        message = f"Hello {name} \U0001F600,\nWelcome to Jambyte, my name is {botler} and i will be your Quizbotler.\n\n"
        for subject in self.subjects:
            sub = subject.replace(' ','').lower()
            message += f'{subject}: start_{sub} \n'

        return message
