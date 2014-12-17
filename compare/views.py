from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from os import path
from collections import OrderedDict
from xml.dom import minidom

# Create your views here.
dataPath = '/Users/giovanni/working/ntcir11/ntcir11-analysis/data/'
qrelfile = 'NTCIR_2014_results/MCAT/result_judge/NTCIR11_Math-qrels.dat'
submfile = 'NTCIR_2014_results/MCAT/result_submit/MCAT_all.tsv'
htmlDir = '/Users/giovanni/working/ntcir11/ntcir11-analysis/data/xhtmls/'
nmath_subm = 10

def parseQrel(qrelFullPath):
    lns = open(qrelFullPath).readlines()
    qrel = OrderedDict() #{NTCIR11-Math-1:{1205.2498_1_107:3}}
    for ln in lns:
        cells = ln.strip().split()
        if cells[0] not in qrel:
            qrel[cells[0]] = {}
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

def displaySubm_Old(qrel, subm, nmath, qid):
    submList = []
    for query, maths in subm.iteritems():
        submDict = {}
        submDict['title'] = query
        submDict['maths'] = []
        nmts = 0
        for mt in maths:
            if nmts < nmath:
                score = qrel[query][mt] if mt in qrel[query] else 0
                #submDict['maths'].append({'paraname':mt, 'score':score, 'html':extractHTMLBody(mt)})
                submDict['maths'].append({'paraname':mt, 'score':score, 'html':qid})
                nmts += 1
        submList.append(submDict)
    return submList

def displaySubm(qrel, subm, nmath):
    submList = []
    for query, maths in subm.iteritems():
        submDict = {}
        submDict['title'] = query
        submDict['link'] = '../ajax/?qid=' + query[query.rindex('-') + 1:]
        submList.append(submDict)
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

def ajax(request):
    qrel = parseQrel(path.join(dataPath, qrelfile))
    subm = parseSubm(path.join(dataPath, submfile))
    qid = request.GET.get('qid')
    maths = displaySingleQuery(qrel, subm, nmath_subm, qid)
    template = loader.get_template('ajax.html')
    context = RequestContext(request, {'maths':maths,})
    return HttpResponse(template.render(context))

def index(request):
    qrel = parseQrel(path.join(dataPath, qrelfile))
    subm = parseSubm(path.join(dataPath, submfile))
    queries = displaySubm(qrel, subm, nmath_subm)

    template = loader.get_template('index.html')
    context = RequestContext(request, {'queries':queries,})
    return HttpResponse(template.render(context))
