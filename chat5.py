from tkinter import *
from urllib.request import urlopen
import json, random, requests
from textblob import TextBlob
from app import db, UserMessage
import numpy as np

GREETING_KEYWORDS = ("hello", "hi", "hey", "howdy", "sup")
GREETING_RESPONSES = ["hey", "hilo"]

def find_pronoun(sent):
	pronoun = None
	
	for word, part_of_speech in sent.tags:
		if part_of_speech == 'PRP' and word.lower() == 'you':
			pronoun = 'I'
		elif part_of_speech == 'PRP' and word == 'I':
			pronoun = 'You'
	return pronoun

def find_verb(sent):
	verb = None
	pos = None
	
	for word, part_of_speech in sent.tags:
		if part_of_speech.startswith('VB'):
			verb = word
			pos = part_of_speech
			break
	return verb, pos

def find_noun(sent):
	noun = None
	
	if not noun:
		for w, p in sent.tags:
			if p == 'NN':
				noun = w
				break
	return noun

def find_adjective(sent):
	adj = None
	
	for w, p in sent.tags:
		if p == 'JJ':
			adj = w
			break
	return adj

def find_candidate_parts_of_speech(blob):
	pronoun = None
	noun = None
	adjective = None
	verb = None
	for sent in blob.sentences:
		pronoun = find_pronoun(sent)
		noun = find_noun(sent)
		adjective = find_adjective(sent)
		verb = find_verb(sent)
	return pronoun, noun, adjective, verb

def check_for_comment_about_bot(pronoun, noun, adjective):
	resp = None
	if pronoun == 'I' and (noun or adjective):
		if noun:
			if random.choice((True, False)):
				resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
			else:
				resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
		else:
			resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
	return resp

# Template for responses that include a direct noun which is indefinite/uncountable
SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "My last startup totally crushed the {noun} vertical",
    "Were you aware I was a serial entrepreneur in the {noun} sector?",
    "My startup is Uber for {noun}",
    "I really consider myself an expert on {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "Yeah but I know a lot about {noun}",
    "My bros always ask me about {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "I'm personally building the {adjective} Economy",
    "I consider myself to be a {adjective}preneur",
]

PRONOUNS = [
	"He", "She", "We", "Us", "They", "Me", "I", "You",
]

VERBS = [
	"swims", "runs", "breathes", "falls", "hikes", "hacks", "wins", "drinks",
]

ADJS = [
	"gross", "blue", "tired", "awesome", "big", "crusty", "clean", "new",
]

NOUNS = [
	"park", "train", "Earth", "bro", "table", "fence", "shrub", "water",
]

def construct_response(pronoun, noun, verb, adj):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    print('making a response!')
    resp = []
	
    if pronoun:
    	resp.append(pronoun)
    else:
        pronoun = random.choice(PRONOUNS)
        resp.append(pronoun)
		
    print(verb)
    if verb:
        verb_word = verb[0]
        resp.append(verb_word)
    else:
        print(random.choice(VERBS))
        verb = random.choice(VERBS)
        resp.append(verb)
    print(resp)
	
    if adj:
    	resp.append(adj)
    else:
        adjective = random.choice(ADJS)
        resp.append(adjective)
		
    if noun:
    	resp.append(noun)
    else:
        resp.append(random.choice(NOUNS))
    print(resp)
    return " ".join(resp)

def check_for_define(text):
	resp = None
	if 'define' in text:
		words = text.split()
		resp = words[words.index('define') + 1]
		resp = resp.definitions[0]
	return resp

def hobot(text):
	blob = TextBlob(text)
	
	pronoun, noun, adjective, verb = find_candidate_parts_of_speech(blob)
	
	resp = check_for_define(blob)
	if resp:
		return resp
	
	for word in blob.words:
		if word in GREETING_KEYWORDS:
			return random.choice(GREETING_RESPONSES)
	if resp: 
		return resp
	
	resp = check_for_comment_about_bot(pronoun, noun, adjective)
	if resp:
		return resp
	
	if pronoun or noun or adjective or verb:
		resp = construct_response(pronoun, noun, verb, adjective)
	
	if resp:
		return resp
	
	return "better luck next time"



# Create the main window to hold the text entry field and other options
master = Tk()
master.title('Messages')

# Define a string to hold message history when texts are sent
messageHistory = ""

i = 0

previousUserHistory = []
previousBotHistory = []

def getHelp():
	helpWindow = Toplevel()
	helpWindow.title('Help Window')

	helpText = "Hey there! I'm hobot! I can tell you the weather, help you with math, play a round of trivia, or talk it out. \nMath: I can add, subtract, multiply, and divide. Just tell me what to do! You can type the number characters or the corresponding words. \nWeather: Just ask about the weather! \nTrivia: Just ask and I'll open up a new game! \nChat: Tell me anything! Just be sure not to use any other keywords! \nDefine: Type 'define' and your word!"

	helpInfo = Label(helpWindow, text=helpText, font=('Helvetica', 10), justify=LEFT)
	helpInfo.pack()

chatBot = Button(master, text="Welcome to chatbot", font=('System', 13), command=getHelp, borderwidth=0)
chatBot.grid(row=0, columnspan=2, sticky=W+E)

def previousMessages():
	#Open a new window to show previous message history
	history = Toplevel()
	history.title('Message History')
	global messageHistory
	w = Label(history, text=messageHistory, justify=LEFT, font=('Helvetica', 15))
	w.pack()

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def triviaRun():
	print('Trivia time!')

	q = urlopen('https://www.opentdb.com/api.php?amount=50&type=multiple&token='+json.loads(urlopen('https://www.opentdb.com/api_token.php?command=request').read().decode('utf-8'))['token'])
	json_string = q.read().decode('utf-8')
	parsed_json = json.loads(json_string)

	triviaWindow = Toplevel()
	triviaWindow.title('Trivia Time!')

	question = Label(triviaWindow, text=parsed_json['results'][0]['question'], font=('System', 13))
	question.grid()

	answerArray = [parsed_json['results'][0]['correct_answer'], parsed_json['results'][0]['incorrect_answers'][0], parsed_json['results'][0]['incorrect_answers'][1], parsed_json['results'][0]['incorrect_answers'][2]]
	random_choice = np.random.choice(4, 4, replace=False)

	correctAnswer = np.argmin(random_choice)

	def checkAnswer(correctAnswer, number):
		if number == correctAnswer:
			print('success')
			resulting = Toplevel()
			resulting.title('')
			a = Label(resulting, text='Correct!', bg='green', font=('helvetica', 25)).pack()
			triviaWindow.destroy()
		else:
			print('fail')
			resulting = Toplevel()
			resulting.title('')
			a = Label(resulting, text='Wrong', bg='red', font=('helvetica', 25)).pack()
			triviaWindow.destroy()
			

	answer1 = Button(triviaWindow, text=answerArray[random_choice[0]], command=lambda:checkAnswer(correctAnswer, 0))
	answer1.grid()
	answer2 = Button(triviaWindow, text=answerArray[random_choice[1]], command=lambda:checkAnswer(correctAnswer, 1))
	answer2.grid()
	answer3 = Button(triviaWindow, text=answerArray[random_choice[2]], command=lambda:checkAnswer(correctAnswer, 2))
	answer3.grid()
	answer4 = Button(triviaWindow, text=answerArray[random_choice[3]], command=lambda:checkAnswer(correctAnswer, 3))
	answer4.grid()

def sendText():

	result = " "

	def getWeather():
		global result
		f = urlopen('http://api.wunderground.com/api/62cf407a8229ef86/geolookup/conditions/q/MA/Boston.json')
		json_string = f.read().decode('utf-8')
		parsed_json = json.loads(json_string)
		location = parsed_json['location']['city']
		temp_f = parsed_json['current_observation']['temp_f']
		result = "Temperature in %s: %s" % (location, temp_f)
		f.close()
		return result


	global previousUserHistory
	global previousBotHistory
	global i

	math = ['plus', 'minus', 'times', 'divide', 'add', 'sum', 'subtract', 'multiply', 'product', 'difference']
	weather = ['weather', 'Weather', 'weather?', 'Weather?']
	trivia = ['trivia', 'quiz', 'question', 'trivia?', 'quiz?']
	helpKeywords = ['help', 'assistance']
	numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "eleven", "twelve", "thirteen", "fifteen", "nine", "ten","twenty", "thirty", "forty", "fifty", "hundred", "thousand", "million"]

	# Send to the console that the message was successful
	print('Sent!')
	global messageHistory

	phrase = str(bodyText.get('1.0', END))

	# Add the sent message to the message history string
	messageHistory += phrase

	previousUserHistory.append(Label(master, text=phrase, font=('Helvetica', 8)))
	previousUserHistory[i].grid(row=5+i, column=0, sticky=W)
	
	j = 0
	numberNumber = []
	state = 0
	isInt = 0
	
	def isInt(s):
		try:
			int(s)
			return True
		except ValueError:
			return False
	
	for word in phrase.split():
		print(word)
		if word.lower() in math and state==0 or isInt(word) and state==0:
			print('math')
			for part in phrase.split():
				for k in numbers:
					try:
						int(part)
						print('found one!')
						print(part)
						state = 1
						numberNumber.append(int(part))
						break
					except:
						pass

					if k in part:
						state = 1
						print('found one!')
						print(part)
						numberNumber.append(text2int(part))
						j+=1
		elif word.lower() in weather and state==0:
			state = 2
		elif word.lower() in helpKeywords and state==0:
			getHelp()
			break
		elif word.lower() in trivia and state==0:
			triviaRun()
			break
		elif state==0:
			result = hobot(phrase)


	if(state == 1):
		if 'add' in phrase or 'Add' in phrase or 'plus' in phrase or 'Plus' in phrase or 'sum' in phrase or 'Sum' in phrase:
			result = 0
			print("adding")
			for element in numberNumber:
				result+=element
		

		elif 'multiply' in phrase or 'Multiply' in phrase or 'times' in phrase or 'Times' in phrase or 'product' in phrase or 'Product' in phrase:
			result = 1
			print("multiplying")
			for element in numberNumber:
				result*=element

		elif 'subtract' in phrase or 'Subtract' in phrase:
			result = 0
			print('subtracting')
			result = numberNumber[1] - numberNumber[0]

		elif 'minus' in phrase or 'Minus' in phrase:
			result = 0
			print('subtracting')
			result = numberNumber[0]-numberNumber[1]

		elif 'difference' in phrase or 'Difference' in phrase:
			result = 0
			print('Finding difference')
			result = abs(numberNumber[1]-numberNumber[0])
		
	elif (state == 2):
		result = getWeather()


	print(result)
	
	message = UserMessage(message=phrase, response=result)
	db.session.add(message)
	db.session.commit()
	
	previousBotHistory.append(Label(master, text=result, font=('Helvetica', 8), fg='green'))
	previousBotHistory[i].grid(row=5+i, column=1, sticky=E)
	
	# Clear the text field entry
	bodyText.delete('1.0', END)
	i+=1


# Large text box on master window for text entry into text message
bodyText = Text(master, height=5)
bodyText.grid(row=2, columnspan=2)
bodyText.focus_set()
	
# Create a send button on the bottom of the page
sendbutton = Button(master, text='Send', command=sendText, font=('System', 10), bg='green', fg='white')
sendbutton.grid(row=3, columnspan=2, sticky=W+E)

mainloop()