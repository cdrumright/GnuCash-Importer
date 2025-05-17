import csv  # for reading from the csv file
from piecash import open_book, Transaction, Split
from datetime import datetime, date
from decimal import Decimal
import re
import sys
import os.path
import warnings
from sqlalchemy import exc as sa_exc

def findDuplicate(dupeBook, dupeTransaction):
    for dupeSplit in dupeTransaction["splits"]:
        for accountSplit in dupeSplit.account.splits:
            # print(accountSplit.account.description)
            # print(dupeTransaction["description"])
            if (
                accountSplit.transaction.description == dupeTransaction["description"] and
                accountSplit.transaction.post_date == dupeTransaction["post_date"] and
                accountSplit.value == dupeSplit.value
               ):
                print(accountSplit.transaction)
                return True
            else:
                print("false")

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=sa_exc.SAWarning)

    for arg in sys.argv:
        if ".csv" in arg:
            if os.path.isfile(arg):
                importPath = arg  # path to csv file
        if ".gnucash" in arg:
            if os.path.isfile(arg):
                targetFile = arg
    
    rulePath = os.path.splitext(importPath)[0] + ".rules"
    
    # configs
    # amountSymbols = ["+","-",",",".","(",")","0","1","2","3","4","5","6","7","8","9"]
    amountSymbols = "+-,.()0123456789"
    
    # set  the rules file to open
    # rulePath = "test.rules"  # path of rules file
    # importPath = "test.csv"  # path to csv file
    # targetFile = "test.gnucash"  # path to gnucash file
    
    # open rules file and read in lines to an array
    ruleLines = []
    with open(rulePath, mode='r') as rulesFile:
        ruleLines = rulesFile.readlines()  # read lines from rules file
    
    # precheck rules for things like source file
    for line in ruleLines:
        words = line.split()
    
        if not words:
            continue  # empty line, skip
        if words[0][0] == "#":
            continue  # first character of the first word is a hashtag, skip
    
    # open csv file
    with open(importPath, 'r') as importFile:
        csvReader = csv.reader(importFile)
        # don't need to read headers since we use a rules file to skip headers
    
        importedCount = 0
        # for each line in csv file check rules for match
        for row in csvReader:
            skipRow = False
            ifRule = False
            for line in ruleLines:
                words = line.split()  # read line into words array
    
                # check if currently inside an if block
                if ifRule:
                    # check if empty line: exit
                    if not words:
                        ifRule = False
                        continue
                    # check if first space is empty: rule
                    if line.startswith(' '):
                        # check if matchers were true and apply rule
                        if isTrue:
                            # add check for the word skip and skip the row
    
                            # get string after first word
                            valueString = line[len(words[0]) + 1:].strip()
                            # for variables in fieldRules if instring replace with value
                            for rule in fieldRules:
                                if "%" + rule in valueString:
                                    valueString = valueString.replace("%" + rule, fieldRules[rule])
    
                            # use regex to find %[1-9] and replace with row index
                            replaceList = re.findall("%\\d+", valueString)
                            for reString in replaceList:
                                valueString = valueString.replace(reString, row[int(reString[1:])])
    
                            # set field equal to updated string
                            fieldRules[words[0]] = valueString
                    # what's left must be a matcher
                    else:
                        if skipMatchers:
                            # no need to evaluate, next line
                            continue
                        # check if first character is &, and with previous line
                        if line.startswith('&'):
                            # check if group is true, add current matcher
                            if isTrue:
                                # evaluate matcher and add with previous
                                # if && found split the matchers into array
                                matchers = [x.strip() for x in line[2:].split('&&')]
                                # evaluate each matcher and and it with the previous matcher
                                matchState = True
                                for matcher in matchers:
                                    # if ! found shave off and set not flag
                                    notRule = False
                                    if matcher[0] == "!":
                                        notRule = True
                                        matcher = matcher[1:].strip()
                                    # if % found take first word as field and leave the rest as match string
                                    if matcher[0] == "%":
                                        # separate the first word and the rest of the string
                                        (searchField, matchString) = [x.strip() for x in matcher.split(maxsplit=1)]
                                        # replace search field with field value
                                        valueString = searchField
                                        # for variables in fieldRules if instring replace with value
                                        for rule in fieldRules:
                                            if "%" + rule in valueString:
                                                valueString = valueString.replace("%" + rule, fieldRules[rule])
    
                                        # use regex to find %[1-9] and replace with row index
                                        replaceList = re.findall("%\\d+", valueString)
                                        for reString in replaceList:
                                            valueString = valueString.replace(reString, row[int(reString[1:])])
                                        # check if matchString in valueString and set false if not unless not
                                        if (not (matchString in valueString)) ^ notRule:
                                            matchState = False
                                    else:
                                        # check if matcher exists in whole row
                                        inRow = False
                                        for cell in row:
                                            if matcher in cell:
                                                inRow = True
                                        if (not inRow) ^ notRule:
                                            matchState = False
                                # if the whole row is true set isTrue
                                if not matchState:
                                    isTrue = False
                            else:
                                # previous current andGroup is false, skip this line
                                continue
                        else:
                            # current group is or, check if previous group was true
                            if isTrue:
                                # prvious group was true, no need to check any more
                                skipMatchers = True
                            else:
                                # starting new group, evaluate matcher
                                # if && found split the matchers into array
                                matchers = [x.strip() for x in line[2:].split('&&')]
                                # evaluate each matcher and and it with the previous matcher
                                matchState = True
                                for matcher in matchers:
                                    # if ! found shave off and set not flag
                                    notRule = False
                                    if matcher[0] == "!":
                                        notRule = True
                                        matcher = matcher[1:].strip()
                                    # if % found take first word as field and leave the rest as match string
                                    if matcher[0] == "%":
                                        # separate the first word and the rest of the string
                                        (searchField, matchString) = [x.strip() for x in matcher.split(maxsplit=1)]
                                        # replace search field with field value
                                        valueString = searchField
                                        # for variables in fieldRules if instring replace with value
                                        for rule in fieldRules:
                                            if "%" + rule in valueString:
                                                valueString = valueString.replace("%" + rule, fieldRules[rule])
    
                                        # use regex to find %[1-9] and replace with row index
                                        replaceList = re.findall("%\\d+", valueString)
                                        for reString in replaceList:
                                            valueString = valueString.replace(reString, row[int(reString[1:])])
                                        # check if matchString in valueString and set false if not unless not
                                        if (not (matchString in valueString)) ^ notRule:
                                            matchState = False
                                    else:
                                        # check if matcher exists in whole row
                                        inRow = False
                                        for cell in row:
                                            if matcher in cell:
                                                inRow = True
                                        if (not inRow) ^ notRule:
                                            matchState = False
                                # if the whole row is true set isTrue
                                if matchState:
                                    isTrue = True
                elif not words:
                    continue  # empty line, skip
                elif words[0][0] == "#":
                    continue  # first character of the first word is a hashtag, skip
                elif words[0] == "skip":  # set number of header lines to skip
                    skipLines = int(words[1])  # convert number of lines to skip to int
                    if csvReader.line_num <= skipLines:
                        skipRow = True
                        break  # break out of for loop and skip this in the csv
                elif words[0] == "date-format":  # set date format
                    dateFormat = line[12:].strip()  # save everything after the space
                elif words[0] == "fields":  # set field mappings
                    fields = [x.strip() for x in line[6:].split(',')]
                    fieldRules = {}
                    for index, field in enumerate(fields):
                        # map field positions to dictionary
                        if field:
                            fieldRules[field] = row[index]
                    # map fields to an array or dictionary
    
                # need to check for case insesitivity ?
    
                # check for if rule
                elif words[0] == "if":
                    # set if flag because next line is either matcher or rule
                    ifRule = True
                    isTrue = False
                    skipMatchers = False
    
                    # check if any text after if string
                    if words[1]:
                        # if && found split the matchers into array
                        matchers = [x.strip() for x in line[2:].split('&&')]
                        # evaluate each matcher and and it with the previous matcher
                        matchState = True
                        for matcher in matchers:
                            # if ! found shave off and set not flag
                            notRule = False
                            if matcher[0] == "!":
                                notRule = True
                                matcher = matcher[1:].strip()
                            # if % found take first word as field and leave the rest as match string
                            if matcher[0] == "%":
                                # separate the first word and the rest of the string
                                (searchField, matchString) = [x.strip() for x in matcher.split(maxsplit=1)]
                                # replace search field with field value
                                valueString = searchField
                                # for variables in fieldRules if instring replace with value
                                for rule in fieldRules:
                                    if "%" + rule in valueString:
                                        valueString = valueString.replace("%" + rule, fieldRules[rule])
    
                                # use regex to find %[1-9] and replace with row index
                                replaceList = re.findall("%\\d+", valueString)
                                for reString in replaceList:
                                    valueString = valueString.replace(reString, row[int(reString[1:])])
                                # check if matchString in valueString and set false if not unless not
                                if (not (matchString in valueString)) ^ notRule:
                                    matchState = False
                            else:
                                # check if matcher exists in whole row
                                inRow = False
                                for cell in row:
                                    if matcher in cell:
                                        inRow = True
                                if (not inRow) ^ notRule:
                                    matchState = False
                        # if the whole row is true set isTrue
                        if matchState:
                            isTrue = True
                else:
                    # not caught by any other keys so must be setting a field
                    # get string after first word
                    valueString = line[len(words[0]):].strip()
                    # for variables in fieldRules if instring replace with value
                    for rule in fieldRules:
                        if "%" + rule in valueString:
                            valueString = valueString.replace("%" + rule, fieldRules[rule])
    
                    # use regex to find %[1-9] and replace with row index
                    replaceList = re.findall("%\\d+", valueString)
                    for reString in replaceList:
                        valueString = valueString.replace(reString, row[int(reString[1:])])
    
                    # set field equal to updated string
                    fieldRules[words[0]] = valueString
            if skipRow:
                continue  # skip this csv row
    
            # fields should be set, build transaction
            # open the book
            with open_book(targetFile,
                           open_if_lock=True,
                           readonly=False) as mybook:
                today = datetime.now()
                # retrieve the currency from the book
                USD = mybook.currencies(mnemonic="USD")
                splits = []
                # retrieve accounts, need to loop through accounts1-99
                for n in range(1, 100):
                    if "account" + str(n) in fieldRules:
                        # strip currency and junk
                        strippedAmount = ''.join(c for c in fieldRules["amount" + str(n)] if c in amountSymbols)
                        # replace parenthasis with negative symbol
                        strippedAmount = strippedAmount.replace("(", "-")
                        strippedAmount = strippedAmount.replace(")", "")
                        if strippedAmount.count("-") > 1:
                            # check if even or odd and replace with one or none
                            if strippedAmount.count("-") % 2 == 0:
                                # even, remove negatives
                                strippedAmount = strippedAmount.replace("-", '')
                            else:
                                # odd, leave 1 negative
                                strippedAmount = strippedAmount.replace("-", '')
                                strippedAmount = "-" + strippedAmount
    
                        # account exists, build split
                        splits.append(Split(account=mybook.accounts(fullname=fieldRules["account" + str(n)]),
                                            value=Decimal(strippedAmount)))
                transaction=dict(
                    post_date=datetime.strptime(fieldRules["date"], dateFormat).date(),
                    enter_date=today,
                    currency=USD,
                    description=fieldRules["description"],
                    splits=splits)
                duplicate = findDuplicate(mybook, transaction)

                # build transaction
                Transaction(
                    post_date=datetime.strptime(fieldRules["date"], dateFormat).date(),
                    enter_date=today,
                    currency=USD,
                    description=fieldRules["description"],
                    splits=splits)
                # save the book
                mybook.save()

                importedCount = importedCount + 1
        print("Imported " + str(importedCount) + " transactions")
    
    
