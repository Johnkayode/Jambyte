import requests

def get_questions(subject, mode):
    
    url = f'https://questions.aloc.ng/api/q/10?subject={subject}&type={mode}'
    print(url)
    questions = requests.get(url).json()
    return questions['data']

