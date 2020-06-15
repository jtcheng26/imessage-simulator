import sqlite3
import pandas as pd
from numpy.random import choice

path = '/Users/<user>/Library/Messages/chat.db'  #  replace <user> with your username (without the <>).


#  prepares the messages database
def import_db(file_path):
	print("Reading data...")
	conn = sqlite3.connect(file_path)
	c = conn.cursor()
	c.execute(" select name from sqlite_master where type = 'table' ")
	messages = pd.read_sql_query("select * from message", conn)
	handles = pd.read_sql_query("select * from handle", conn)
	messages.rename(columns={'ROWID': 'message_id'}, inplace=True)
	handles.rename(columns={'id': 'phone_number', 'ROWID': 'handle_id'}, inplace=True)
	messages_db = pd.merge(messages[['text', 'handle_id', 'is_from_me', 'message_id']],
						   handles[['handle_id', 'phone_number']], on='handle_id', how='left')
	return messages_db


#  makes a list of words from the message database for the specified number and person
#  from_me: true if only for user, false for the other person, number: phone number in string with + if necessary
def get_words_from_db(db, from_me=True, number=None):
	print("Getting words...")
	b = 1 if from_me else 0
	word_string = ""
	all_numbers = False
	if number is None:
		all_numbers = True
	for i in range(len(db["text"])):
		if all_numbers:
			number = db["phone_number"][i]
		if db["text"][i] is not None and db["is_from_me"][i] == b and db["phone_number"][i] == number:
			word_string += (db["text"][i] + " ||| ")
	return word_string.split()


#  Makes a data frame with the probabilities of each word following another using a list of words
#  word_list: list of words
def make_prob_df_from_words(word_list):
	print("Processing probabilities...")
	if len(word_list) > 10:
		predict_df = pd.DataFrame(columns=["lead", "follow", "freq"])
		follow = word_list[1:]
		follow.append(word_list[0])
		predict_df['lead'] = word_list
		predict_df['follow'] = follow

		predict_df['freq'] = predict_df.groupby(['lead', 'follow'])[['lead', 'follow']].transform('count').copy()
		predict_df.drop_duplicates(inplace=True)
		pivot_df = predict_df.pivot(index='lead', columns='follow', values='freq')
		total_words = pivot_df.sum(axis=1)
		pivot_df = pivot_df.apply(lambda x: x / total_words)
		return pivot_df
	else:
		return False


#  finds all numbers with more than minNum texts
def filter_numbers(message_data, minNum):
	final_list = []
	numbers_list = message_data["phone_number"].value_counts().keys().tolist()
	numbers_counts = message_data["phone_number"].value_counts().tolist()
	for numIndex in range(len(numbers_counts)):
		if numbers_counts[numIndex] > minNum:
			final_list.append(numbers_list[numIndex])
	return final_list


#  generates 1 text
def make_text(df, startWord, minLength=1, maxLength=10, end_words=None):
	if end_words is None:
		end_words = ["."]
	word = startWord
	sentence = [word]
	while len(sentence) < maxLength:
		next_word = choice(a=list(df.columns), p=df.iloc[df.index == word].fillna(0).values[0])
		if next_word in end_words and len(sentence) >= minLength:
			break
		elif next_word in end_words:
			next_word = choice(list(df.columns))
		else:
			sentence.append(next_word)
		word = next_word
	sentence = ' '.join(sentence)
	return sentence


#  generates num texts with a max length of length using data frame df
#  num: number of texts to generate
#  length: max length of texts
def generate_texts(df, num=5, minLength=1, maxLength=10):
	print("Generating texts...")
	end_words = ["|||", ".", "!", "?"]
	for i in range(num):
		startWord = "|||"
		while startWord in end_words:
			startWord = choice(words)
		sentence = make_text(df, startWord, minLength, maxLength, end_words)
		print(sentence)


message_db = import_db(path)
number_list = filter_numbers(message_db, 100)

for n in range(len(number_list)):
	print(number_list[n])
chosen_number = input("Copy and paste one of the above numbers.")

invalid = False if chosen_number in number_list else True
while invalid is True:
	chosen_number = input("Invalid. Try again. If there is a +1 in front of a number, remember to include it.")
	invalid = False if chosen_number in number_list else True

words = get_words_from_db(message_db, from_me=True, number=chosen_number)
prob_df = make_prob_df_from_words(words)
if prob_df is not False:
	generate_texts(prob_df, 50, 1, 5)
else:
	print("Not enough messages.")
