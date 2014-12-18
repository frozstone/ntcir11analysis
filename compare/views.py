from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from os import path
from collections import OrderedDict
from xml.dom import minidom

# Create your views here.
queryfile = 'NTCIR_2014_topic/NTCIR11-Math2-queries-participants.xml'
dataPath = '/Users/giovanni/working/ntcir11/ntcir11-analysis/data/'
qrelfile = 'NTCIR_2014_results/MCAT/result_judge/NTCIR11_Math-qrels.dat'
submfile = 'NTCIR_2014_results/MCAT/result_submit/MCAT_all.tsv'
htmlDir = '/Users/giovanni/working/ntcir11/ntcir11-analysis/data/xhtmls/'

#queryfile = 'NTCIR11-Math2-queries-participants.xml'
#dataPath = 'D:/AizawaLaboratory/Mathcat/ntcir11/'
#qrelfile = 'MCAT/result_judge/NTCIR11_Math-qrels.dat'
#submfile = 'MCAT/result_submit/MCAT_all.tsv'
#htmlDir = 'D:/AizawaLaboratory/Mathcat/ntcir11/xhtmls/'

nmath_subm = 10

def parseQrel(qrelFullPath):
    lns = open(qrelFullPath).readlines()
    qrel = OrderedDict() #{NTCIR11-Math-1:{1205.2498_1_107:3}}
    for ln in lns:
        cells = ln.strip().split()
        if cells[0] not in qrel:
            qrel[cells[0]] = {}
        if int(cells[3]) > 0:
            qrel[cells[0]][cells[2]] = int(cells[3])
    return qrel

def parseSubm(submFullPath):
    lns = open(submFullPath).readlines()
    subm = OrderedDict() #{NTCIR11-Math-1:[1304.6518_1_8,...]}
    for ln in lns:
        cells = ln.strip().split()
        if cells[0] not in subm:
            subm[cells[0]] = []
        subm[cells[0]].append(cells[2])
    return subm

def extractHTMLBody(xhtml_name):
    xdoc = minidom.parse(path.join(htmlDir, xhtml_name + '.xhtml'))
    body = xdoc.getElementsByTagName('body')[0]
    body.tagName = 'div'
    return body.toxml()

def displaySubm(qrel, subm, nmath):
    submList = []
    topicdict = getQueryPresentation()
    summ = getQuerySummary(qrel, subm)
    for query, maths in subm.iteritems():
        submDict = {}
        submDict['title'] = query
        submDict['P5_R'] = summ[query]['R'][0]
        submDict['P10_R'] = summ[query]['R'][1]
        submDict['P5_PR'] = summ[query]['PR'][0]
        submDict['P10_PR'] = summ[query]['PR'][1]
        submDict['mathml'] = topicdict[query]['latex']
        submDict['keywords'] = ' '.join(topicdict[query]['keywords']) 
        submDict['link'] = '../ajax/?qid=' + query[query.rindex('-') + 1:]
        submList.append(submDict)
        print submDict['P5_R']
    return submList

def displaySingleQuery(qrel, subm, nmath, qid):
    submList = []
    query = 'NTCIR11-Math-' + qid
    maths = subm[query]
    
    nmts = 0
    for mt in maths:
        if nmts < nmath:
            score = qrel[query][mt] if mt in qrel[query] else 0
            submList.append({'paraname':mt, 'score':score, 'html':extractHTMLBody(mt)})
            nmts += 1
    return submList

def displaySingleQueryForQrel(qrel, subm, qid):
    qrelList = []
    query = 'NTCIR11-Math-' + qid
    maths = qrel[query]
    mathsInSubm = subm[query][:nmath_subm]
    for mt,score in maths.iteritems():
        if score < 3:continue
        if mt in mathsInSubm: continue
        score = qrel[query][mt]
        qrelList.append({'paraname':mt, 'score':score, 'html':extractHTMLBody(mt)})
    print len(qrelList)
    return qrelList
    
def getQuerySummary(qrel, subm):
    summ = {} #{NTCIR11-Math-1:{'R':(P@5, p@10), 'PR':(P@5,P@10)}}
    for query, maths in subm.iteritems():
        maths_relv = [qrel[query][mt] if mt in qrel[query] else 0 for mt in maths]
                              
        P5_R = len([mt for mt in maths_relv[:5] if mt > 2])
        P5_PR = len([mt for mt in maths_relv[:5] if mt > 0])
        P10_R = len([mt for mt in maths_relv[:10] if mt > 2])
        P10_PR = len([mt for mt in maths_relv[:10] if mt > 0])
        summ[query] = {'R':(P5_R, P10_R), 'PR':(P5_PR, P10_PR)}
    return summ
    
def getKeywordTokens(keywordTags):
    ks = []
    for k in keywordTags:
        kval = k.firstChild.nodeValue
        ks.extend(kval.split())
    return ks

def getQueryPresentation():
    xdoc = minidom.parse(path.join(dataPath, queryfile))
    topics = xdoc.getElementsByTagName('topic')
    topicdict = {}
    for topic in topics:
        topicname = topic.getElementsByTagName('num')[0].firstChild.nodeValue
        mathml = [t for t in topic.getElementsByTagName('m:annotation-xml') if t.getAttribute('encoding') == 'MathML-Presentation'][0].toxml()
        latex = [t for t in topic.getElementsByTagName('m:annotation') if t.getAttribute('encoding') == 'application/x-tex'][0].firstChild.nodeValue
        keywords = getKeywordTokens(topic.getElementsByTagName('keyword'))
        topicdict[topicname] = {'latex':latex, 'mathml': mathml, 'keywords':keywords}
    return topicdict
    
def ajax(request):
    qrel = parseQrel(path.join(dataPath, qrelfile))
    subm = parseSubm(path.join(dataPath, submfile))
    qid = request.GET.get('qid')
    isqrel = request.GET.get('qrel')
    maths = []
    if isqrel == 'true':
        maths = displaySingleQueryForQrel(qrel, subm, qid)
    else:
        maths = displaySingleQuery(qrel, subm, nmath_subm, qid)
    
    template = loader.get_template('ajax.html')
    context = RequestContext(request, {'maths':maths,})
    return HttpResponse(template.render(context))

def displayQrel(qrel, subm):
    qrelList = []
    topicdict = getQueryPresentation()
    for query, maths in subm.iteritems():
        mathsInQrel_R = set(mt for mt,score in qrel[query].iteritems() if score > 2)
        mathsInQrel_PR = set(mt for mt,score in qrel[query].iteritems() if score > 0)
        qrelDict = {}
        qrelDict['title'] = query
        qrelDict['N_R'] = len(mathsInQrel_R.difference(set(maths[:nmath_subm])))
        qrelDict['N_PR'] = len(mathsInQrel_PR.difference(set(maths[:nmath_subm])))
        qrelDict['mathml'] = topicdict[query]['latex']
        qrelDict['keywords'] = ' '.join(topicdict[query]['keywords'])
        qrelDict['link'] = '../ajax/?qrel=true&qid=' + query[query.rindex('-') + 1:]
        qrelList.append(qrelDict)
    return qrelList
    
def index(request):
    qrel = parseQrel(path.join(dataPath, qrelfile))
    subm = parseSubm(path.join(dataPath, submfile))
    isqrel = request.GET.get('qrel')
    queries = []
    if isqrel == 'true':
        queries = displayQrel(qrel, subm)
    else:
        queries = displaySubm(qrel, subm, nmath_subm)
    
    template = loader.get_template('index.html')
    context = RequestContext(request, {'queries':queries,'isqrel':isqrel})
    return HttpResponse(template.render(context))
