from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader

# Create your views here.
qrelfile = '/home/coeus/working/data/ntcir11-analysis/MCAT/result_judge/NTCIR11_Math-qrels.dat'
submfile = '/home/coeus/working/data/ntcir11-analysis/MCAT/result_submit/MCAT_all.tsv'
def parseQrel():
    lns = open(qrelfile).readlines()
    qrel = {} #{NTCIR11-Math-1:{1205.2498_1_107:3}}
    for ln in lns:
        cells = ln.strip().split()
        if cells[0] not in qrel:
            qrel[cells[0]] = {}
        qrel[cells[0]][cells[2]] = int(cells[3])
    return qrel

def parseSubm():
    lns = open(submfile).readlines()
    subm = {} #{NTCIR11-Math-1:[1304.6518_1_8,...]}
    for ln in lns:
        cells = ln.strip().split()
        if cells[0] not in subm:
            subm[cells[0]] = []
        subm[cells[0]].append(cells[2])
    return subm

def displaySubm(qrel, subm):
    submList = []
    for query, maths in subm.iteritems():
        submDict = {}
        submDict['title'] = query
        submDict['maths'] = []
        for mt in maths:
            submDict['maths'].append({'html':'asd'})
        submList.append(submDict)
    return submList

def index(request):
    qrel = parseQrel()
    subm = parseSubm()
    queries = displaySubm(qrel, subm)
    template = loader.get_template('index.html')
    context = RequestContext(request, {'queries':queries,})
    return HttpResponse(template.render(context))
