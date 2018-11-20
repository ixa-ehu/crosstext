#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This script is to generate projection for a given target language from 3 other source languages."""

import sys, os
from collections import Counter
from itertools import *

#backoff corpora
corporaType = "wikiner"
en_freq_tag = "en.wikiner"
es_freq_tag = "es.wikiner"
it_freq_tag = "it.wikiner"
de_freq_tag = "de.wikiner"
en_freq_corpora = '/tartalo03/users/crosstext/ner-silver-standard/wikipedia/wikiner/aij-wikiner-en-nerc.conll02'
it_freq_corpora = '/tartalo03/users/crosstext/ner-silver-standard/wikipedia/wikiner/aij-wikiner-it-nerc.conll02'
es_freq_corpora = '/tartalo03/users/crosstext/ner-silver-standard/wikipedia/wikiner/aij-wikiner-es-nerc.conll02'
de_freq_corpora = '/tartalo03/users/crosstext/ner-silver-standard/wikipedia/wikiner/aij-wikiner-de-nerc.conll02'

#automatic alignments from Europarl train set
de_en_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-de'
es_en_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-es'
it_en_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-it'
de_it_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.de-it'
es_it_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.es-it'
en_it_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-it'
en_es_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-es'
de_es_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.de-es'
it_es_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.es-it'
en_de_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.en-de'
es_de_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.de-es'
it_de_alignment = '/tartalo03/users/crosstext/europarl/train/train.grow-diag-final.alignment.de-it'

en_standard_tag = '/tartalo03/users/crosstext/first-cycle/train-automatic-europarl/en-3-class-train-automatic.conll02'
es_standard_tag = '/tartalo03/users/crosstext/first-cycle/train-automatic-europarl/es-3-class-train-automatic.conll02'
it_standard_tag = '/tartalo03/users/crosstext/first-cycle/train-automatic-europarl/it-3-class-train-automatic.conll02'
de_standard_tag = '/tartalo03/users/crosstext/first-cycle/train-automatic-europarl/de-3-class-train-automatic.conll02'

def read_freq_corpora(filename, lang, corpora):
    """Read back-off corpora (wikiner) and create back-off database."""
    freq_dict = {}
    print("get frequent corpora")
    with open(filename, encoding = "utf8") as f:
        for line in f:
            line = line.split()
            if line != [] and len(line) >= 3:
                if line[0] not in freq_dict.keys():
                    freq_dict[line[0]] = []
                    freq_dict[line[0]].append(line[-1])
                else:
                    freq_dict[line[0]].append(line[-1])
    with open(lang+"."+corpora, "w", encoding = "utf8") as freq_file:
        for word in freq_dict.keys():
            freq = Counter(freq_dict[word]).most_common()
            freq_file.write(word + " " + str(freq).strip('[]')+"\n")

def get_freq_tag(file, lang):
    """Get freq tag file from read_freq_corpora function"""
    freq_tag = {}
    with open(file, encoding = "utf8") as f:
        for line in f:
            freq = line.split()
            freq_tag[freq[0]] = []
            for i in range(1, len(freq), 2):
                f = freq[i].strip("(',)")
                freq_tag[freq[0]].append(f)
    return freq_tag

def get_standard_tag (filename, lang):
    """Get the standard tag. Create standard tag dictionary."""
    word_tag_dict = {}
    tag_dict = {}
    sentence_cnt = 1
    word_tag_dict[sentence_cnt] = {}
    tag_dict[sentence_cnt] = []
    word_position = 0
    print("get standard tag")
    with open(filename, encoding = "utf8") as f:
        for line in f:
            word_tag = line.split()
            if word_tag == []:
                sentence_cnt += 1
                word_position = 0
                word_tag_dict[sentence_cnt] = {}
                tag_dict[sentence_cnt] = []
                # wf.write("\n")
            else:
                tag_dict[sentence_cnt].append(word_tag[1])
                word_tag_dict[sentence_cnt][word_position] = [word_tag[0], word_tag[1]]
                word_position += 1
    return word_tag_dict, tag_dict

def get_alignment (filename, reverse ="False"):
    """Find the alignments between source language and target language. Create alignment dictionary."""
    align_dict = {}
    sentence_cnt = 1
    print("get alignment")
    with open(filename) as f:
        for line in f:
            sentence = line.split()
            align_dict[sentence_cnt] = {}
            for element in sentence:
                words = element.split('-')                      # words[1] is target position, words[0] is src position
                if reverse == "False":
                    if words[1] not in align_dict[sentence_cnt].keys():
                        align_dict[sentence_cnt][words[1]] = []
                    align_dict[sentence_cnt][words[1]].append(words[0])     # key (words[1]) is the target position
                else:
                    if words[0] not in align_dict[sentence_cnt].keys():
                        align_dict[sentence_cnt][words[0]] = []
                    align_dict[sentence_cnt][words[0]].append(words[1])     # key (words[0]) is the target position
            sentence_cnt += 1
    return align_dict

def get_source_tag (aligned_dict, src_word_tag_dict):
    """Get the aligned (source) tag for each word in each sentence of target language from a source language"""
    tar_tag_dict = {}		# create a dict to store predicted tag for tar language
    print("get source tag")
    for sentence_cnt in aligned_dict.keys():
        tar_tag_dict[sentence_cnt] = {}
        for tar_w_position in sorted(aligned_dict[sentence_cnt].keys()):
            source_position = aligned_dict[sentence_cnt][tar_w_position]
            if len(source_position) == 1:  # aligned word in source if only one alignment are found
                if sentence_cnt in src_word_tag_dict.keys() and source_position[0] in src_word_tag_dict[sentence_cnt].keys():
                    word, tag = src_word_tag_dict[sentence_cnt][int(source_position[0])]
                    tar_tag_dict[sentence_cnt][tar_w_position] = tag
                else:
                    print(sentence_cnt, source_position)
            else:     # aligned word in source if multiple alignments are found, the value is a list
                tagList1 = []
                for w in source_position:
                    word, tag = src_word_tag_dict[sentence_cnt][int(w)]
                    tagList1.append(tag)
                tar_tag_dict[sentence_cnt][tar_w_position] = tagList1
    return tar_tag_dict

def fix_alignment (src_tag_dict, standard_tag, lang):
    """Fix no alignment. Make the length of each sentence in source language the same as the target language.
    Then evaluate the performance easily."""

    print("fix alignment")
    with open(lang+".tag", "w") as f:
        for sentence in standard_tag.keys():
            for i in range(len(standard_tag[sentence])):
                if str(i) in src_tag_dict[sentence].keys():
                    tag = src_tag_dict[sentence][str(i)]
                    tag = str(tag)
                else:
                    tag = 'O'
                f.write(tag + "\n")
            f.write("\n")

def remove_prefix(element):
    """Remove the prefix (B/I-) from the tag of each token.
    The span of the named will be assigned later."""

    tagList = []
    if type(element) is not list:
        if element != "O":
            tagList.append(element[2:])
        else:
            tagList.append("O")
    else:
        for tag in element:
            if tag != "O":
                tagList.append(tag[2:])
            else:
                tagList.append("O")
    return tagList

def prediction (standardWordTag, src_tag_dict1, src_tag_dict2, src_tag_dict3, freq_tag):
    """Predict tags of target language by collecting all tags from three source languages"""
    final_predict = {}
    for sentence in sorted(src_tag_dict1.keys()):
        prediction_tag = list(zip_longest(src_tag_dict1[sentence], src_tag_dict2[sentence], src_tag_dict3[sentence]))
        final_predict[sentence] = []
        previous_tag = 'O'
        for index, element in enumerate(prediction_tag):
            t1 = remove_prefix(element[0])
            t2 = remove_prefix(element[1])
            t3 = remove_prefix(element[2])
            result = set(t1) & set(t2) & set(t3)

            word = standardWordTag[sentence][index][0]

            if len(result) > 1:    # more than 2 tags of 3 agreements found for one token, backoff to most frequent tag
                if word in freq_tag.keys() and len(freq_tag[word]) > 1:
                    tag = freq_tag[word][0]

                elif 'O' not in result:  # ORG/LOC/PER
                    t = result.pop()
                    if previous_tag[-1] != t[-1]:
                        tag = "B-"+ t
                    else:
                        tag = "I-" + t
                else:
                    tag = "O"
            elif len(result) == 1:      # only 1 tag of 3 agreements found for one token
                if 'O' not in result:
                    t = result.pop()
                    if previous_tag[-1] != t[-1]:
                        tag = "B-" + t
                    else:
                        tag = "I-" + t
                else:			    # "O"
                    tag = result.pop()
            elif set() == result:       # no agreement found or 2 agreements or more than 2 tags of 2 agreements found for one token
                tag = "O"
            final_predict[sentence].append(tag)
            previous_tag = tag
    return final_predict

def writeFile (standard, predict, targetlang):
    """Write predict tags and errors to two files"""
    print("writing")
    with open(targetlang+".tag", "w", encoding = "utf8") as f:
        for sent in predict.keys():
            if sent < 1380214:
                for i in range(len(standard[sent])):
                    word = standard[sent][i][0]
                    predictTag = predict[sent][i]
                    f.write(word+"\t"+predictTag+"\n")
                f.write("\n")

def get_align_tag(file):
    print("get align tag")
    final_tag = {}
    n = 1
    final_tag[n] = []
    with open(file) as f:
        for line in f:
            if line != '\n':
                if line.startswith("["):
                    a = line[1:-2]
                    b = a.split(",")
                    tagList = [e.strip().strip("'") for e in b]
                    final_tag[n].append(tagList)
                else:
                    final_tag[n].append(line.strip())
            else:
                n += 1
                final_tag[n] = []
    return final_tag

def projection(tarlanguage):
    if tarlanguage == "it":
        print("\nPredict it tag: ")

        # create back-off database
        read_freq_corpora(it_freq_corpora, "it", "wikiner")

        # get standard tag of target language
        it_src_wt_dict, it_src_tag_dict = get_standard_tag(it_standard_tag, "it")

        print("projection from es")
        es_src_wt_dict, es_src_tag_dict = get_standard_tag(es_standard_tag, "es")
        es_it_align_dict = get_alignment(es_it_alignment)
        es_it_tag_dict = get_source_tag(es_it_align_dict, es_src_wt_dict)
        fix_alignment(es_it_tag_dict, it_src_tag_dict, "es-it")

        print("projection from de")
        de_src_wt_dict, de_src_tag_dict = get_standard_tag(de_standard_tag, "de")
        de_it_align_dict = get_alignment(de_it_alignment)
        de_it_tag_dict = get_source_tag(de_it_align_dict, de_src_wt_dict)
        fix_alignment(de_it_tag_dict, it_src_tag_dict, "de-it")

        print("projection from en")
        en_src_wt_dict, en_src_tag_dict = get_standard_tag(en_standard_tag, "en")
        en_it_align_dict = get_alignment(en_it_alignment)
        en_it_tag_dict = get_source_tag(en_it_align_dict, en_src_wt_dict)
        fix_alignment(en_it_tag_dict, it_src_tag_dict, "en-it")

        it_freq = get_freq_tag(it_freq_tag, "it")
        it_src_wt_dict, it_src_tag_dict = get_standard_tag(it_standard_tag, "it")
        de_it_final = get_align_tag("de-it.tag")
        en_it_final = get_align_tag("en-it.tag")
        es_it_final = get_align_tag("es-it.tag")
        it_predict = prediction(it_src_wt_dict, de_it_final, en_it_final, es_it_final, it_freq)
        writeFile(it_src_wt_dict, it_predict, "it")

    elif tarlanguage == "es":
        print("\nPredict es tag: ")
        read_freq_corpora(es_freq_corpora, "es", "wikiner")
        es_src_wt_dict, es_src_tag_dict = get_standard_tag(es_standard_tag, "es")

        print("projection from de")
        de_src_wt_dict, de_src_tag_dict = get_standard_tag(de_standard_tag, "de")
        de_es_align_dict = get_alignment(de_es_alignment)
        de_es_tag_dict = get_source_tag(de_es_align_dict, de_src_wt_dict)
        fix_alignment(de_es_tag_dict, es_src_tag_dict, "de-es")

        print("projection from it")
        it_src_wt_dict, it_src_tag_dict = get_standard_tag(it_standard_tag, "it")
        it_es_align_dict = get_alignment(it_es_alignment, "True")
        it_es_tag_dict = get_source_tag(it_es_align_dict, it_src_wt_dict)
        fix_alignment(it_es_tag_dict, es_src_tag_dict, "it-es")

        print("projection from en")
        en_src_wt_dict, en_src_tag_dict = get_standard_tag(en_standard_tag, "en")
        en_es_align_dict = get_alignment(en_es_alignment)
        en_es_tag_dict = get_source_tag(en_es_align_dict, en_src_wt_dict)
        fix_alignment(en_es_tag_dict, es_src_tag_dict, "en-es")

        es_freq = get_freq_tag(es_freq_tag, "es")
        es_src_wt_dict, es_src_tag_dict = get_standard_tag(es_standard_tag, "es")
        de_es_final = get_align_tag("de-es.tag")
        en_es_final = get_align_tag("en-es.tag")
        it_es_final = get_align_tag("it-es.tag")
        es_predict = prediction(es_src_wt_dict, de_es_final, en_es_final, it_es_final, es_freq)
        writeFile(es_src_wt_dict, es_predict, "es")

    elif tarlanguage == "de":
        print("\nPredict de tag: ")
        read_freq_corpora(de_freq_corpora, "de", "wikiner")
        de_src_wt_dict, de_src_tag_dict = get_standard_tag(de_standard_tag, "de")

        print("projection from en")
        en_src_wt_dict, en_src_tag_dict = get_standard_tag(en_standard_tag, "en")
        en_de_align_dict = get_alignment(en_de_alignment)
        en_de_tag_dict = get_source_tag(en_de_align_dict, en_src_wt_dict)
        fix_alignment(en_de_tag_dict, de_src_tag_dict, "en-de")

        print("projection from it")
        it_src_wt_dict, it_src_tag_dict = get_standard_tag(it_standard_tag, "it")
        it_de_align_dict = get_alignment(it_de_alignment, "True")
        it_de_tag_dict = get_source_tag(it_de_align_dict, it_src_wt_dict)
        fix_alignment(it_de_tag_dict, de_src_tag_dict, "it-de")

        print("projection from es")
        es_src_wt_dict, es_src_tag_dict = get_standard_tag(es_standard_tag, "es")
        es_de_align_dict = get_alignment(es_de_alignment, "True")
        es_de_tag_dict = get_source_tag(es_de_align_dict, es_src_wt_dict)
        fix_alignment(es_de_tag_dict, de_src_tag_dict, "es-de")

        de_freq = get_freq_tag(de_freq_tag, "de")
        de_src_wt_dict, de_src_tag_dict = get_standard_tag(de_standard_tag, "de")
        en_de_final = get_align_tag("en-de.tag")
        it_de_final = get_align_tag("it-de.tag")
        es_de_final = get_align_tag("es-de.tag")
        de_predict = prediction(de_src_wt_dict, en_de_final, it_de_final, es_de_final, de_freq)
        writeFile(de_src_wt_dict, de_predict, "de")

    elif tarlanguage == "en":
        print("\nPredict en tag: ")
        read_freq_corpora(en_freq_corpora, "en", "wikiner")
        en_src_wt_dict, en_src_tag_dict = get_standard_tag(en_standard_tag, "en")

        print("projection from de")
        de_src_wt_dict, de_src_tag_dict = get_standard_tag(de_standard_tag, "de")
        de_en_align_dict = get_alignment(de_en_alignment, "True")
        de_en_tag_dict = get_source_tag(de_en_align_dict, de_src_wt_dict)
        fix_alignment(de_en_tag_dict, en_src_tag_dict, "de-en")

        print("projection from it")
        it_src_wt_dict, it_src_tag_dict = get_standard_tag(it_standard_tag, "it")
        it_en_align_dict = get_alignment(it_en_alignment, "True")
        it_en_tag_dict = get_source_tag(it_en_align_dict, it_src_wt_dict)
        fix_alignment(it_en_tag_dict, en_src_tag_dict, "it-en")

        print("projection from es")
        es_src_wt_dict, es_src_tag_dict = get_standard_tag(es_standard_tag, "es")
        es_en_align_dict = get_alignment(es_en_alignment, "True")
        es_en_tag_dict = get_source_tag(es_en_align_dict, es_src_wt_dict)
        fix_alignment(es_en_tag_dict, en_src_tag_dict, "es-en")

        en_freq = get_freq_tag(en_freq_tag, tarLanguage)
        en_src_wt_dict, en_src_tag_dict = get_standard_tag(en_standard_tag, "en")
        de_en_final = get_align_tag("de-en.tag")
        it_en_final = get_align_tag("it-en.tag")
        es_en_final = get_align_tag("es-en.tag")
        en_predict = prediction(en_src_wt_dict, de_en_final, it_en_final, es_en_final, en_freq)
        writeFile(en_src_wt_dict, en_predict, "en")

if __name__ == '__main__':
    tarLanguage = sys.argv[1]
    projection(tarLanguage)
