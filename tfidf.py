from collections import Counter
import csv
import math
import matplotlib.pyplot as plt
import string
import sys
from wordcloud import WordCloud
inTable = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
outTable = "abcdefghijklmnopqrstuvwxyz"
translateTable = str.maketrans(inTable, outTable, string.punctuation + '“”')

maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

def load_articles(filename, skipHeader = True):
    with open(filename, encoding="utf8") as csvfile:
        articles = []
        articleMetaDataList = []
        readCsv = csv.reader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(readCsv):
            if (i % 500 == 0):
                print('Loading article {}'.format(i))
            if i == 0 and skipHeader:
                continue
            articleMetaData = {
                'title': row[2],
                'publication': row[3],
                'author': row[4],
                'date': row[5],
                'year': row[6],
                'month': row[7],
                'url': row[8],
            }
            articleMetaDataList.append(articleMetaData)
            articles.append(row[9])
        csvfile.close()
        return articleMetaDataList, articles
    return []

def tf(word, articleInfo):
    return articleInfo['words'][word]['count'] / articleInfo['total_words']

def n_containing(word, wordCount):
    return wordCount['global'][word]['appeared_in']

def idf(word, wordCount):
    return math.log(len(wordCount['articles']) / (1 + n_containing(word, wordCount)))

def tfidf(word, articleInfo, wordCount):
    return tf(word, articleInfo) * idf(word, wordCount)

def get_word_count(article, globalWordCount, articleInfo):
    seenWords = set()
    for word in article.split():

        normalizedWord = word.translate(translateTable)
        if normalizedWord not in globalWordCount:
            globalWordCount[normalizedWord] = {
                'count': 0,
                'appeared_in': 0
            }

        if (normalizedWord not in seenWords):
            articleInfo['words'][normalizedWord] = {
                'count': 0
            }
            globalWordCount[normalizedWord]['appeared_in'] += 1
            seenWords.add(normalizedWord)

        articleInfo['words'][normalizedWord]['count'] += 1
        articleInfo['total_words'] += 1
        globalWordCount[normalizedWord]['count'] += 1

def calculate_tfidf(wordCount):
    scores = {}
    for i, article in enumerate(wordCount['articles']):
        if i % 500 == 0:
            print('Calculating tfidf for article {}'.format(i))

        title = article['title']
        words = article['words']
        total_words = article['total_words']
        scores[title] = {}
        for word in words:
            scores[title][word] = tfidf(word, article, wordCount)
    return scores

if __name__ == '__main__':
    articleMetaData, articles = load_articles('articles2.csv')
    wordCount = {
        'global': {},
        'articles': []
    }
    for i, article in enumerate(articles):
        if i % 500 == 0:
            print('Processing article {}'.format(i))

        articleWordCount = {
            'title': articleMetaData[i]['title'],
            'words': {},
            'total_words': 0
        }

        get_word_count(article, wordCount['global'], articleWordCount)
        wordCount['articles'].append(articleWordCount)

    scores = calculate_tfidf(wordCount)
    topMostCommonTopics = Counter()
    for title, wordCounts in scores.items():
        print('Title: ', title)
        sortedWords = sorted(wordCounts.items(), key=lambda x: x[1], reverse=True)
        try:
            topMostCommonTopics[sortedWords[0][0]] += 1
        except IndexError:
            print('Error ', sortedWords[:10])
        i = 1
        for word, score in sortedWords[:10]:
            print('\t {}) {}'.format(i, word))
            i += 1
        print('\n')

    print('Top Most Common Topics')
    i = 1
    for word, _ in topMostCommonTopics.most_common(10):
        print('\t {}) {}'.format(i, word))
        i += 1

    for index in range(10, 13):
        print(index, ' - ', articleMetaData[index]['title'])
        wordcloud = WordCloud(max_font_size=40).generate(str(articles[index]))
        plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()