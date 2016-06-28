import snowballstemmer

stemmer = snowballstemmer.stemmer('spanish')
print(stemmer.stemWords("te queremos".split()))
