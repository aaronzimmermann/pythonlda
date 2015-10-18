MISSION

To figure out what the correct structure of the topic_word_count matrix in topic-model.py needs to be. 

THE PROBLEM

Assuming that our matrix is an ntopics x nwords matrix, our matrix from Infomap will be 28x4301 however the default matrix created by the LDA code is size 28x9, this doesnt make sense.

INSTRUCTIONS

Run the programs using the supplied *.sh files which launch the programs with the correct launch arguments.
To run LDA without the custom matrix > run_lda_nomatrix.sh
To run LDA with the custom matrix > run_lda_withmatrix.sh
Just in case you want to see or run the map file parser > run_output_matrix.sh

Note that for testing purposes I have removed some subfolders from the original brown corups to make it run faster. The main reason for doing this is because generating a *.map file for the entire brown corupus would have been a long process. 

FILE DESCRIPTIONS

If you need to know more:

- tagged: File containing the brown corpus. For the sake of testing purposes I have removed most of the content and only left a small portion (the "cr" subfolder) otherwise the algorithms take too long to execute.
- lda_output_nomatrix.txt: Output from running LDA without an input matrix
- lda_output_withmatrix.txt: Output from running LDA with an input matrix
- output_matrix.py: Outputs a numpy matrix from a map file. See, run_output_matrix.txt
- pajex.dump: The matrix pickle output by output_matrix.py. See run_output_matrix.txt
- pajek.map: The output from Infomap that we use to generate the matrix. See run_output_matrix.txt
- prepare-posfile-data.py: Part of the supplied python LDA code
- run_lda_nomatrix: Runs the supplied python LDA code without an input matrix which is the default behaviour..sh
- run_lda_withmatrix.sh: Runs the supplied python LDA code with an input matrix using the modifications I made to topic_model.py.
- run_output_matrix.txt: Runs the program I wrote to extract values from a *.map file (output from Infomap) into a numpy matrix and export it as a pickle. Note that because I'm not sure of the exact matrix format I just populate the matrix with all 1 values for the time being.
- stopwords.txt: A list of stopwords used by LDA
- topic-model.py: Part of the supplied python LDA code
