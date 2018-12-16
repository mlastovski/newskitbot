import re

# importing stopwords and converting them to the list
with open('stopwords.txt', 'r') as myfile:
    stopwords = myfile.read().replace('\n', ' ')
    stopwords = re.sub('\W+',' ', stopwords )
    stopwords = stopwords.split(' ')
    # print(stopwords)

def extract_keywords(article_text):

    for word in stopwords:
        while word in article_text: article_text.remove(word)
    final_words = [item for item in article_text if not item.isdigit()]
    filter(lambda a: a != ' ', final_words)
    while '' in final_words:
        final_words.remove('')

    final_words = {i:final_words.count(i) for i in final_words}
    search_num = 3 #minimum numbeer of times that the word should appear in the article
    final_text = []
    for word, num in final_words.items():
        if num >= search_num:
            final_text.append(word)
    #print(final_text, title_text, link)

    final_text = ' '.join(final_text)

    return final_text
