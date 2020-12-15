import os
import telegram
import random
import pytz
import logging
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters 
from bs4 import BeautifulSoup as bs
from questions import get_questions
from faunadb import query as q
from faunadb.objects import Ref
from fauna import get_client

client = get_client()
telegram_bot_token = os.environ.get('TOKEN')
port = int(os.environ.get('PORT',5000))

#ENABLE LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)


updater = Updater(token=telegram_bot_token, use_context=True)
dispatcher = updater.dispatcher
botlers = ['John','Moyin','Kayode','Chioma','Ayo','Jeff','Ebuka','Lateefat','Rose','Jason']




def start(update, context):

    '''
    Starts the bot and saves the user details if it is not existing
    '''

    

    
    chat_id = update.effective_chat.id
    try:
        name = update["message"]["chat"]["first_name"]
    except:
        name = update["message"]["chat"]["username"] 

    

    try:
        client.query(q.get(q.match(q.index("users"), chat_id)))
    except:
        client.query(q.create(q.collection("users"), {
        "data": {
            "id": chat_id,
            "name": name,
            "last_command": "",
            "date": datetime.now(pytz.UTC)},
           
        }))
        
    
    botler = botlers[random.randint(0,9)]
    msg = f"Hello {name} \U0001F600,\nWelcome to Jambyte, my name is {botler} and i will be your Quizbotler.\n \
        \nMaths: /start_mathematics\nEnglish: /start_english\nChemistry: /start_chemistry\nPhysics: /start_physics\
        \nCommerce: /start_commerce\nAccounting: /start_accounting\nGovernment: /start_government\nGeography: /start_geography \
        \nEnglish Lit: /start_englishlit\nBiology: /start_biology\nCRK: /start_crk\nEconomics: /start_economics\nIRK: /start_irk \
        \nInsurance: /start_insurance"
    context.bot.send_message(chat_id=chat_id, text=msg)

def start_quiz(update, context):

    '''
    Starts the quiz and gets the questions from aloc API, then saves to database
    '''
    chat_id = update.effective_chat.id
    message = update.message.text
    try:
        name = update["message"]["chat"]["first_name"] 
    except:
        name = update["message"]["chat"]["username"] 
    subject = message.split('_')[1]
    questions = get_questions(subject=subject,mode='utme')

    quiz = client.query(q.create(q.collection("quiz"), {
            "data": {
                "user_id": chat_id,
                "subject": subject,
                "answered": 0,
                "score": 0,
                "id_": random.randint(0,100),
                'completed': False,
                'questions':questions,
            }
        }))

    
    user = client.query(q.get(q.match(q.index("users"), chat_id)))
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "start_quiz"}}))
    msg = f"{subject.upper()}\n\n10 questions, enter 'q' to continue\n\n/end_quiz to end the quiz session."
    context.bot.send_message(chat_id=chat_id, text=msg)

def end_quiz(update, context):
    chat_id = update.effective_chat.id
    message = update.message.text
    try:
        name = update["message"]["chat"]["first_name"]
    except:
        name = update["message"]["chat"]["username"] 

    quizzes = client.query(q.paginate(q.match(q.index("quiz"), chat_id)))
    user = client.query(q.get(q.match(q.index("users"), chat_id)))

    
    #Gets uncompleted quiz

    quiz = {}
    for i in quizzes["data"]:
       quiz_ = client.query(q.get(q.ref(q.collection("quiz"), i.id())))
       if not quiz_["data"]["completed"]:
           quiz = quiz_
           break

    
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "end_quiz"}}))
        
        
    client.query(q.update(q.ref(q.collection("quiz"), quiz["ref"].id()), {"data": {"completed": True}}))
    context.bot.send_message(chat_id=chat_id,
            text=f"Quiz completed\nScore: {int(quiz['data']['score'])}/10 ",
            reply_markup=telegram.ReplyKeyboardRemove())
    botler = botlers[random.randint(0,9)]
    msg = f"Hello {name} \U0001F600,\nWelcome to Jambito, my name is {botler} and i will be your Quizbotler.\n \
    \nMaths: /start_mathematics\nEnglish: /start_english\nChemistry: /start_chemistry\nPhysics: /start_physics\
    \nCommerce: /start_commerce\nAccounting: /start_accounting\nGovernment: /start_government\nGeography: /start_geography \
    \nEnglish Lit: /start_englishlit\nBiology: /start_biology\nCRK: /start_crk\nEconomics: /start_economics\nIRK: /start_irk \
    \nInsurance: /start_insurance"
    context.bot.send_message(chat_id=chat_id, text=msg)
        
def common_message(update, context):
    """
    General response handler for quiz
    """
    
    chat_id = update.effective_chat.id
    message = update.message.text
    user = client.query(q.get(q.match(q.index("users"), chat_id)))
    last_command = user["data"]["last_command"]
    try:
        name = update["message"]["chat"]["first_name"]
    except:
        name = update["message"]["chat"]["username"] 
 



    quizzes = client.query(q.paginate(q.match(q.index("quiz"), chat_id)))

    
    #Gets uncompleted quiz

    quiz = {}
    for i in quizzes["data"]:
       quiz_ = client.query(q.get(q.ref(q.collection("quiz"), i.id())))
       if not quiz_["data"]["completed"]:
           quiz = quiz_
           break
    
      

    
    #Gets questions' details
    questions_left = 10 - int(quiz['data']['answered'])
    questions = quiz['data']['questions']


    #Hnadles the last question and ends the quiz
    if questions_left == 1:
        if message == user['data']['answer']:
            
            score = int(quiz['data']['score']) + 1
            
        else:
            score = int(quiz['data']['score'])
        answered = int(quiz['data']['answered']) + 1
        client.query(q.update(q.ref(q.collection("quiz"), quiz["ref"].id()), {"data": {"score": score,"answered": answered}}))
        client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "end_quiz"}}))
        
        
        client.query(q.update(q.ref(q.collection("quiz"), quiz["ref"].id()), {"data": {"completed": True}}))
        context.bot.send_message(chat_id=chat_id,
                text=f"Quiz completed\nScore: {int(quiz['data']['score'])}/10 ",
                reply_markup=telegram.ReplyKeyboardRemove())
        botler = botlers[random.randint(0,9)]
        msg = f"Hello {name} \U0001F600,\nWelcome to Jambito, my name is {botler} and i will be your Quizbotler.\n \
        \nMaths: /start_mathematics\nEnglish: /start_english\nChemistry: /start_chemistry\nPhysics: /start_physics\
        \nCommerce: /start_commerce\nAccounting: /start_accounting\nGovernment: /start_government\nGeography: /start_geography \
        \nEnglish Lit: /start_englishlit\nBiology: /start_biology\nCRK: /start_crk\nEconomics: /start_economics\nIRK: /start_irk \
        \nInsurance: /start_insurance"
        context.bot.send_message(chat_id=chat_id, text=msg)
        
    #Handles starting the quiz
    elif last_command == 'start_quiz' or message == 'q':
        print(questions_left)
        if questions_left > 1:
            answered = int(quiz['data']['answered'])
            question = questions[answered]
            title = bs(question['question'],'lxml').text
            section = str(question['section']).capitalize()
            if section:
                context.bot.send_message(chat_id=chat_id,
                    text=f"{section}\n\n{int(quiz['data']['answered']) + 1}. {title}\n\n" + \
                        '\n'.join(f'{aid}. {text}' for aid, text in sorted(question['option'].items())),
                    reply_markup=telegram.ReplyKeyboardMarkup([[aid for aid in sorted(question['option'])]]))
            else:
                context.bot.send_message(chat_id=chat_id,
                    text=f"{int(quiz['data']['answered']) + 1}. {title}\n\n" + \
                        '\n'.join(f'{aid}. {text}' for aid, text in sorted(question['option'].items())),
                    reply_markup=telegram.ReplyKeyboardMarkup([[aid for aid in sorted(question['option'])]]))
            client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "answer_quiz","answer":question['answer']}}))

        else:
            
            context.bot.send_message(chat_id=chat_id,
                text=f"Quiz completed\nScore: {int(quiz['data']['score'])}/10",
                reply_markup=telegram.ReplyKeyboardRemove())
            client.query(q.update(q.ref(q.collection("quiz"), quiz["ref"].id()), {"data": {"completed": True}}))
            botler = botlers[random.randint(0,9)]
            msg = f"Hello {name} \U0001F600,\nWelcome to Jambito, my name is {botler} and i will be your Quizbotler.\n \
            \nMaths: /start_mathematics\nEnglish: /start_english\nChemistry: /start_chemistry\nPhysics: /start_physics\
            \nCommerce: /start_commerce\nAccounting: /start_accounting\nGovernment: /start_government\nGeography: /start_geography \
            \nEnglish Lit: /start_englishlit\nBiology: /start_biology\nCRK: /start_crk\nEconomics: /start_economics\nIRK: /start_irk \
            \nInsurance: /start_insurance"
            context.bot.send_message(chat_id=chat_id, text=msg)

    #Receives answers and send next questions
    elif last_command == 'answer_quiz':
        print(message)
        if message == user['data']['answer']:
            
            score = int(quiz['data']['score']) + 1
            
        else:
            score = int(quiz['data']['score'])
        answered = int(quiz['data']['answered']) + 1
        client.query(q.update(q.ref(q.collection("quiz"), quiz["ref"].id()), {"data": {"score": score,"answered": answered}}))
        client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "start_quiz"}}))
        
        if questions_left > 1:
            
            answered = int(quiz['data']['answered'])
            question = questions[answered + 1]
            title = bs(question['question'],'lxml').text
            section = str(question['section']).capitalize()
            if section:
                context.bot.send_message(chat_id=chat_id,
                    text=f"{section}\n\n{int(quiz['data']['answered']) + 2}. {title}\n\n" + \
                        '\n'.join(f'{aid}. {text}' for aid, text in sorted(question['option'].items())),
                    reply_markup=telegram.ReplyKeyboardMarkup([[aid for aid in sorted(question['option'])]]))
            else:
                context.bot.send_message(chat_id=chat_id,
                    text=f"{int(quiz['data']['answered']) + 2}. {title}\n\n" + \
                        '\n'.join(f'{aid}. {text}' for aid, text in sorted(question['option'].items())),
                    reply_markup=telegram.ReplyKeyboardMarkup([[aid for aid in sorted(question['option'])]]))

            client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": "answer_quiz","answer":question['answer']}}))

        else:
            
            context.bot.send_message(chat_id=chat_id,
                text=f"Quiz completed\nScore: {int(quiz['data']['score'])}/10",
                reply_markup=telegram.ReplyKeyboardRemove())
            botler = botlers[random.randint(0,9)]
            msg = f"Hello {name} \U0001F600,\nWelcome to Jambito, my name is {botler} and i will be your Quizbotler.\n \
            \nMaths: /start_mathematics\nEnglish: /start_english\nChemistry: /start_chemistry\nPhysics: /start_physics\
            \nCommerce: /start_commerce\nAccounting: /start_accounting\nGovernment: /start_government\nGeography: /start_geography \
            \nEnglish Lit: /start_englishlit\nBiology: /start_biology\nCRK: /start_crk\nEconomics: /start_economics\nIRK: /start_irk \
            \nInsurance: /start_insurance"
            context.bot.send_message(chat_id=chat_id, text=msg)
    else:
        context.bot.send_message(chat_id=chat_id,
                text="Unknown Command",
                reply_markup=telegram.ReplyKeyboardRemove())


def error(update, context):
    #Logs update errors
    logger.warning('Update "%s" caused by error "%s"', update, context.error)           

    
            

def main():
   
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('end_quiz', end_quiz))
    dispatcher.add_handler(MessageHandler(Filters.regex("/start_[a-z]*"), start_quiz))
    dispatcher.add_handler(MessageHandler(None, common_message))

    dispatcher.add_error_handler(error)

    updater.start_webhook(listen='0.0.0.0', port=int(port), url_path=telegram_bot_token)
    updater.bot.setWebhook('https://jambito-bot.herokuapp.com/' + telegram_bot_token)
    updater.idle()


if __name__ == '__main__':
    main()