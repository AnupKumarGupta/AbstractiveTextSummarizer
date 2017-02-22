class tag_data(object):

    """
    Usage
    =====
    Break up given paragraphs into text into individual sentences.

    Abbreviations: Dr. W. Watson is amazing. In this case,
    the first and second '.' occurs after Dr (Doctor) and
    W (initial in the person's name) are not to be confused
    as the end of the sentence.

    Sentences enclosed in quotes: "What good are they? They're led about just for show!" remarked another.
    All of this, should be identified as just one sentence.

    Questions and exclamations: Who is it? -This is a question.
    This is identified as a sentence.
    I am tired! -Something which has been exclaimed.
    This should also is identified as a sentence.


    Parameters
    ==========
    para: A chunk of text, containing several sentences,
    questions, statements and exclamations- all in one line.

    """
    def tag_sentences(self, para):

        def find_marks(listcheck, mark, lst):
            return [i for i, ltr in enumerate(listcheck) if mark == ltr and i not in lst]


        quotes = find_marks(para, '"', [])
        count_single_quote_begin = para.count(" '")
        count_single_quote_ends = para.count("' ")
        single_quote_begin_index = 0
        single_quote_end_index = 0
        list_single_quote_begin_index = []
        list_single_quote_end_index = []

        for i in range(count_single_quote_begin):
            single_quote_begin_index = para.index(" '", single_quote_begin_index)
            list_single_quote_begin_index.append(single_quote_begin_index)

        for i in range(count_single_quote_ends):
            single_quote_end_index = para.index("' ", single_quote_end_index)
            list_single_quote_end_index.append(single_quote_begin_index)

        for i in zip(list_single_quote_begin_index, list_single_quote_end_index):
            x, y = i
            quotes = quotes + [x, y]

        ignored_fullstops_list = []
        ignored_questionmark_list = []
        ignored_exclamation_list = []

        for i in xrange(0, len(quotes), 2):
            ignored_fullstops_list = ignored_fullstops_list + [j + quotes[i] for j in find_marks(para[quotes[i]:quotes[i + 1]], '.', [])]
            ignored_questionmark_list = ignored_questionmark_list + [j + quotes[i] for j in find_marks(para[quotes[i]:quotes[i + 1]], '?', [])]
            ignored_exclamation_list = ignored_exclamation_list + [j + quotes[i] for j in find_marks(para[quotes[i]:quotes[i + 1]], '!', [])]

        fullstop = find_marks(para, '.', ignored_fullstops_list)
        to_be_removed = []
        for i in fullstop:
            if (i == 1 or i == 2):
                to_be_removed.append(i)
            if (ord(para[i - 2]) == 32 and (ord(para[i - 1]) in range(65, 91) or ord(para[i - 1]) in range(97, 123))):
                to_be_removed.append(i)
            if (ord(para[i - 3]) == 32 and ord(para[i - 2]) in range(65, 91) and ord(para[i - 1]) in range(97, 123)):
                to_be_removed.append(i)
            if (ord(para[i - 3]) == 32 and ord(para[i - 2]) == 111 and ord(para[i - 1]) == 110):
                to_be_removed.append(i)

        if ('etc.' in para):
            count_abbreviation = para.count('etc.')
            abbreviation_index = 0
            for _ in range(count_abbreviation):
                abbreviation_dot_index = para.index('etc.', abbreviation_index) + 3
                to_be_removed.append(abbreviation_dot_index)
                abbreviation_index = abbreviation_dot_index + 1

        for i in to_be_removed:
            fullstop.remove(i)

        questionmark = find_marks(para, '?', ignored_questionmark_list)
        exclamation = find_marks(para, '!', ignored_exclamation_list)

        valid_stopmarks = fullstop + questionmark + exclamation
        valid_stopmarks = [0] + [i + 1 for i in sorted(valid_stopmarks)]

        tagged_sentences =''
        for i in xrange(len(valid_stopmarks) - 1):
            sentence = para[valid_stopmarks[i]:valid_stopmarks[i + 1]].split()
            str =  ' '.join(sentence)
            tagged_sentences += ' <s> '+str+' </s>'
        return (tagged_sentences)

    def tag_paragraphs(self,input_str):
        tagged_article =''
        paragraph_list = input_str.split('\n')
        for paragraph in (paragraph_list):
            tagged_article += ' <p>'+self.tag_sentences(paragraph)+' </p>'
        return tagged_article

    def tag_input(self,input_str,input_str_type):
        return input_str_type + '= <d>' + self.tag_paragraphs(input_str) + ' </d>'

    def tag_input_data(self,input_str_article ,input_str_abstract):
        print(self.tag_input(input_str_article,'article')+'\t'+ self.tag_input(input_str_abstract,'abstract'))
