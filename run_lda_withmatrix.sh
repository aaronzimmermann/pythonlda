#!/bin/bash
# Runs LDA on the brown corpus but loads the ntopics x nwords matrix output by output_matrix.py
./prepare-posfile-data.py -s ./stopwords.txt | ./topic-model.py -i 10 -m ./pajek.dump > lda_output_withmatrix.txt

