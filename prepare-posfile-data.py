#! /usr/bin/env python3

description = """Version of 19th July 2014

(c) Mark Johnson

Reads tagged data from the U Penn TB3 CDROM and generates 
training corpora for topic modelling"""

import argparse, collections, glob, itertools, os.path, re, sys

pos_data_rex = re.compile(r"""
(?P<HEADER>^(?:\*x\*.*\*x\*[ \t]*\n)+\s*)
|(?P<EOS>\n[=]+\s*\n)
|(?:(?P<WORD>(?:[^ \t\n/\[\]]|\\.)+)/(?P<TAG>[^ \t\n/\[\]\|]+))
|(?P<OSB>\[)
|(?P<CSB>\])""",
                          re.VERBOSE)

alpha_rex = re.compile(r"^[A-Za-z]+$")

def read_sentence(ftext, stopwords=[], transform=lambda w, p: w):
    sentence = []
    for mo in pos_data_rex.finditer(ftext):
        # print(mo.lastgroup, mo.groupdict())
        if mo.lastgroup == "EOS" and len(sentence) > 0:
            yield sentence
            sentence = []
        elif mo.lastgroup == "TAG":
            word = transform(mo.group("WORD"), mo.group("TAG"))
            if word and word not in stopwords:
                sentence.append(word)
    if len(sentence) > 0:
        yield sentence
    
def read_files(filepath, stopwords, transform):
    for fname in sorted(glob.glob(filepath)):
        yield os.path.basename(fname), list(read_sentence(open(fname, "rU").read(), stopwords, transform))

def remove_words(data, min_word_count, top_words):
    """remove words from data that doesn't occur at least min_word_count times
    or is in the top_words number of most-frequent words"""
    word_count = collections.Counter()
    for fname, sentences in data:
        for sentence in sentences:
            word_count.update(sentence)
    stopwords = set(w for w,c in word_count.most_common(top_words))
    for fname, sentences0 in data:
        sentences1 = []
        for sentence0 in sentences0:
            sentence1 = [word for word in sentence0
                         if word_count.get(word) >= min_word_count 
                         and word not in stopwords]
            if sentence1:
                sentences1.append(sentence1)
        if sentences1:
            yield fname, sentences1

def flatten_lists(xs):
    """yields a stream of the non-list elements in xs"""
    return itertools.chain.from_iterable(xs)
                
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-p", "--path", dest="path",
                        default="/comp350/python/tagged/pos/brown/*/*.pos",
                        help="file path for POS-tagged data")
    parser.add_argument("-m", "--min-word-count", dest="min_word_count", 
                        default=5, type=int,
                        help="ignore words that appear less frequently than this")
    parser.add_argument("-s", "--stop-words", dest="stop_words",
                        help="file containing stopword list")
    parser.add_argument("-T", "--top-words", dest="top_words", 
                        default=200, type=int,
                        help="add the most frequent words to the stop-word list")
    parser.add_argument("-t", "--transform", dest="transform", 
                        choices=['none','lower','loweralpha'], 
                        default='loweralpha',
                        help="apply this transform to words")
    args = parser.parse_args()

    if args.stop_words:
        stopwords = set(open(args.stop_words, "rU").read().split())
    else:
        stopwords = set()

    if args.transform == 'none':
        transform = lambda w, p: w
    elif args.transform == 'lower':
        transform = lambda w, p: w.lower()
    elif args.transform == 'loweralpha':
        transform = lambda w, p: w.lower() if alpha_rex.match(w) else None

    data = list(read_files(args.path, stopwords, transform))

    if args.min_word_count > 0 or args.top_words:
        data = remove_words(data, args.min_word_count, args.top_words)

    for fname, sentences in data:
        print(" ".join(flatten_lists(sentences)))
