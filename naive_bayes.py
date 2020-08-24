# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 08:31:01 2020

@author: Jerry
"""
import re
import random
from math import log,exp
from collections import defaultdict


def read_file(filepath="SMSSpamCollection.txt"):
    """
    :return mails: 訊息列表
    """
    mails = []
    with open(filepath,encoding="utf-8") as file:
        for line in file.readlines():
            is_spam,message = line.split("\t")
            is_spam = 1 if is_spam=="spam" else 0
            message = message.strip()
            mails.append((message,is_spam))
    return mails

class NaiveBayesClassifier():
    def __init__(self, k = 1):
        self.k = k  # smoothing factor
        self.class_count_ = [0,0] 
        self.word_count_ = defaultdict(lambda :[0,0])
        self.word_prob_ = defaultdict(lambda :[0,0])
        
    def tokenize(self,message):
        message = message.lower()                      
        all_words = re.findall("[a-z]+", message) 
        return set(all_words)
    
    def train(self,messages,spam_or_not):
        """
        messages:訊息文本
        spam_or_not:是否為垃圾訊息
        """
        #1-計算各類別次數、單詞在各類別的次數
        for message,is_spam in zip(messages,spam_or_not):
            for word in self.tokenize(message):
                self.word_count_[word][is_spam] += 1
            self.class_count_[is_spam] += 1 
            
        #2-計算單詞在各類別條件下的條件機率 (單詞出現次數/類別出現次數)
        for word,count in self.word_count_.items():
            word_prob_if_spam = (self.k+count[1])/(2*self.k+self.class_count_[1])
            word_prob_if_non_spam = (self.k+count[0])/(2*self.k+self.class_count_[0])
            
            self.word_prob_[word][1] = word_prob_if_spam
            self.word_prob_[word][0] = word_prob_if_non_spam

    
    def predict_proba(self,message):
        log_prob_if_spam = 0
        log_prob_if_non_spam = 0
        
        all_words = self.tokenize(message)
        for word,word_prob in self.word_prob_.items():
            if word in all_words:
                log_prob_if_spam += log(word_prob[1])
                log_prob_if_non_spam += log(word_prob[0])
                
            else:
                log_prob_if_spam += log(1-word_prob[1])
                log_prob_if_non_spam += log(1-word_prob[0])
        
        prob_if_spam = exp(log_prob_if_spam)
        prob_if_non_spam = exp(log_prob_if_non_spam )
        return prob_if_spam/(prob_if_spam+prob_if_non_spam)
    
    def predict(self,message):
        return 1 if self.predict_proba(message)>0.5 else 0

def confusion_matrix(y_true,y_pred):
    tn, fp, fn, tp = 0,0,0,0
    for actual,prediction in zip(y_true,y_pred):
        
        if (actual==0 and prediction==0):
           tn +=1
        elif(actual==0 and prediction==1):
            fp += 1
        elif(actual==1 and prediction==0):
            fn += 1
        else:
            tp += 1
    return  tn, fp, fn, tp

def split_data(mails,ratio=0.8):
    random.shuffle(mails)
    train_num  = round(0.8*len(mails))
    train_X = [ mail[0] for mail in mails[:train_num]]
    train_y = [ mail[1] for mail in mails[:train_num]]

    test_X = [ mail[0] for mail in mails[train_num:]]
    test_y = [ mail[1] for mail in mails[train_num:]]
    return (train_X,train_y,test_X,test_y)
   
mails = read_file()
train_X,train_y, test_X,test_y = split_data(mails)
nb = NaiveBayesClassifier()
nb.train(train_X,train_y)
y_pred = []
for x in test_X:
    y_pred.append(nb.predict(x))

tn, fp, fn, tp = confusion_matrix(test_y,y_pred)
print(tn, fp, fn, tp)
print((tn+tp)/(fp+fn+tn+tp))



