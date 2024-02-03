import yaml
import numpy as np

# Load Rasa stories
with open('data/stories.yml', 'r') as file:
    stories_data = yaml.safe_load(file)

# Initialize a list to store the number of turns in each dialogue
turns_per_dialogue = []

# Iterate over each story
for story in stories_data['stories']:
    # Each step in the story is a turn, but we ignore 'slot_was_set' events
    num_turns = 0
    for step in story['steps']:
        #print("step", step)
        if step.get('intent') or step.get('action'):
            num_turns += 1
    
    #num_turns = len([step for step in story['steps'] if step == "intent" or step == "action"])
    turns_per_dialogue.append(num_turns)

# Now you have a list of the number of turns in each dialogue, ignoring 'slot_was_set' events
#print("turns per dialogue", turns_per_dialogue)
mean_turns = np.mean(turns_per_dialogue)
max_turns = np.max(turns_per_dialogue)
min_turns = np.min(turns_per_dialogue)

print(f'The mean number of turns per dialogue is {mean_turns}')
print(f'The maximum number of turns in a dialogue is {max_turns}')
print(f'The minimum number of turns in a dialogue is {min_turns}')


import re
from sklearn.feature_extraction.text import CountVectorizer

# Load Rasa NLU training data
with open('data/nlu/nlu.yml', 'r') as file:
    training_data = yaml.safe_load(file)

# num intents
num_intents = len([intent for intent in training_data['nlu'] if 'intent' in intent])
print(f'\n\n\nThe number of intents in the training data is {num_intents}')#, [intent for intent in training_data['nlu'] if 'intent' in intent])
# Extract text data for vocabulary analysis
#text_data = [ example.split('- ')[1:] for intent in training_data['nlu'] for example in intent['examples'].split('\n') if example != '']
#text_data = [ [example.split('- ')[1:] for example in intent['examples'].split('\n') if example != ''] for intent in training_data['nlu'] ]
text_data = [[example.split('- ')[1] for example in intent['examples'].split('\n') if example != ''] for intent in training_data['nlu'] if 'intent' in intent]
#print("text data", text_data[0])

# count examples per intent
examples_per_intent = [len(intent) for intent in text_data]
print(f'The number of examples per intent is {examples_per_intent}')
mean_examples = np.mean(examples_per_intent)
max_examples = np.max(examples_per_intent)
min_examples = np.min(examples_per_intent)
tot_examples = np.sum(examples_per_intent)

print(f'The mean number of examples per intent is {mean_examples}')
print(f'The maximum number of examples in an intent is {max_examples}')
print(f'The minimum number of examples in an intent is {min_examples}')
print(f'The total number of examples in the training data is {tot_examples}')

# Flatten the list of lists into a single list
text_data = [item for sublist in text_data for item in sublist]

#print("text data", text_data[:2])

# Remove content inside parentheses and curly braces, but keep content inside square brackets
text_data = [re.sub(r'\([^)]*\)', '', example) for example in text_data]  # Remove content inside parentheses
text_data = [re.sub(r'\{[^}]*\}', '', example) for example in text_data]  # Remove content inside curly braces
text_data = [re.sub(r'\[([^]]*)\]', r'\1', example) for example in text_data]  # Keep content inside square brackets

#print("text data", text_data[:6])
# Initialize a CountVectorizer
vectorizer = CountVectorizer()

# Fit the CountVectorizer to the text data
vectorizer.fit(text_data)

# The vocabulary size is the length of the vocabulary
vocabulary_size = len(vectorizer.vocabulary_)

print(f'The vocabulary size is {vocabulary_size}')
