import glob                     # 디렉토리 내 파일을 얻기 위해 사용
import os                       # 디렉토리를 바꿔야 할 경우 사용
import datetime                 # date와 time을 얻기 위해 사용
import copy
from lxml.html import parse     # html양식으로 파싱
from io import StringIO         # 문자열 입출력 모듈
from xml.etree.ElementTree import Element, SubElement, dump, ElementTree

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def sourceRead(filePath):
    source = ''
    # web문서를 source(text문서)로 가져오기
    with open(filePath, mode="r") as f:
        while True:
            line = f.readline()
            if line is '':
                break
            else:
                source = source + line
    return source

def findTag(tagName, source):
    tag = []
    tempTag = []
    tempNum = 0
    # html 문서로 파싱(변환)
    source = StringIO(source)  # 문자열로 읽음
    parsed = parse(source)  # source -> html형식으로 파싱

    # root node 찾기
    doc = parsed.getroot()

    # doc.findall(".//태그")    # 찾고자 하는 태그명
    while True:
        if tempNum is len(tagName):
            break
        tempTag = doc.findall('.//'+tagName[tempNum])
        tag.append(tempTag)
        tempNum = tempNum + 1
    return tag

def clangParsing(tag):
    tempNum1 = 0
    while True:     # repeat as many as files
        tempNum2 = 0
        if tempNum1 is len(tag):
            break
        while True:
            if len(tag[tempNum1][0]) is 6:
                break
            if tempNum2 < 6:
                tempNum2 = tempNum2 + 1
            else:
                del(tag[tempNum1][0][tempNum2])
        tempNum1 = tempNum1 + 1

    tempNum1 = 0
    tempText3 = []
    tagText = []
    while True:     # repeat as many as files
        tempNum2 = 0
        tempText1 = []
        tempText2 = []
        if tempNum1 is len(tag):
            break
        tempText1 = tag[tempNum1][0][1].text    # tempText1 = file name
        tempText2.append(tempText1)

        tempText1 = (tag[tempNum1][1][0].text).split(',')
        tempText1 = tempText1[0].replace('line ', '')    # tempText1 = error location
        tempText2.append(tempText1)

        tempText1 = tag[tempNum1][0][5].text    # tempText1 = error content
        tempText2.append(tempText1)

        tagText.append(tempText2)

        tempNum1 = tempNum1 + 1
    tempNum3 = 0
    while True:
        if tempNum3 is len(tagText):
            break
        tagText[tempNum3].append('clang_result')
        tempNum3 = tempNum3 + 1
    return tagText

def flawfinderParsing(tag):
    tempNum1 = 0
    tempNum2 = 0
    tempNum3 = 0
    tempText = []
    tagText = []
    while True:
        if tempNum1 is len(tag[0]):
            break
        tempText = (tag[0][tempNum1].text).split('./')
        tempText = tempText[1].split(':')
        del tempText[2]
        tagText.append(tempText)
        tempNum1 = tempNum1 + 1
    while True:
        if tempNum2 is len(tag[1]):
            break
        tagText[tempNum2].append(tag[1][tempNum2].text)
        tempNum2 = tempNum2 + 1
    while True:
        if tempNum3 is len(tagText):
            break
        tagText[tempNum3].append('flawfinder_result')
        tempNum3 = tempNum3 + 1
    return tagText

def clang_to_tag(tagText, nowDate):
    tagNum = 0
    clang = Element("clang")
    clang.attrib["result"] = nowDate
    while True:
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        clang.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, "Description").text = tagText[tagNum][2]
        tagNum = tagNum + 1
        if tagNum is len(tagText):
            break
    indent(clang)
    # dump(clang)
    return clang

def flawfinderResult_to_tag(tagText, nowDate):
    tagNum = 0
    flawfinder = Element("flawfinder")
    flawfinder.attrib["result"] = nowDate
    while True:
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        flawfinder.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, "Description").text = tagText[tagNum][2]
        tagNum = tagNum + 1
        if tagNum is len(tagText):
            break
    indent(flawfinder)
    # dump(flawfinder)
    return flawfinder

def makeTag(tagText, nowDate):
    tagNum = 0
    code_analysis = Element("code_analysis")
    code_analysis.attrib["result"] = nowDate
    while True:
        if tagNum is len(tagText):
            break
        error = Element("error")
        error.attrib["File"] = tagText[tagNum][0]
        code_analysis.append(error)
        SubElement(error, "Location").text = "line " + tagText[tagNum][1]
        SubElement(error, tagText[tagNum][3]).text = tagText[tagNum][2]
        if len(tagText[tagNum]) > 4:
            for i in range(4, len(tagText[tagNum])-4, 1):
                SubElement(error, tagText[tagNum][3]).text = tagText[tagNum][i]
        tagNum = tagNum + 1
    indent(code_analysis)
    dump(code_analysis)
    return code_analysis

def bubbleSort(tagText):
    sort_tagText = copy.deepcopy(tagText)
    for i in range(0, len(tagText)-1, 1):
        for j in range(1, len(tagText)-i, 1):
            if int(sort_tagText[j-1][1]) > int(sort_tagText[j][1]):
                sort_tagText[j-1], sort_tagText[j] = sort_tagText[j], sort_tagText[j-1]
    return sort_tagText

def sort_filename(tagText):
    sort_tagText = []
    tempText1 = []
    tempText2 = []
    sort_tagText.append(tagText[0])
    for i in range(1, len(tagText), 1):
        if tagText[0][0] == tagText[i][0]:
            tempText1.append(tagText[i])
        else:
            tempText2.append(tagText[i])
    sort_tagText = sort_tagText + tempText1
    sort_tagText = sort_tagText + tempText2
    return sort_tagText

def sort_errors(tagText1, tagText2):
    sort_tagText = copy.deepcopy(tagText2)
    tempNum1 = 0
    tof = True
    while True:
        if tempNum1 is len(tagText1):
            break
        tempNum2 = 0
        while True:
            if tempNum2 is len(tagText2):
                break
            if tagText1[tempNum1][0] == tagText2[tempNum2][0]:
                if tagText1[tempNum1][1] == tagText2[tempNum2][0]:
                    sort_tagText[tempNum1].append(tagText1[tempNum1][2])
                    sort_tagText[tempNum1][3] = tagText2[tempNum1][3] + tagText1[tempNum1][3]
                    tof = True
                else:
                    tof = False
            else:
                tof = False
            tempNum2 = tempNum2 + 1
        if tof is False:
            sort_tagText.append(tagText1[tempNum1])
        tempNum1 = tempNum1 + 1
    sort_tagText = bubbleSort(sort_tagText)
    sort_tagText = sort_filename(sort_tagText)
    return sort_tagText




# nowDatatime에 datetime정보 저장
now = datetime.datetime.now()
nowDatetime = now.strftime('%Y%m%d-%H_%M/')
nowDate = now.strftime('%Y%m%d-%H%M')

# clangfolderName에 폴더명 저장
# clang_folderName = 'clangResult-' + nowDatetime
clang_folderName = 'clangResult'
# flawfinderfileName에 파일명 저장
flawfinder_fileName = 'flawfinder.html'

## clang_filePath에 html파일이 있는 경로 저장
clang_filePath = '/var/lib/jenkins/workspace/testCWE/' + clang_folderName
os.chdir(clang_filePath) # 디렉토리를 바꿔야 할 경우에만 쓰세요
clang_fileList = []
for clang_file in glob.glob("report-*.html"): # '*'은 모든 값을 의미
    clang_fileList.append(clang_filePath+clang_file)
## flawfinder_filePath에 html파일이 있는 경로 저장
flawfinder_filePath = '/var/lib/jenkins/workspace/testCWE/' + flawfinder_fileName

clang_tagName = ['td', 'a']
flawfinder_tagName = ['li', 'i']
tempTag = []
clang_tag = []
clang_tagText = []
clang_source = []
flawfinder_tag = []
flawfinder_tagText = []
sort_tagText = []
tempSource = ''
flawfinder_source = ''

tempNum = 0
while True:
    if tempNum is len(clang_fileList):
        break
    tempSource = sourceRead(clang_fileList[tempNum])
    clang_source.append(tempSource)
    tempNum = tempNum + 1

tempNum = 0
while True:
    if tempNum is len(clang_source):
        break
    tempTag = findTag(clang_tagName, clang_source[tempNum])
    clang_tag.append(tempTag)
    tempNum = tempNum + 1

clang_tagText = clangParsing(clang_tag)

flawfinder_source = sourceRead(flawfinder_filePath)
flawfinder_tag = findTag(flawfinder_tagName, flawfinder_source)
flawfinder_tagText = flawfinderParsing(flawfinder_tag)

sort_tagText = sort_errors(clang_tagText, flawfinder_tagText)
# print(sort_tagText)

codeAnalysis = Element('codeAnalysis')
codeAnalysis.attrib['result'] = nowDate
code_analysis = Element
code_analysis = makeTag(sort_tagText, nowDate)
codeAnalysis.append(code_analysis)

ElementTree(codeAnalysis).write('/var/lib/jenkins/workspace/testCWE/codeAnalysis-' + nowDate + '.xml')