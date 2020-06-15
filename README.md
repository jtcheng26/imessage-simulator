# imessage-simulator
Generates a list of texts that sound like you using Markov Chains.  

### Usage
> Only works on Mac OS.

At the top of the `TextGenerator.py` file, specify the path to your chat.db file (the given path usually works, just replace <user> with your username).  
When prompted, you can choose the phone number of the intended conversation.

### Functions
| Name | Parameters | Purpose |
| ---- | ---------- | ------- |
| `import_db` | `file_path` | Connects to the chat.db file and creates a Pandas dataframe to store relevant data. |
| `get_words_from_db` | `db`, `from_me=True`, `number=None` | Creates a list of words from the Pandas dataframe. When `from_me` is false, script checks for the recipient's words instead of yours. `number` is used to limit the search to just one conversation. |
| `make_prob_df_from_words` | `word_list` | Creates another Pandas dataframe that keeps track of the frequency of each word following another before converting it to a probability to be used in the Markov Chain. |
| `generate_texts` | `df`, `num=5`, `minLength=1`, `maxLength=10` | Generates `num` texts with a minimum length of `minLength` words and a maximum of `maxLength` words. |
