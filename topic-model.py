#! /usr/bin/env python3

description = """Version of 19th July 2014

(c) Mark Johnson

Reads an input file with one document per line containing white-space
separated words (you should have done all preprocessing such as
tokenisation, stop-word and punctuation removal, case normalisation,
etc., while preparing this file), and trains a variety of topic
models.

To run LDA EM on the Brown corpus, run:

prepare-posfile-data.py | topic-model.py > em-topics-t100.txt

To run LDA VB on the Brown corpus, run:

prepare-posfile-data.py | topic-model.py -a 0.1 -b 0.1 > vb-topics-a0.1-b0.1-t100.txt
"""

import argparse, collections, itertools, math, numpy, sys

def EM_Mstep(x_y_count):

    """This is the M-step for the EM algorithm.  It is just the relative
    frequency of the y_count."""

    sum = x_y_count.sum(axis=1) + 1e-100
    assert(len(sum) == x_y_count.shape[0])
    return x_y_count/sum[:,numpy.newaxis]


def VB_Mstep(x_y_count, alpha):

    """This is the M-step for the VB algorithm.  It involves passing the same counts
    used in the EM algorithm through the exp(digamma(.)) function.  alpha is the 
    Dirichlet prior."""
    
    def exp_digamma(v):

            """This is a rough approximation to exp(digamma(.)), but it's generally
            good enough for the VB EM algorithm."""

            # return v-0.5 if v > 1.0 else 0.5*v*v
            return v-0.5+0.061459483567/v if v >=1.0 else exp_digamma(v+1.0)*math.exp(-1.0/v)

    nx, ny = x_y_count.shape
    sum = x_y_count.sum(axis=1)
    assert(sum.shape[0] == nx)
    x_y_prob = numpy.empty_like(x_y_count)
    for ix in range(nx):
        assert(sum[ix] >= 0.0)
        denom = exp_digamma(sum[ix]+ny*alpha)
        for iy in range(ny):
            x_y_prob[ix,iy] = exp_digamma(x_y_count[ix,iy]+alpha)/denom
            assert(x_y_prob[ix,iy] > 0.0)

    return x_y_prob


def Admixture_Estep(doc_word_count, doc_topic_prob, topic_word_prob):

    """This is the E-step for an admixture model, where documents have
    a distribution over topics, and each word is associated with a topic
    (as in LDA and PLSA)"""

    assert(doc_topic_prob.shape[0] == len(doc_word_count))
    assert(doc_topic_prob.shape[1] == topic_word_prob.shape[0])

    doc_topic_count = numpy.zeros_like(doc_topic_prob)
    topic_word_count = numpy.zeros_like(topic_word_prob)
    logP = 0.0
    for doc, word_counts in enumerate(doc_word_count):
        for word, count in word_counts:
            topic_weight = doc_topic_prob[doc,:] * topic_word_prob[:,word]
            assert(topic_weight.shape[0] == doc_topic_prob.shape[1])
            sum = topic_weight.sum()
            if sum <= 0.0:
                print("Error: sum = {}\ntopic_weight = {}\ndoc = {}, word = {}\ndoc_topic_prob = {}\ntopic_word_prob = {}".format(sum, topic_weight, doc, word, doc_topic_prob[doc,:], topic_word_prob[:,word]))
            topic_weight *= count/sum
            doc_topic_count[doc,:] += topic_weight
            topic_word_count[:,word] += topic_weight
            logP += count*math.log(sum)
    return doc_topic_count, topic_word_count, logP

def summarise_results(topic_word_count, wordid_word,
                      outstream, nwords=20, smooth=5.0):
    
    """Print out summary results.  Sort the clusters by probability, and then
    print the words maximising P(word|cluster)"""

    ntopics, nwordtypes = topic_word_count.shape
    wordid_count = topic_word_count.sum(axis=0)
    topic_count = topic_word_count.sum(axis=1)
    # print("topic_word_count.shape =", topic_word_count.shape, "wordid_count.shape =", wordid_count.shape, "topic_count.shape =", topic_count.shape)
    topic_ordering = sorted(range(len(topic_count)), key=lambda i:topic_count[i], reverse=True)

    for topic in topic_ordering:
        outstream.write("\nTopic {}, count {}\n".format(topic, topic_count[topic]))

        outstream.write("\nWord\tCount\n")
        wordid_prob = collections.Counter()
        for wordid, count in enumerate(topic_word_count[topic,:]):
            if count > 0.0:
                wordid_prob[wordid] += count
        for wordid, count in wordid_prob.most_common(nwords):
            outstream.write("{}\t{:.4f}\n".format(wordid_word[wordid], count))

        outstream.write("\nWord\tP(Topic|Word)\n")
        wordid_prob = collections.Counter()
        for wordid, count in enumerate(topic_word_count[topic,:]):
            if count != 0.0:
                assert(count > 0)
                assert(count <= wordid_count[wordid])
                prob = (count+smooth)/(wordid_count[wordid]+ntopics*smooth)
                assert(prob > 0)
                wordid_prob[wordid] = prob
        for wordid, prob in wordid_prob.most_common(nwords):
            outstream.write("{}\t{:.4f}\n".format(wordid_word[wordid], prob))
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

	# AARON - added extra param for matrix
    parser.add_argument("-m", "--m", dest="m", type=str, default="", help="Path to numpy matrix output by output_matrix.py")
    parser.add_argument("-a", "--a", dest="a", type=float, default=0.0, help="Dirichlet prior for document->topic parameters")
    parser.add_argument("-b", "--b", dest="b", type=float, default=0.0, help="Dirichlet prior for topic->word parameters")
    parser.add_argument("-j", "--jitter", dest="jitter", type=float, default=1e-2, help="Random jitter for initialisation")
    parser.add_argument("-i", "--iterations", dest="iterations", type=int, default=250, help="Number of iterations")
    parser.add_argument("-s", "--random-seed", dest="random_seed", help="Seed for random number generator")
    parser.add_argument("-t", "--topics", dest="topics", type=int, default=100, help="number of topics")
    parser.add_argument("-T", "--trace-stream", dest="trace_stream", default=sys.stderr, type=argparse.FileType('wt'), help="write trace information to this file")
    parser.add_argument("instream", nargs='?', type=argparse.FileType('rU'), default=sys.stdin, help="read documents from this file (one per line)")
    parser.add_argument("outstream", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="write topics to this stream")
    args = parser.parse_args()
    
    

    ntopics = args.topics
    if args.random_seed:
        numpy.random.seed(int(args.random_seed))
        
    # AARON - load input matrix if one was given
    matrix = None
    if args.m != "":        
        # Load the matrix
        matrix = numpy.load(args.m)        
        # Overwrite the number of topics
        ntopics = matrix.shape[0]
    
    docs = [collections.Counter(line.split()) for line in args.instream]
    ndocs = len(docs)

    words = sorted(set(itertools.chain.from_iterable(doc.keys() for doc in docs)))
    nwords = len(words)
    word_id = dict(zip(words, range(nwords)))

    print("Read {} documents, {} word types; random-seed = {}.".format(ndocs, nwords, args.random_seed), 
          file=args.trace_stream, flush=True)

    doc_word_count = [[(word_id[word],count) for word,count in doc.items()] 
                      for doc in docs]
    
    # doc_word_count = numpy.zeros((ndocs,nwords))
    # for docid, doc in enumerate(docs):
    #    for word, count in doc.items():
    #        doc_word_count[docid,word_id[word]] = count

    doc_topic_count = 1.0 + args.jitter*numpy.random.rand(ndocs, ntopics)
    topic_word_count = 1.0 + args.jitter*numpy.random.rand(ntopics, nwords)
    
    # AARON - overwrite topic_word_count with our input matrix
    if args.m != "":
        topic_word_count = matrix
    

    print("Iteration\t-logP")
    for iteration in range(args.iterations):
        if args.a > 0.0:
            doc_topic_prob = VB_Mstep(doc_topic_count, args.a)
        else:
            doc_topic_prob = EM_Mstep(doc_topic_count)
        if args.b > 0.0:
            topic_word_prob = VB_Mstep(topic_word_count, args.b)
        else:
            topic_word_prob = EM_Mstep(topic_word_count)
        doc_topic_count, topic_word_count, logP = Admixture_Estep(doc_word_count, doc_topic_prob, topic_word_prob)
        print("{}\t{:.4g}".format(iteration, -logP), file=args.trace_stream, flush=True)
    
    summarise_results(topic_word_count, words, args.outstream)
