#!/bin/bash
# Runs LDA on the brown corpus with the default settings (no matrix)
./prepare-posfile-data.py -s ./stopwords.txt | ./topic-model.py -i 10 -t 28 > lda_output_nomatrix.txt

