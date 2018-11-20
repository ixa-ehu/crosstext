#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import Counter
from itertools import *

de_en_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-de.grow-diag-final.alignment'
es_en_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-es.grow-diag-final.alignment'
it_en_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-it.grow-diag-final.alignment'
de_it_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/de-it.grow-diag-final.alignment'
es_it_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/es-it.grow-diag-final.alignment'
en_it_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-it.grow-diag-final.alignment'
en_es_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-es.grow-diag-final.alignment'
de_es_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/de-es.grow-diag-final.alignment'
it_es_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/es-it.grow-diag-final.alignment'
en_de_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/en-de.grow-diag-final.alignment'
es_de_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/de-es.grow-diag-final.alignment'
it_de_alignment = '/tartalo03/users/crosstext/europarl/test/alignments/de-it.grow-diag-final.alignment'

en_standard_tag = '/tartalo03/users/crosstext/europarl/test/en-europarl.test.conll02'
es_standard_tag = "/tartalo03/users/crosstext/europarl/test/es-europarl.test.conll02"
it_standard_tag = "/tartalo03/users/crosstext/europarl/test/it-europarl.test.conll02"
de_standard_tag = "/tartalo03/users/crosstext/europarl/test/de-europarl.test.conll02"

def get_standard_tag (filename, lang):
    """Get the standard tag. Create standard tag dictionary."""
    word_tag_dict = {}
    tag_dict = {}
    sentence_cnt = 1
    word_tag_dict[sentence_cnt] = {}
    tag_dict[sentence_cnt] = []
    word_position = 0
    sentence_dict = {}
    sentence_dict[sentence_cnt] = []
    print("get standard tag")
    with open(filename, encoding = "utf8") as f:
        for line in f:
            word_tag = line.split()     # word_tag[0] is the word, word_tag[1] is the tag of the word
            if word_tag == []:
                sentence_cnt += 1
                word_position = 0
                word_tag_dict[sentence_cnt] = {}
                tag_dict[sentence_cnt] = []
                sentence_dict[sentence_cnt] = []
            else:
                tag_dict[sentence_cnt].append(word_tag[1])
                sentence_dict[sentence_cnt].append(word_tag[0])
                word_tag_dict[sentence_cnt][word_position] = [word_tag[0], word_tag[1]]
                word_position += 1
    return word_tag_dict, tag_dict, sentence_dict

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
                words = element.split('-')                       # words[1] is tar position, words[0] is src position
                if reverse == "False":
                    if words[1] not in align_dict[sentence_cnt].keys():
                        align_dict[sentence_cnt][words[1]] = []
                    align_dict[sentence_cnt][words[1]].append(words[0])     # key (words[1]) is the tar position
                else:
                    if words[0] not in align_dict[sentence_cnt].keys():
                        align_dict[sentence_cnt][words[0]] = []
                    align_dict[sentence_cnt][words[0]].append(words[1])     # key (words[0]) is the tar position
            sentence_cnt += 1
    return align_dict

def get_source_tag (aligned_dict, src_word_tag_dict):
    """Get the aligned (source) tag for each word in each sentence of target language from a source language"""
    tar_tag_dict = {}		# create a dict to store predicted tag for tar language
    print("get source")
    for sentence_cnt in aligned_dict.keys():
        tar_tag_dict[sentence_cnt] = {}
        for tar_w_position in sorted(aligned_dict[sentence_cnt].keys()):
            source_position = aligned_dict[sentence_cnt][tar_w_position]
            if len(source_position) == 1:  # aligned word in source if only one alignment are found
                if sentence_cnt in src_word_tag_dict.keys() and int(source_position[0]) in src_word_tag_dict[sentence_cnt].keys():
                    word, tag = src_word_tag_dict[sentence_cnt][int(source_position[0])]
                    tar_tag_dict[sentence_cnt][tar_w_position] = tag

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

    final_tag = {}
    for sentence in src_tag_dict.keys():
        final_tag[sentence] = []
        for i in range(len(standard_tag[sentence])):
            if str(i) in src_tag_dict[sentence].keys():
                tag = src_tag_dict[sentence][str(i)]
                final_tag[sentence].append(tag)
            else:
                final_tag[sentence].append('O')  # when no alignment
    return final_tag

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

def prediction (standardWordTag, src_tag_dict1, src_tag_dict2, src_tag_dict3):
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

            if len(result) == 1:      # only 1 tag of 3 agreements found for one token
                if 'O' not in result:
                    t = result.pop()
                    if previous_tag[-1] != t[-1]:
                        tag = "B-" + t
                    else:
                        tag = "I-" + t
                else:			    # "O"
                    tag = result.pop()
            else:
                tag = 'O'
                standardWordTag[sentence][index] = 'O'
            final_predict[sentence].append(tag)
            previous_tag = tag
    return final_predict, standardWordTag

def writeRandE (ali1, ali2, ali3, sentence, sent1, sent2, sent3, standard, predict, targetlang, tar_tag_dict1, tar_tag_dict2, tar_tag_dict3, src):
    """write predict tags and errors to two files"""
    print("writing")
    with open(targetlang+".tag", "w", encoding = "utf8") as f:
        for sent in predict.keys():
            if sent < 1380214:
                for i in range(len(standard[sent])):
                    word = sentence[sent][i]
                    standardTag = standard[sent][i]
                    predictTag = predict[sent][i]
                    f.write(word + " " + standardTag + " " + predictTag+"\n")
    sentlist = [sent for sent in predict.keys() if sent < 1380214 for i, j in zip(predict[sent], standard[sent]) if i != j]

    # For error analysis: Output the sentences and tags where the prediction is different from gold-standard
    with open(targetlang + ".error", "w") as f:
        f.write("target: "+targetlang+"  .  "+"source sequence: "+src + "\n")
        for sent in sorted(set(sentlist)):
            index = -1
            f.write("******************************************************************"+"\n")
            f.write(str(sent) + ". " + ' '.join(sentence[sent]) + "\n")  # print tar sentence that contains wrong tag
            f.write(' '.join(sent1[sent]) + "\n")  # print src1 sentence that contains wrong tag
            f.write(' '.join(sent2[sent]) + "\n")  # print src2 sentence that contains wrong tag
            f.write(' '.join(sent3[sent]) + "\n")  # print src3 sentence that contains wrong tag
            f.write("\n")
            for i, j in zip(predict[sent], standard[sent]):
                index += 1      # word index in each sentence
                if i != j:
                    a1 = "None"
                    a2 = "None"
                    a3 = "None"
                    t1 = tar_tag_dict1[sent][index]
                    t2 = tar_tag_dict2[sent][index]
                    t3 = tar_tag_dict3[sent][index]
                    if str(index) in ali1[sent].keys():
                        a1 = ali1[sent][str(index)]
                    if str(index) in ali2[sent].keys():
                        a2 = ali2[sent][str(index)]
                    if str(index) in ali3[sent].keys():
                        a3 = ali3[sent][str(index)]
                    f.write(sentence[sent][index] + " " + j + " " + i + "  .  " + ','.join(t1) + " ; " + ','.join(t2) + " ; " +','.join(t3)  + "  .  " +
                        "alignment in source language: " + ','.join(a1) + " ; " + ','.join(a2) + " ; " + ','.join(a3) + "\n")

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
    it_src_wt_dict, it_src_tag_dict, it_sen_tag = get_standard_tag(it_standard_tag, "it")
    es_src_wt_dict, es_src_tag_dict, es_sen_tag = get_standard_tag(es_standard_tag, "es")
    de_src_wt_dict, de_src_tag_dict, de_sen_tag = get_standard_tag(de_standard_tag, "de")
    en_src_wt_dict, en_src_tag_dict, en_sen_tag = get_standard_tag(en_standard_tag, "en")

    if tarlanguage == "it":
        print("\nPredict it tag: ")
        print("from es")
        es_it_align_dict = get_alignment(es_it_alignment)
        es_it_tag_dict = get_source_tag(es_it_align_dict, es_src_wt_dict)
        es_it_final = fix_alignment(es_it_tag_dict, it_src_tag_dict, "es-it")

        print("from de")
        de_it_align_dict = get_alignment(de_it_alignment)
        de_it_tag_dict = get_source_tag(de_it_align_dict, de_src_wt_dict)
        de_it_final = fix_alignment(de_it_tag_dict, it_src_tag_dict, "de-it")

        print("from en")
        en_it_align_dict = get_alignment(en_it_alignment)
        en_it_tag_dict = get_source_tag(en_it_align_dict, en_src_wt_dict)
        en_it_final = fix_alignment(en_it_tag_dict, it_src_tag_dict, "en-it")

        it_predict, it_standWordTag = prediction(it_src_tag_dict, es_it_final, de_it_final, en_it_final)
        writeRandE(de_it_align_dict, es_it_align_dict, en_it_align_dict, it_sen_tag, de_sen_tag, es_sen_tag, en_sen_tag, it_standWordTag, it_predict, "it", de_it_final, es_it_final, en_it_final, "de ; es ; en")

    elif tarlanguage == "es":
        print("\nPredict es tag: ")

        print("from de")
        de_es_align_dict = get_alignment(de_es_alignment)
        de_es_tag_dict = get_source_tag(de_es_align_dict, de_src_wt_dict)
        de_es_final = fix_alignment(de_es_tag_dict, es_src_tag_dict, "de-es")

        print("from it")
        it_es_align_dict = get_alignment(it_es_alignment, "True")
        it_es_tag_dict = get_source_tag(it_es_align_dict, it_src_wt_dict)
        it_es_final = fix_alignment(it_es_tag_dict, es_src_tag_dict, "it-es")

        print("from en")
        en_es_align_dict = get_alignment(en_es_alignment)
        en_es_tag_dict = get_source_tag(en_es_align_dict, en_src_wt_dict)
        en_es_final = fix_alignment(en_es_tag_dict, es_src_tag_dict, "en-es")

        es_predict, es_standWordTag = prediction(es_src_tag_dict, de_es_final, it_es_final, en_es_final)
        writeRandE(de_es_align_dict, it_es_align_dict, en_es_align_dict, es_sen_tag, de_sen_tag, it_sen_tag, en_sen_tag,
                   es_standWordTag, es_predict, "es", de_es_final, it_es_final, en_es_final, "de ; it ; en")

    elif tarlanguage == "de":
        print("\nPredict de tag: ")

        print("from en")
        en_de_align_dict = get_alignment(en_de_alignment)
        en_de_tag_dict = get_source_tag(en_de_align_dict, en_src_wt_dict)
        en_de_final = fix_alignment(en_de_tag_dict, de_src_tag_dict, "en-de")

        print("from it")
        it_de_align_dict = get_alignment(it_de_alignment, "True")
        it_de_tag_dict = get_source_tag(it_de_align_dict, it_src_wt_dict)
        it_de_final = fix_alignment(it_de_tag_dict, de_src_tag_dict, "it-de")

        print("from es")
        es_de_align_dict = get_alignment(es_de_alignment, "True")
        es_de_tag_dict = get_source_tag(es_de_align_dict, es_src_wt_dict)
        es_de_final = fix_alignment(es_de_tag_dict, de_src_tag_dict, "es-de")

        de_predict, de_standWordTag = prediction(de_src_tag_dict, en_de_final, it_de_final, es_de_final)
        writeRandE(it_de_align_dict, es_de_align_dict, en_de_align_dict, de_sen_tag, it_sen_tag, es_sen_tag, en_sen_tag,
                   de_standWordTag, de_predict, "de", it_de_final, es_de_final, en_de_final, "it ; es ; en")

    elif tarlanguage == "en":
        print("\nPredict en tag: ")

        print("from de")
        de_en_align_dict = get_alignment(de_en_alignment, "True")
        de_en_tag_dict = get_source_tag(de_en_align_dict, de_src_wt_dict)
        de_en_final = fix_alignment(de_en_tag_dict, en_src_tag_dict, "de-en")

        print("from it")
        it_en_align_dict = get_alignment(it_en_alignment, "True")
        it_en_tag_dict = get_source_tag(it_en_align_dict, it_src_wt_dict)
        it_en_final = fix_alignment(it_en_tag_dict, en_src_tag_dict, "it-en")

        print("from es")
        es_en_align_dict = get_alignment(es_en_alignment, "True")
        es_en_tag_dict = get_source_tag(es_en_align_dict, es_src_wt_dict)
        es_en_final = fix_alignment(es_en_tag_dict, en_src_tag_dict, "es-en")

        en_predict, en_standWordTag = prediction(en_src_tag_dict, de_en_final, it_en_final, es_en_final)
        writeRandE(de_en_align_dict, es_en_align_dict, it_en_align_dict, en_sen_tag, de_sen_tag, es_sen_tag, it_sen_tag,
                   en_standWordTag, en_predict, "en", de_en_final, es_en_final, it_en_final, "de ; es ; it")

if __name__ == '__main__':
    tarLanguage = sys.argv[1]
    projection(tarLanguage)
