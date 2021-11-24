# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse, FileResponse
from django.shortcuts import redirect,render, render_to_response
from django.template.loader import render_to_string
from django.forms.models import modelformset_factory,inlineformset_factory
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from utility_tool.forms import DecisionForm, SolOptForm, SolOptForm2, ScrCriteriaForm, EvaCriteriaForm, LoginForm, RegisterForm, StakeholdersForm, SolOptView, VotesForm, ScoresForm, SolOptArchive, SetupForm, CostSetupForm, DecisionMadeForm, FruitForm
from django.template import loader
from .models import Decisions, Solution_Options, Screening_Criteria, Evaluation_Criteria, Importance_Scores, Users, Stakeholders, Stakeholders_Decisions, MappingTable, SummaryTable, Evaluation_Measures, PA_Setup, EvaluationTable,  Cost_Setup, Cost_Utility, Decision_Made, Detailed_Costs, Fruit, CBCSE_Screening_Criteria, Master_Screening_Criteria, CBCSE_Evaluation_Criteria, Master_Evaluation_Criteria
import datetime
import json
import xlrd
import xlwt
import MySQLdb
import math
import types
import io
from django.core import serializers
from django.http import Http404
from selectable.registry import registry
from utility_tool.functions import check_required, group_cal, individual_cal, further_cal
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable 
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.files.storage import FileSystemStorage
from reportlab.lib.colors import black, blue, lightblue
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm

def get_lookup(request, lookup_name):

    lookup_cls = registry.get(lookup_name)
    if lookup_cls is None:
        raise Http404('Lookup %s not found' % lookup_name)

    lookup = lookup_cls()
    return lookup.results(request)

def fruit(request):
    if request.method == 'POST':
        fruitform = FruitForm(request.POST)
    else:
        if request.GET:
           fruitform = FruitForm(initial=request.GET)
        else:
           fruitform = FruitForm()

    return render(request,'fruit.html', {'fruitform': fruitform})
    '''
    #if 'name' in request.GET:
    entry_list = Fruit.objects.all()
    #for e in entry_list:
        #print e.name
    #if entry_list.count() == 1:
       #return redirect(entry_list[0])
    return render_to_response("fruit.html",{'entry_list':entry_list})
    #else:
    #return render_to_response("fruit.html",{'error':'Search query missing.'})
    '''
def index(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    #return HttpResponse("Hello, world. You're at the costutility index.")
    return render(request, 'index.html', {'loggedinuser':loggedinuser})

def summary_report(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
       dec = Decisions.objects.get(id=dec_id)
       name_decisionmaker = dec.name_decisionmaker
       title = dec.title
    except:
        name_decisionmaker = ''  
        title = ''

    try:
       std = Stakeholders_Decisions.objects.filter(dec_id=dec_id)
       stdec_count = std.exclude(email = user_email).count()
    except:
       stdec_count = 0
    
    text = ""
    try:
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, solopt_type = 'Y') 
       std_count = std.exclude(email = user_email).count()     
       if std_count > 0: 
          text = "suggesting Solution Options"
    except ObjectDoesNotExist:
       text= text + ""
    except MultipleObjectsReturned:                                                                                                           
       text = "suggesting Solution Options"   

    try:
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, scrcr_type = 'Y') 
       std_count = std.exclude(email = user_email).count()     
       if std_count > 0:
          if text <> "": 
             text = text + ", providing Screening Criteria"
          else:
             text = text + " providing Screening Criteria"
    except ObjectDoesNotExist:
       text= text + ""
    except MultipleObjectsReturned:                                                                                                           
          if text <> "": 
             text = text + ", providing Screening Criteria"
          else:
             text = text + " providing Screening Criteria"

    try:
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, evacr_type = 'Y') 
       std_count = std.exclude(email = user_email).count()     
       if std_count > 0: 
          if text <> "": 
             text = text + ", developing a list of Evaluation Criteria"
          else:
             text = text + " developing a list of Evaluation Criteria"
    except ObjectDoesNotExist:
       text= text + ""
    except MultipleObjectsReturned:                       
          if text <> "": 
             text = text + ", developing a list of Evaluation Criteria"
          else:
             text = text + " developing a list of Evaluation Criteria"   

    try:
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, iw_type = 'Y') 
       std_count = std.exclude(email = user_email).count()     
       if std_count > 0: 
          if text <> "": 
             text = text + " and contributing Importance Scores"
          else:
             text = text + " contributing Importance Scores" 
    except ObjectDoesNotExist:
       text= text + ""
    except MultipleObjectsReturned:                                                                                                          
          if text <> "": 
             text = text + " and contributing Importance Scores"
          else:
             text = text + " contributing Importance Scores"  

    try:                                                                                                                                                                                                         
       solopt_count = Solution_Options.objects.filter(dec_id=dec_id, archived='N').count()
    except:
       solopt_count = 0

    try:
       cost_utility = Cost_Utility.objects.filter(dec_id = dec_id, archived = 'N')
       cc = cost_utility.order_by('-weighted_utility')
      
       onerec = cc.first()
       type_of_cost = onerec.type_of_cost
       wu = onerec.weighted_utility
       so1 = ""
       for c in cc:
           if wu == c.weighted_utility:
              if so1 <> "":
                 so1 = so1 + ", " + c.sol_option
              else:
                 so1 = so1 + " " + c.sol_option 
           else: 
              so1 = onerec1.sol_option             

       cd = cost_utility.order_by('cost')
       onerec2 = cd.first()                                                                                                                                                                                     
       co = onerec2.cost
       so2 = ""
       for c in cd:
           if co == c.cost:
              if so2 <> "":
                 so2 = so2 + ", " + c.sol_option
              else:
                 so2 = so2 + " " + c.sol_option 
           else: 
              so2 = onerec2.sol_option 

       ce = cost_utility.order_by('cost_utility_ratio')                                                                                                                                                             
       onerec3 = ce.first()                                                                                                                                                                                     
       cur = onerec3.cost_utility_ratio
       so3 = ""
       for c in ce:
           if cur == c.cost_utility_ratio:
              if so3 <> "":
                 so3 = so3 + ", " + c.sol_option
              else:
                 so3 = so3 + " " + c.sol_option 
           else: 
              so3 = onerec3.sol_option  
    except:
       type_of_cost = ''
       wu = ''
       so1 = ''
       co = ''
       so2 = ''
       cur = ''
       so3 = ''
                                                                                                                                                                                                         
    try:
       dec_made = Decision_Made.objects.get(dec_id = dec_id)
       opt = dec_made.sol_option  
       reason = dec_made.reason
    except:
       opt = ''
       reason = ''
    
    chosen = ''
    z = opt.replace('[u', '')
    y = z.replace("'", "")
    x = y.replace("]","")

    try:
       sc = Solution_Options.objects.get(id=x)
       chosen = sc.sol_option
    except:
       chosen = '' 

     
    #http://www.blog.pythonlibrary.org/2014/03/10/reportlab-how-to-create-custom-flowables/
    class BoxyLine(Flowable):
    #Draw a box + line + text
        def __init__(self, x=1, y=-1, width=450, height=40, text=""):
           Flowable.__init__(self)
           self.x = x
           self.y = y
           self.width = width
           self.height = height
           self.text = text
           self.styles = getSampleStyleSheet()
 
        def coord(self, x, y, unit=1):
        #http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
        #Helper class to help position flowables in Canvas objects
           x, y = x * unit, self.height -  y * unit
           return x, y
 
        def draw(self):
           #Draw the shape, text, etc
           self.canv.rect(self.x, self.y, self.width, self.height)
           #self.canv.line(self.x, 0, 500, 0)
           self.styles = getSampleStyleSheet()
           self.styles.add(ParagraphStyle( name="ParagraphTitle", fontSize=12, alignment=TA_CENTER, fontName="Times-Roman", textColor= blue))
           p = Paragraph(self.text, style=self.styles["ParagraphTitle"])
           p.wrapOn(self.canv, self.width, self.height)
           p.drawOn(self.canv, *self.coord(self.x+2, 10, mm))
 

    doc = SimpleDocTemplate("/tmp/Summary Report.pdf", title="Summary Report")
    styles = getSampleStyleSheet()
    #styles.add(ParagraphStyle( name="ParagraphTitle", fontSize=12, alignment=TA_CENTER, fontName="Times-Roman", textColor= blue,backColor=lightblue))
    styles.add(ParagraphStyle( name="ParagraphTitle", fontSize=12, alignment=TA_LEFT, fontName="Times-Roman", textColor= blue))
    styles.add(ParagraphStyle( name="MainParagraph", fontSize=11, alignment=TA_JUSTIFY, fontName="Times-Roman"))
    p = Paragraph('title', styles["Normal"])
    data = []

    box = BoxyLine(text="<strong><i>DecisionMaker</i> Summary Report</strong>")
    data.append(box)
    data.append(Spacer(0, 20))
    '''     
    d = Drawing(1,1)
    d.add(Rect(1,1,450,40, fillColor=lightblue))
    data.append(d)
    data.append(Paragraph('<strong><i>DecisionMaker</i> Summary Report</strong>', styles["ParagraphTitle"]))
    '''
    #data.append(Spacer(1, 24))
    data.append(Paragraph('<strong>Executive Summary</strong>', styles["ParagraphTitle"])) 
    data.append(Spacer(1,10)) 
    actualpara = "Using <i>DecisionMaker</i>’s cost-utility decision-making framework, " +  name_decisionmaker + " engaged in a decision about: " + title +".<br/><br/>" 
    if stdec_count > 0 and text <> "":
       if stdec_count == 1:
          actualpara = actualpara + str(stdec_count) + " stakeholder was "
       else:
          actualpara = actualpara + str(stdec_count) + " stakeholders were "  
       actualpara = actualpara + "invited to contribute to the following stages of the decision-making process: " + text + "." 

    actualpara = actualpara +  "<br/><br/>Among " +  str(solopt_count) + " solution options that were evaluated," + so1 + " has the highest overall utility value, indicating that it is the best one to meet the stakeholders’ needs; " + so2 + " has the lowest " + type_of_cost + " cost; and " + so3 + " has the lowest cost-utility ratio, indicating that it provides the highest return on investment.<br/><br/>" + name_decisionmaker + " chose " + chosen + " based on the following rationale or consideration: " + reason + ".<br/><br/>For details, please refer to the following pages. " 
    data.append(Paragraph(actualpara, styles["MainParagraph"]))

    doc.build(data)

    fs = FileSystemStorage("/tmp")
    with fs.open("Summary Report.pdf") as pdf:
          response = HttpResponse(pdf, content_type='application/pdf')
          response['Content-Disposition'] = 'inline; filename="Summary Report.pdf"'
          return response

def temp(request):
    return render(request, 'temp.html')

def message(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    return render(request, 'decisions/message.html', {'dec_id':dec_id})

def nouser_message(request):
    return render(request, 'decisions/nouser_message.html')

def dec_info(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  
 
    return render(request, 'resources/dec_info.html', {'dec_id':dec_id, 'whereamI':whereamI})  

def st_info(request):                                                                                                                                                                                           
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/st_info.html', {'dec_id':dec_id, 'whereamI':whereamI})  

def solopt_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/solopt_info.html', {'dec_id':dec_id, 'whereamI':whereamI})    

def scr_info(request):                                                                                                                            
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/scr_info.html', {'dec_id':dec_id, 'whereamI':whereamI})    

def eva_info(request):                                                                                                                            
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/eva_info.html', {'dec_id':dec_id, 'whereamI':whereamI})  

def score_info(request):                                                                                                                            
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/score_info.html', {'dec_id':dec_id, 'whereamI':whereamI}) 


def evamea_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/evamea_info.html', {'dec_id':dec_id, 'whereamI':whereamI}) 

def utility_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  
    return render(request, 'resources/utility_info.html', {'dec_id':dec_id})  

def costs_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  
 
    return render(request, 'resources/costs_info.html', {'dec_id':dec_id, 'whereamI':whereamI})     

def makedec_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  

    if 'whereamI' in request.session:
       whereamI = request.session['whereamI']
    else:
       whereamI  = 0  

    return render(request, 'resources/makedec_info.html', {'dec_id':dec_id, 'whereamI':whereamI})   

def gen_info(request):     
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  
    return render(request, 'resources/gen_info.html', {'dec_id':dec_id})  

def about(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    return render(request, 'about.html', {'loggedinuser':loggedinuser})

def about_maker(request):                                                                                                                                  
    request.session['whereamI'] = 'aboutmaker'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    return render(request, 'resources/about_maker.html', {'loggedinuser':loggedinuser})


def menu3(request, dec_id):
    request.session['dec_id'] = dec_id

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    try: 
       dec = Decisions.objects.get(id=dec_id)
       request.session['dec_title'] = dec.title
       created_by = dec.created_by
    except:
       request.session['dec_title'] = 'not found' 
       created_by = 'not found'

    return render(request, 'decisions/menu3.html',{'dec_title':request.session['dec_title'], 'loggedinuser':loggedinuser})

def menu4(request, dec_id):
    request.session['dec_id'] = dec_id
                                                                                                                                                            
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    try: 
       dec = Decisions.objects.get(id=dec_id)
       request.session['dec_title'] = dec.title
       created_by = dec.created_by
    except:
       request.session['dec_title'] = 'not found' 
       created_by = 'not found'
    return render(request, 'decisions/menu4.html',{'dec_title':request.session['dec_title'], 'loggedinuser':loggedinuser})

def stakeholders(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
   

    if 'whereamI' in request.session:                                                                                                                                                                            
        whereamI = request.session['whereamI']
    else:
        whereamI = 'stakeholders'

    if request.method == 'POST':
       print request.POST.getlist('id')  
       if 'id' in request.POST:                                                                                                                                                                                 
           if 'submit' in request.POST: 
              for value in request.POST.getlist('id'):
                  try: 
                     old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value)
                  except ObjectDoesNotExist:
                     st = Stakeholders.objects.get(pk=value)
                     st_name = st.firstName + ' ' + st.lastName
                     st_dec = Stakeholders_Decisions(st_id = value, name = st_name, email=st.email, dec_id = request.session['dec_id'],created_by = request.session['user'],created_date = datetime.datetime.now())  
                     st_dec.save() 
       return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html')               
    if loggedinuser == 'not found':
       return HttpResponseRedirect('/utility_tool/decisions/nouser_message.html')           
    else:    
       stakeholders = Stakeholders.objects.filter(created_by=loggedinuser).order_by('firstName')
       return render(request,'stakeholders/stakeholders.html',{'stakeholders':stakeholders, 'loggedinuser':loggedinuser, 'dec_id':dec_id, 'whereamI':whereamI})

def add_stakeholder(request):
    context = RequestContext(request)
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
   
    if 'whereamI' in request.session:                                                                                                                                                                            
        whereamI = request.session['whereamI']
    else:
        whereamI = 'stakeholders'

    MFormSet = modelformset_factory(Stakeholders, form=StakeholdersForm, extra=6) 
    if request.method == 'POST':
        stform = MFormSet(request.POST,request.FILES, prefix="stform" )

        if stform.is_valid():
            id = stform.save(commit=False)
            for recs in id:
                if recs.email == '':
                   sterr = "Please enter an email address for the stakeholder/s you have added." 
                   return render(request,'stakeholders/add_stakeholder.html',{'stform':stform, 'sterr':sterr,'dec_id':dec_id, 'whereamI':whereamI}) 
                else:
                    try:
                       Stakeholders.objects.get(firstName = recs.firstName, lastName = recs.lastName, created_by=loggedinuser) 
                       sterr = "You have already added a stakeholder with the same name." 
                       return render(request,'stakeholders/add_stakeholder.html',{'stform':stform, 'sterr':sterr,'dec_id':dec_id, 'whereamI':whereamI}) 
                    except ObjectDoesNotExist:
                       try:
                           Stakeholders.objects.get(email = recs.email, created_by=loggedinuser) 
                           sterr = "You have already added a stakeholder with the same email address." 
                           return render(request,'stakeholders/add_stakeholder.html',{'stform':stform, 'sterr':sterr,'dec_id':dec_id, 'whereamI':whereamI}) 
                       except ObjectDoesNotExist:
                           recs.created_by = request.session['user']
                           recs.save()
            if 'submit' in request.POST:
               return HttpResponseRedirect('/utility_tool/stakeholders/stakeholders.html')
            elif 'menu' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
        else:
            print stform.errors

    else:
        qset = Stakeholders.objects.none()
        stform = MFormSet(queryset=qset,prefix="stform" )
        #stform = StakeholdersForm()

    return render(request,'stakeholders/add_stakeholder.html',{'stform':stform,'dec_id':dec_id, 'whereamI':whereamI})

def edit_stakeholder(request, st_id):
    context = RequestContext(request)

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    st = Stakeholders.objects.get(pk=st_id)
    if request.method == 'POST':
        stform = StakeholdersForm(data=request.POST,instance=st)
        if stform.is_valid():
            id = stform.save(commit=False)
            if id.email == '':
                sterr = "Please enter an email address." 
                return render(request,'stakeholders/edit_stakeholder.html',{'stform':stform, 'sterr':sterr}) 
            else:
                st1 = Stakeholders.objects.filter(firstName = id.firstName, lastName = id.lastName, created_by=loggedinuser).count() 
                if st1 > 1:
                   sterr = "You have already added a stakeholder with the same name." 
                   return render(request,'stakeholders/edit_stakeholder.html',{'stform':stform, 'sterr':sterr}) 
                st1 = Stakeholders.objects.filter(email = id.email, created_by=loggedinuser).count()
                if st1 > 1:
                   sterr = "You have already added a stakeholder with the same email address." 
                   return render(request,'stakeholders/edit_stakeholder.html',{'stform':stform, 'sterr':sterr}) 
                id.updated_by = request.session['user']   
                id.updated_date = datetime.datetime.now()
                id.save(update_fields=['firstName', 'lastName', 'title', 'email', 'phone', 'organisation', 'notes','updated_by', 'updated_date']) 
            return HttpResponseRedirect('/utility_tool/stakeholders/stakeholders.html')
        else:
            print stform.errors
    else:    
        stform = StakeholdersForm(instance=st)
    t = loader.get_template('stakeholders/edit_stakeholder.html')
    c = Context({'stform' :stform})
    return render(request,'stakeholders/edit_stakeholder.html',{'st_id':st_id, 'stform':stform})

def delete_stakeholder(request, st_id):
    context = RequestContext(request)
    stdec = Stakeholders_Decisions.objects.filter(st_id=st_id)
    for s in stdec:
        s.updated_by = request.session['user']   
        s.updated_date = datetime.datetime.now()
        s.deleted = 'Y'
        s.save(update_fields=['deleted','updated_by', 'updated_date']) 
    Stakeholders.objects.get(pk=st_id).delete()                                                                                                                                                               
    return HttpResponseRedirect('/utility_tool/stakeholders/stakeholders.html')

def add_st_privs(request):
    return render(request, 'stakeholders/add_st_privs.html') 

'''
def handsontable(request):
    return render(request, 'decisions/handsontable.html')
'''

def add_decision(request):
    context = RequestContext(request)

    if 'user_email' in request.session:                                                                                                                                                                          
       user_email = request.session['user_email']
    else:
       user_email = 'not found'
    print request.session['user']
    print user_email    
    if request.method == 'POST':
        decform = DecisionForm(data=request.POST)

        if decform.is_valid():
            id = decform.save(commit=False)
            id.created_by = request.session['user']

            try: 
               d = Decisions.objects.filter(title = id.title, created_by = id.created_by).count()
               if d > 0: 
                  return render_to_response('decisions/add_decision.html',{'decform':decform,'err':'This title is already taken. Please enter a unique name.'}, context)
            except ObjectDoesNotExist:
                print 'something wrong in add decision unique check'

            id.save()
            try:
               st = Stakeholders.objects.get(created_by = request.session['user'], email = user_email) 
               name = st.firstName + ' ' + st.lastName
               st_dec = Stakeholders_Decisions(st_id = st.id, name = name, email=st.email, dec_id = id.id,solopt_type = 'Y',scrcr_type = 'Y',evacr_type = 'Y',iw_type = 'Y',created_by = request.session['user'],created_date = datetime.datetime.now())      
               st_dec.save()
            except ObjectDoesNotExist:
                print 'stakeholder does not exist'
            #return HttpResponseRedirect('/utility_tool/decisions/decisions_list.html') 
            return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % id.id)
        else:
            print decform.errors

    else:
        decform = DecisionForm()

    t = loader.get_template('decisions/add_decision.html')
    c = Context({'decform' :decform})
    #html = t.render({'decform': decform})
    #return HttpResponse(html)

    return render(request,'decisions/add_decision.html',{'decform':decform})
    #return render_to_string(
            #'decisions/add_decision.html',
            #{'decform': decform}, context)

def decisions_list(request):
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if loggedinuser == 'not found':
       return HttpResponseRedirect('/utility_tool/decisions/nouser_message.html')           
    else:   
       if 'user_email' in request.session: 
          user_email = request.session['user_email']
       else:
          user_email = 'not found'
       request.session['whereamI'] = 'dec_list'   

       #f = open( '/home/amritha/costtool/documents/f.txt', 'w+' )
       #f.write('\n') 
       #f.close()

       declist = [] 
       st = Stakeholders_Decisions.objects.filter(email = user_email)
       qset = st.exclude(deleted = 'Y')

       for d in qset:
          declist.append(d.dec_id)

       #get unique dec ids   
       myset = set(declist)
       #print myset
       alldecisions = Decisions.objects.filter(created_by=loggedinuser) | Decisions.objects.filter(id__in=myset)
       alldecisions = alldecisions.order_by('-id')

       return render(request,'decisions/decisions_list.html',{'alldecisions':alldecisions, 'loggedinuser':loggedinuser})  

def view_decision(request, dec_id):
    decision = Decisions.objects.get(pk=dec_id)
    return render(request,'decisions/view_decision.html',{'decision':decision})

def edit_decision(request, dec_id):
    context = RequestContext(request)
    '''if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0'''
    decision = Decisions.objects.get(pk=dec_id)

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    #if 'created_by' in request.session:
       #created_by = request.session['created_by']
    #else:
    created_by = decision.created_by

    if 'whereamI' in request.session:
        whereamI = request.session['whereamI']
    else:
        whereamI = 'dec_list'

    if request.method == 'POST':
        decform = DecisionForm(data=request.POST,instance=decision)
        if decform.is_valid():
            id = decform.save(commit=False)
            id.updated_date = datetime.datetime.now()
            id.updated_by = request.session['user']
            try: 
               d = Decisions.objects.filter(title = id.title, created_by = id.created_by).count()
               if d > 1: 
                  return render_to_response('decisions/add_decision.html',{'decform':decform,'err':'This title is already taken. Please enter a unique name.'}, context)
            except ObjectDoesNotExist:
               print 'something wrong in edit decision unique check'
            print id.by_when   
            id.save(update_fields=['title','name_decisionmaker', 'type_of_dec', 'decision_prob','goal','target_audience', 'by_when', 'updated_date','updated_by']) 
            if whereamI == 'dec_list':
               return HttpResponseRedirect('/utility_tool/decisions/decisions_list.html')
            else:
               return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % id.id)
        else:
            print decform.errors
    else:                                                                                                                                                                                                        
        decform = DecisionForm(instance=decision)
        if loggedinuser != created_by:
           decform.fields['title'].widget.attrs['disabled'] = True
           decform.fields['name_decisionmaker'].widget.attrs['disabled'] = True
           decform.fields['type_of_dec'].widget.attrs['disabled'] = True
           decform.fields['decision_prob'].widget.attrs['disabled'] = True
           decform.fields['evidence'].widget.attrs['disabled'] = True
           decform.fields['goal'].widget.attrs['disabled'] = True
           decform.fields['target_audience'].widget.attrs['disabled'] = True
           decform.fields['by_when'].widget.attrs['disabled'] = True
    t = loader.get_template('decisions/edit_decision.html')
    c = Context({'decform' :decform})
    return render(request,'decisions/edit_decision.html',{'dec_id':dec_id, 'decform':decform, 'whereamI':whereamI, 'loggedinuser':loggedinuser, 'created_by':created_by})

def delete_decision(request, dec_id):
    context = RequestContext(request)

    Solution_Options.objects.filter(dec_id=dec_id).delete()
    Screening_Criteria.objects.filter(dec_id=dec_id).delete()
    Evaluation_Criteria.objects.filter(dec_id=dec_id).delete()
    Stakeholders_Decisions.objects.filter(dec_id=dec_id).delete()
    Cost_Utility.objects.filter(dec_id=dec_id).delete()
    Cost_Setup.objects.filter(dec_id=dec_id).delete()
    Decision_Made.objects.filter(dec_id=dec_id).delete()
    Evaluation_Measures.objects.filter(dec_id=dec_id).delete()
    EvaluationTable.objects.filter(dec_id=dec_id).delete()
    Importance_Scores.objects.filter(dec_id=dec_id).delete()
    MappingTable.objects.filter(dec_id=dec_id).delete()
    PA_Setup.objects.filter(dec_id=dec_id).delete()
    SummaryTable.objects.filter(dec_id=dec_id).delete()
    Master_Screening_Criteria.objects.filter(dec_id=dec_id).delete()
    Master_Evaluation_Criteria.objects.filter(dec_id=dec_id).delete()
    Detailed_Costs.objects.filter(dec_id=dec_id).delete()
    Decisions.objects.get(pk=dec_id).delete()                                                                                                                                                                  
    return HttpResponseRedirect('/utility_tool/decisions/decisions_list.html') 

def solutions_options_menu(request):
    return render(request,'decisions/solution_options/menu.html')

def question1(request, dec_id):
    request.session['dec_id'] = dec_id
    return render(request,'decisions/solution_options/question1.html')

def pa_setup(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                       
    else:
       dec_title = 'not found'

    if 'user_email' in request.session:                                                                                                               
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try:
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, iw_type = 'Y') 
       std_count = std.exclude(email = user_email).count()     
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                           
       stakeholdersNow = 'Y'                                                                                                                          

    return render(request,'decisions/pa_setup.html',{'dec_id':dec_id,'dec_title':dec_title, 'stakeholdersNow':stakeholdersNow})

'''
def pa_setup(request):                                                                                                                                                                                 
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'

    if 'user_email' in request.session:                                                                                                               
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
        setup = PA_Setup.objects.get(dec_id=dec_id)
        group_yn = setup.scores_group_yn
        votes_yn = setup.votes_yn 
    except ObjectDoesNotExist:
        #print 'error in setup'
        setup = PA_Setup(dec_id = dec_id, scores_group_yn = 'Y', votes_yn = 'N', created_date = datetime.datetime.now(), created_by = request.session['user'])
        group_yn = setup.scores_group_yn                                                                                                               
        votes_yn = setup.votes_yn
        setup.save()
    dec = Decisions.objects.get(pk=dec_id) 
    if request.method == 'POST':
       print request.POST.get('group_yn')
       print request.POST.get('votes_yn')
       if request.POST.get('group_yn') or request.POST.get('votes_yn'):
          setup.scores_group_yn = request.POST.get('group_yn')
          setup.votes_yn = request.POST.get('votes_yn') 
          setup.updated_date = datetime.datetime.now()
          setup.save(update_fields=['scores_group_yn','votes_yn','updated_date'])   
          dec.updated_by = request.session['user'] 
          dec.updated_date = datetime.datetime.now()
          dec.save(update_fields=['updated_by','updated_date'])
            if 'submit' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
            elif 'votes' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_iw_votes.html')
            elif 'scores' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_scores.html')
    return render(request,'decisions/pa_setup.html',{'dec_id':dec_id,'dec_title':dec_title, 'group_yn':group_yn, 'votes_yn':votes_yn})
'''

def menu(request, dec_id):
    request.session['dec_id'] = dec_id

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try:
       dec = Decisions.objects.get(id=dec_id)
       request.session['dec_title'] = dec.title
       created_by = dec.created_by
       request.session['created_by'] = created_by
    except:
       request.session['dec_title'] = 'not found' 
       created_by = 'not found'
       request.session['created_by'] = created_by 
                                                                                                                                                                                                                 
    request.session['whereamI'] = 'menu' 

    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                                                                                       
       if std_count > 0:
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N' 
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                           
       stakeholdersNow = 'Y' 

    # if the logged in user has created the decision, he has access to everything
    # if the user is a stakeholder for a decision type, he has access to that type 
    try: 
       Stakeholders_Decisions.objects.get(email = user_email, dec_id = dec_id, solopt_type = 'Y')
       solopt_allowed = 'Y'
    except:
       if loggedinuser == created_by:
          solopt_allowed = 'Y'
       else: 
          solopt_allowed = 'N'

    try: 
       st1 = Stakeholders_Decisions.objects.filter(dec_id = dec_id, solopt_type = 'Y')
       st2_count = st1.exclude(email = user_email).count()
       if st2_count > 0:
          stsolopt_created = 'Y'   
       else:
          stsolopt_created = 'N'
    except ObjectDoesNotExist:
       stsolopt_created = 'N'

    try: 
       Stakeholders_Decisions.objects.get(email = user_email, dec_id = dec_id, scrcr_type = 'Y')
       scrcr_allowed = 'Y' 
    except:
       if loggedinuser == created_by:
          scrcr_allowed = 'Y'
       else: 
          scrcr_allowed = 'N'

    try: 
       st1 = Stakeholders_Decisions.objects.filter(dec_id = dec_id, scrcr_type = 'Y')
       st2_count = st1.exclude(email = user_email).count()
       if st2_count > 0:
          stscr_created = 'Y'   
       else:
          stscr_created = 'N'
    except ObjectDoesNotExist:
       stscr_created = 'N'

    try:                                                                                                                                                                                                         
       Stakeholders_Decisions.objects.get(email = user_email, dec_id = dec_id, evacr_type = 'Y')
       evacr_allowed = 'Y' 
       steva_created = 'Y'
    except:
       steva_created = 'N'
       if loggedinuser == created_by:
          evacr_allowed = 'Y'
       else: 
          evacr_allowed = 'N'  

    try: 
       st1 = Stakeholders_Decisions.objects.filter(dec_id = dec_id, evacr_type = 'Y')
       st2_count = st1.exclude(email = user_email).count()
       if st2_count > 0:
          steva_created = 'Y'   
       else:
          steva_created = 'N'
    except ObjectDoesNotExist:
       steva_created = 'N'

    try:                                                                                                                                                                                                         
       Stakeholders_Decisions.objects.get(email = user_email, dec_id = dec_id, iw_type = 'Y')
       iw_allowed = 'Y' 
       stiw_created = 'Y' 
    except:
       stiw_created = 'N'
       if loggedinuser == created_by:
          iw_allowed = 'Y'
       else: 
          iw_allowed = 'N'       
     
    try: 
       st1 = Stakeholders_Decisions.objects.filter(dec_id = dec_id, iw_type = 'Y')
       st2_count = st1.exclude(email = user_email).count()
       if st2_count > 0:
          stiw_created = 'Y'   
       else:
          stiw_created = 'N'
    except ObjectDoesNotExist:
       stiw_created = 'N'
    '''
    try: 
        setup = PA_Setup.objects.get(dec_id=dec_id)
        group_yn = setup.scores_group_yn
        votes_yn = setup.votes_yn
        setup_created = 'Y'
    except ObjectDoesNotExist:
        setup_created = 'N'
        group_yn = 'N'
        votes_yn = 'Y'
    ''' 
    # if PA decides scores are decided by the group and not individually then scores screen should NOT be shown to other stakeholders
    #if group_yn == 'Y' and loggedinuser <> created_by:
    #if stiw_created == 'Y': 
       #iw_allowed = 'Y' 

    request.session['solopt_allowed'] = solopt_allowed
    request.session['scrcr_allowed'] = scrcr_allowed 
    request.session['evacr_allowed'] = evacr_allowed 
    request.session['iw_allowed'] = iw_allowed 

    try:
       solopt = Solution_Options.objects.get(dec_id=dec_id)
       solopt_created = 'Y'   
    except ObjectDoesNotExist:
       solopt_created = 'N'
    except MultipleObjectsReturned:                                                                                                           
       solopt_created = 'Y'     
 
    try: 
       scr = Screening_Criteria.objects.get(dec_id=dec_id)
       scr_created = 'Y' 
    except ObjectDoesNotExist:
       scr_created = 'N' 
    except MultipleObjectsReturned:                                                                                                                
       scr_created = 'Y' 

    try: 
       mapp = MappingTable.objects.get(dec_id=dec_id) 
       mapp_created = 'Y'  
    except ObjectDoesNotExist:
       mapp_created = 'N'  

    try: 
       eva = Evaluation_Criteria.objects.get(dec_id=dec_id)
       eva_created = 'Y' 
    except ObjectDoesNotExist:
       eva_created = 'N' 
    except MultipleObjectsReturned:                                                                                                                
       eva_created = 'Y' 
 
    try:
       qset = Evaluation_Measures.objects.get(dec_id=dec_id) 
       if qset.measure is None and qset.unit is None and qset.lowest_value is None and qset.highest_value is None and qset.higher_better is None and qset.option_value is None:
          evam_created = 'N'
       else:   
          evam_created = 'Y' 
    except ObjectDoesNotExist:
       evam_created = 'N' 
    except MultipleObjectsReturned:                                                                                                                
       q = Evaluation_Measures.objects.filter(dec_id=dec_id) 
       for qset in q: 
           if qset.measure is None and qset.unit is None and qset.lowest_value is None and qset.highest_value is None and qset.higher_better is None and qset.option_value is None:
              evam_created = 'N'
           else:   
              evam_created = 'Y'  
              break
    try: 
       iw = Importance_Scores.objects.get(dec_id = dec_id)
       iw_created = 'Y' 
    except ObjectDoesNotExist:
       iw_created = 'N' 
    except MultipleObjectsReturned:                                                                                                                
       iw_created = 'Y' 

    try:
       cu = Cost_Utility.objects.get(dec_id = dec_id)
       cu_created = 'Y'
    except ObjectDoesNotExist:
       cu_created = 'N'
    except MultipleObjectsReturned:
       cu_created = 'Y'

    try: 
       cost = Cost_Setup.objects.get(dec_id = dec_id)                                                                                                                                                            
       cost_created = 'Y'
    except ObjectDoesNotExist:
       cost_created = 'N'
    except MultipleObjectsReturned:
       cost_created = 'Y'

    try:
       decmade = Decision_Made.objects.get(dec_id = dec_id)
       decmade_created = 'Y'
    except ObjectDoesNotExist:
       decmade_created = 'N'
    except MultipleObjectsReturned:
       decmade_created = 'Y'
    print iw_allowed 
    print iw_created
    #print setup_created
    #print created_by
    #print loggedinuser
    return render(request,'decisions/menu.html',{'dec_title':request.session['dec_title'], 'dec_id':dec_id, 'loggedinuser':loggedinuser, 'created_by' :created_by, 'solopt_allowed':solopt_allowed, 'scrcr_allowed':scrcr_allowed, 'evacr_allowed': evacr_allowed, 'iw_allowed':iw_allowed, 'solopt_created':solopt_created, 'scr_created': scr_created, 'eva_created':eva_created, 'evam_created':evam_created, 'iw_created':iw_created, 'decmade_created':decmade_created, 'cu_created':cu_created, 'cost_created':cost_created, 'stsolopt_created':stsolopt_created, 'stscr_created':stscr_created, 'steva_created':steva_created, 'stiw_created':stiw_created, 'stakeholdersNow':stakeholdersNow, 'mapp_created':mapp_created})

def question2(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if request.method == 'POST':
        print request.POST 
        if 'whoEntersSO' in request.POST:
            request.session['whoEntersSO'] = request.POST['whoEntersSO']
            request.session['listType'] = request.POST['listType']
            '''try:
               import smtplib
               smtp = smtplib.SMTP('smtp.gmail.com',587)
               smtp.ehlo()
               smtp.starttls()
               smtp.login('amrithany@gmail.com', 'Daff1911')
               smtp.sendmail('amrithany@gmail.com', 'amritha_mm@yahoo.com', 'test message from cost utility')
               smtp.quit()
            except smtplib.SMTPException, error:
               #return render_to_response('login/forgot.html',{'registerform':registerform,'err':str(error)}, context) 
               return HttpResponse('failure')
            '''
            return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_solopt.html')       
        else: 
            return HttpResponse('FAIL!!!!!')
     
    return render(request,'decisions/solution_options/question2.html', {'dec_id':dec_id})

def question3(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    return render(request,'decisions/solution_options/question3.html', {'dec_id':dec_id})

def identify_st(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'

    return render(request,'decisions/solution_options/identify_st.html', {'dec_id':dec_id, 'dec_title':dec_title})

def guidance(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    request.session['whereamI']  = 0
    if loggedinuser == 'not found':
       return HttpResponseRedirect('/utility_tool/decisions/nouser_message.html')           
    else:    
       return render(request,'decisions/solution_options/guidance.html', {'dec_id':dec_id, 'loggedinuser':loggedinuser})

def add_solopt_det(request):
    context = RequestContext(request)
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'

    #if solopt_allowed == 'Y' and scrcr_allowed == 'Y': 
    if loggedinuser == created_by:
       mapping_allowed = 'Y'
    else:
       mapping_allowed = 'N'

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                                                                                       
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  

    scr_count = Screening_Criteria.objects.filter(dec_id=dec_id).count()
    MFormSet = modelformset_factory(Solution_Options, form=SolOptForm2, extra=6)
       
    dec = Decisions.objects.get(pk=dec_id)   
    something_saved = 'no'
    if request.method == 'POST':
        soloptform = MFormSet(request.POST,request.FILES, prefix="soloptform" )
        if soloptform.is_valid():
           id = soloptform.save(commit=False)
           for recs in id:
              if recs.sol_option <> '':
                 recs.dec_id = request.session['dec_id'] 
                 if recs.source == '':
                    return render(request,'decisions/solution_options/add_solopt_det.html',{'soloptform':soloptform,'dec_id':dec_id, 'dec_title':dec_title, 'mapping_allowed': mapping_allowed, 'scr_count':scr_count, 'err':'Please enter the Source of the Option entered.'})  
                 try:
                    s = Solution_Options.objects.filter(sol_option = recs.sol_option, dec_id = dec_id)
                    st2_count = s.exclude(pk = recs.id).count()
                    if st2_count > 0:
                        return render(request,'decisions/solution_options/add_solopt_det.html',{'soloptform':soloptform,'dec_id':dec_id, 'dec_title':dec_title, 'mapping_allowed': mapping_allowed, 'scr_count':scr_count, 'err':'This Option already exists for this Decision. Please enter an unique Option.'})
                 except ObjectDoesNotExist:
                     print 'there is an exception'

                 if recs.archived == 'Y':
                    recs.archived_by = request.session['user'] 
                    recs.archived_date = datetime.datetime.now()
                    for e in Evaluation_Measures.objects.filter(opt_id = recs.id):
                        e.archived = 'Y'
                        e.updated_by = request.session['user'] 
                        e.updated_date = datetime.datetime.now()
                        e.save(update_fields=['archived','updated_by','updated_date'])
                    c =  Cost_Utility.objects.get(opt_id = recs.id)
                    c.archived = 'Y'
                    c.updated_by = request.session['user'] 
                    c.updated_date = datetime.datetime.now()
                    c.save(update_fields=['archived','updated_by','updated_date'])      
                 else:
                    recs.archived = 'N' 
                    if recs.created_by == '':
                       recs.created_by = request.session['user'] 
                       recs.created_date = datetime.datetime.now()
                    else:   
                       recs.updated_by = request.session['user'] 
                       recs.updated_date = datetime.datetime.now()
                 something_saved ='yes'
                 recs.save()
                 #print recs.id
                 #Evaluation_Measures.objects.filter(opt_id = recs.id, dec_id = dec_id).delete()
                 #Cost_Utility.objects.get(opt_id = recs.id, dec_id = dec_id).delete()
                 #Detailed_Costs.objects.get(opt_id = recs.id, dec_id = dec_id).delete()
                 
           if something_saved == 'yes':  
              dec.updated_by = request.session['user'] 
              dec.updated_date = datetime.datetime.now()
              dec.save(update_fields=['updated_by','updated_date'])
           if 'submit' in request.POST:
              return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
           elif 'map' in request.POST:
              '''
              if something_saved == 'no':
                 err = 'You cannot Map Solution Options to Screening Criteria until you have entered at least one option.'
                 return render(request,'decisions/solution_options/add_solopt_det.html',{'err':err, 'soloptform':soloptform,'dec_id':dec_id, 'dec_title':dec_title, 'mapping_allowed': mapping_allowed, 'scr_count':scr_count })
              else:
              '''
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/handsontable.html')
           elif 'scrcr' in request.POST:
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_scr_criteria.html')
           elif 'archived' in request.POST:
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/solopt_archive.html')
           elif 'st' in request.POST:
              if stakeholdersNow == 'Y':
                 return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html') 
              else:
                 return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_all.html') 
        else:
            print soloptform.errors
    else:
        qset = Solution_Options.objects.filter(dec_id=dec_id, archived='N')
        '''qcount =  qset.count()
        if qcount == 0:
           exists = 'no'
        else:
           exists = 'yes' 
        '''
        soloptform = MFormSet(queryset=qset,prefix="soloptform" )
        for form in soloptform:
            form.fields['created_by'].widget.attrs['readonly'] = True
            form.fields['updated_by'].widget.attrs['readonly'] = True
            if loggedinuser != created_by:
               form.fields['archived'].widget.attrs['disabled'] = True  
    return render(request,'decisions/solution_options/add_solopt_det.html',{'soloptform':soloptform,'dec_id':dec_id, 'dec_title':dec_title, 'mapping_allowed': mapping_allowed, 'scr_count':scr_count,'created_by':created_by, 'loggedinuser':loggedinuser })

def solopt_archive(request):
    context = RequestContext(request)

    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0  
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'

    MFormSet = modelformset_factory(Solution_Options, form=SolOptArchive, extra=0)
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    qset_count = 0
    button_shown = 'no'

    if request.method == 'POST':
        soloptform = MFormSet(request.POST,request.FILES, prefix="soloptform" )
        if soloptform.is_valid():
           id = soloptform.save(commit=False)
           for recs in id:
               if recs.unarchived == 'Y':
                  recs.archived = 'N'
                  recs.unarchived = ''
                  recs.unarchived_by = request.session['user'] 
                  recs.unarchived_date = datetime.datetime.now()
                  something_saved = 'yes'
                  recs.save(update_fields=['archived','unarchived','unarchived_by','unarchived_date'])
           if something_saved == 'yes':  
              dec.updated_by = request.session['user'] 
              dec.updated_date = datetime.datetime.now()
              dec.save(update_fields=['updated_by','updated_date'])   
           #if 'submit' in request.POST:
               #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
           #elif 'solopt' in request.POST:
           return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_solopt_det.html')
        else:
            print soloptform.errors
    else:
        qset = Solution_Options.objects.filter(dec_id=dec_id, archived='Y')
        qset_count = Solution_Options.objects.filter(dec_id=dec_id, archived='Y').count()
        if qset_count == 0:
           button_shown = 'no'
        else:   
           button_shown = 'yes' 
        soloptform = MFormSet(queryset=qset,prefix="soloptform" )

    return render(request,'decisions/solution_options/solopt_archive.html',{'soloptform':soloptform,'dec_id':dec_id, 'dec_title':dec_title, 'button_shown':button_shown })


def view_solopt_det(request, dec_id):
    context = RequestContext(request)                                                                                                                                                                            
    MFormSet = modelformset_factory(Solution_Options, form=SolOptView)
    try:
       dec = Decisions.objects.get(id=dec_id)
       dec_title = dec.title
    except:
       dec_title = 'not found' 
        
    qset = Solution_Options.objects.filter(dec_id=dec_id, archived='N')
    soloptform = MFormSet(queryset=qset,prefix="soloptform" )
    return render(request,'decisions/solution_options/view_solopt_det.html',{'soloptform':soloptform, 'dec_title':dec_title})

def link(request):
    context = RequestContext(request)   
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0 
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'
     
    return render(request,'decisions/solution_options/link.html',{'dec_id':dec_id, 'dec_title':dec_title})  

def add_st_all(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and deleted is null)", [loggedinuser, dec_id])
    stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s) order by firstName", [loggedinuser, dec_id])
   
    if request.method == 'POST':
        #print request.POST.getlist('id') 
        if 'id' in request.POST:
            if 'submit' in request.POST: 
               for value in request.POST.getlist('id'):
                  try: 
                     old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value)
                  except ObjectDoesNotExist:
                     st = Stakeholders.objects.get(pk=value)
                     st_name = st.firstName + ' ' + st.lastName
                     st_dec = Stakeholders_Decisions(st_id = value, name = st_name, email=st.email, dec_id = request.session['dec_id'],created_by = request.session['user'],created_date = datetime.datetime.now())
                     st_dec.save() 
        return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html')       
    return render(request,'decisions/solution_options/add_st_all.html',{'stakeholders':stakeholders,'st_dec': stakeholders_decisions, 'dec_id':dec_id, 'dec_title':dec_title})

def assign_tasks(request):                                                                                                                                                                                         
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and deleted is null) order by firstName", [loggedinuser, dec_id]) 
    #stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and deleted = 'Y')", [loggedinuser, dec_id])
    stdec_type = Stakeholders_Decisions.objects.raw("SELECT id, st_id, solopt_type, scrcr_type, evacr_type, iw_type from utility_tool_stakeholders_decisions where dec_id=%s and deleted is null", [dec_id]) 
    if request.method == 'POST':
        #print request.POST.getlist('selected') 
        id_to_use = request.POST.get('id')
        solopt_type = ''
        scrcr_type = ''
        evacr_type = ''
        iw_type = '' 
        if 'selected' in request.POST:
            for value in request.POST.getlist('selected'):
                if value != "[]":
                   print value
                   if "solopt" in value:
                       if "soloptY" in value: 
                          solopt_type = 'Y'
                       else:   
                          solopt_type = ''
                   if "scrcr" in value:
                       print value 
                       if "scrcrY" in value: 
                          scrcr_type = 'Y'
                       else:   
                          scrcr_type = ''   
                       print scrcr_type
                   if "evacr" in value: 
                       if "evacrY" in value: 
                          evacr_type = 'Y'
                       else:   
                          evacr_type = ''   
                   if "iw" in value: 
                       if "iwY" in value: 
                          iw_type = 'Y'
                       else:   
                          iw_type = ''   

                   stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=id_to_use) 
                   stdec.solopt_type = solopt_type
                   stdec.scrcr_type = scrcr_type 
                   stdec.evacr_type = evacr_type 
                   stdec.iw_type = iw_type   
                   stdec.updated_by = request.session['user']
                   stdec.updated_date = datetime.datetime.now()
                   stdec.save(update_fields=['solopt_type','scrcr_type','evacr_type','iw_type','updated_by','updated_date'])        
        else:
            for value in request.POST.getlist('id'):
                print value
                try: 
                   delsolopt = Stakeholders_Decisions.objects.get(dec_id=dec_id, st_id=value)
                   delsolopt.delete()
                except ObjectDoesNotExist:
                   print 'id does not exist'
                   return HttpResponse('Selected Id does not exist in database. Please contact your Administrator.')
        #else:                                                                                                                                                                                                    
            #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
    return render(request,'decisions/solution_options/assign_tasks.html',{'st_dec': stakeholders_decisions, 'stdec_type':stdec_type, 'dec_id':dec_id, 'dec_title':dec_title})

def add_st_solopt(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                        
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and solopt_type = 'Y' and deleted is null) order by firstName", [loggedinuser, dec_id])

    stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and (solopt_type = 'Y' or deleted = 'Y')) order by firstName", [loggedinuser, dec_id])
   
    if request.method == 'POST':
        if 'id' in request.POST:
            if 'submit' in request.POST: 
               for value in request.POST.getlist('id'):
                  try:
                     old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                     old_stdec.solopt_type = 'Y' 
                     old_stdec.updated_by = request.session['user']
                     old_stdec.updated_date = datetime.datetime.now()
                     old_stdec.save(update_fields=['solopt_type','updated_by','updated_date'])
                  except ObjectDoesNotExist:
                     st = Stakeholders.objects.get(pk=value)
                     st_dec = Stakeholders_Decisions(st_id = value, email=st.email, dec_id = request.session['dec_id'],solopt_type = 'Y' ,created_by = request.session['user'],created_date = datetime.datetime.now())
                     st_dec.save()
               #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)      
            else:    
                for value in request.POST.getlist('id'):
                    try: 
                       old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                       old_stdec.solopt_type = 'N'  
                       old_stdec.updated_by = request.session['user']
                       old_stdec.updated_date = datetime.datetime.now()
                       old_stdec.save(update_fields=['solopt_type','updated_by','updated_date'])
                    except ObjectDoesNotExist:
                       print 'id does not exist'
                       return HttpResponse('Selected Id does not exist in database. Please contact your Administrator.')

        else:
            return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)

    return render(request,'decisions/solution_options/add_st_solopt.html',{'stakeholders':stakeholders,'st_dec': stakeholders_decisions, 'dec_id':dec_id, 'dec_title':dec_title})

def add_scr_criteria(request):
    context = RequestContext(request)
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'
    #if solopt_allowed == 'Y' and scrcr_allowed == 'Y': 
    if loggedinuser == created_by: 
       mapping_allowed = 'Y'
    else:
       mapping_allowed = 'N'
    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:                                                                                                                                                
       user_email = 'not found'
    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                               
       if std_count > 0:                                                                                                                                 
          stakeholdersNow = 'Y'
       else:
          stakeholdersNow = 'N'
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  
    solopt_count = Solution_Options.objects.filter(dec_id=dec_id, archived='N').count()
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    
    try: 
       firstrec = Master_Screening_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       orig_qset = CBCSE_Screening_Criteria.objects.all()                                                                                                   
       for orig in orig_qset:
           orig_scr_save = Master_Screening_Criteria(criterion = orig.criterion, dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
           orig_scr_save.save()
    except MultipleObjectsReturned:                                                                                                                    
       print 'multiple rows in master screening criteria'
 
    qset = Master_Screening_Criteria.objects.filter(dec_id=dec_id)
    qset2 = Screening_Criteria.objects.filter(dec_id=dec_id)
    qset3 = qset2.exclude(orig_scr_id__isnull=False)
    request.session['map_list'] = []  
    # First part is a set of checkboxes. Second part is a set of text boxes.
    # Checkbox values come from Master Screening Criteria for each decision (which comes from CBCSE screening criteria excel)
    # Delete is based on a hiddenfield text box in the HTML file
    # There are 15 text boxes - you can add and edit the criterion, you cannot delete but you can clear the field so it looks as if it has been deleted
    if request.method == 'POST':
       #print request.POST 
       for val in request.POST.getlist('hiddenfield'):   
           if val.endswith('U'):
              print val
              print val[:-1]
              try: 
                 scrdel = Screening_Criteria.objects.get(orig_scr_id = val[:-1], dec_id=dec_id)
                 request.session['map_list'].append(scrdel.id)
                 scrdel.delete()
              except ObjectDoesNotExist:
                 print 'cannot delete something that does not exist'  
       for value in request.POST.getlist('scrcr'):
           #print value
            
           try:
              cbcse_scr = Master_Screening_Criteria.objects.get(id = value, dec_id=dec_id)
              crit =  cbcse_scr.criterion
           except ObjectDoesNotExist:
              crit = ''

           try: 
              old_scr = Screening_Criteria.objects.get(criterion = crit, dec_id=dec_id)
              old_scr_exists = 'Y'   
           except ObjectDoesNotExist:
              old_scr_exists = 'N'

           fieldname = value + 'two'
           if old_scr_exists == 'N':  
              scr_save = Screening_Criteria(criterion = crit, criterion2 = request.POST.get(fieldname), orig_scr_id = value, dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now()) 
              scr_save.save() 
           else:
               old_scr.criterion2 = request.POST.get(fieldname)
               old_scr.orig_scr_id = value
               old_scr.updated_by = request.session['user']
               old_scr.updated_date = datetime.datetime.now()
               old_scr.save(update_fields=['criterion2','orig_scr_id','updated_by','updated_date'])
       try:
          old_scr1 = Screening_Criteria.objects.get(fieldname = 'cri1', dec_id=dec_id)
          old_scr1.criterion = request.POST.get('cri1')
          old_scr1.updated_by = request.session['user']
          old_scr1.updated_date = datetime.datetime.now()
          old_scr1.save(update_fields=['criterion','updated_by','updated_date'])
          print old_scr1.criterion
          if old_scr1.criterion == '' or old_scr1.criterion is None:
             request.session['map_list'].append(old_scr1.id)
       except ObjectDoesNotExist:   
          if request.POST.get('cri1') <> '':                                                                                                                                                                         
             scr_save1 = Screening_Criteria(criterion = request.POST.get('cri1'), fieldname = 'cri1', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save1.save()
       try:
          old_scr2 = Screening_Criteria.objects.get(fieldname = 'cri2', dec_id=dec_id)
          old_scr2.criterion = request.POST.get('cri2')
          old_scr2.updated_by = request.session['user']
          old_scr2.updated_date = datetime.datetime.now()
          old_scr2.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr2.criterion == '' or old_scr2.criterion is None:
             request.session['map_list'].append(old_scr2.id)
       except ObjectDoesNotExist:         
          if request.POST.get('cri2') <> '':                                                                                                                                                                    
             scr_save2 = Screening_Criteria(criterion = request.POST.get('cri2'), fieldname = 'cri2', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save2.save()  
       try:
          old_scr3 = Screening_Criteria.objects.get(fieldname = 'cri3', dec_id=dec_id)
          old_scr3.criterion = request.POST.get('cri3')
          old_scr3.updated_by = request.session['user']
          old_scr3.updated_date = datetime.datetime.now()
          old_scr3.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr3.criterion == '' or old_scr3.criterion is None:
             request.session['map_list'].append(old_scr3.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri3') <> '':                                                                                                                                                               
             scr_save3 = Screening_Criteria(criterion = request.POST.get('cri3'), fieldname = 'cri3', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())               
             scr_save3.save()
       try:
          old_scr4 = Screening_Criteria.objects.get(fieldname = 'cri4', dec_id=dec_id)
          old_scr4.criterion = request.POST.get('cri4')
          old_scr4.updated_by = request.session['user']
          old_scr4.updated_date = datetime.datetime.now()
          old_scr4.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr4.criterion == '' or old_scr4.criterion is None:
             request.session['map_list'].append(old_scr4.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri4') <> '':                                                                                                                                                               
             scr_save4 = Screening_Criteria(criterion = request.POST.get('cri4'), fieldname = 'cri4', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save4.save() 
       try:
          old_scr5 = Screening_Criteria.objects.get(fieldname = 'cri5', dec_id=dec_id)
          old_scr5.criterion = request.POST.get('cri5')
          old_scr5.updated_by = request.session['user']
          old_scr5.updated_date = datetime.datetime.now()
          old_scr5.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr5.criterion == '' or old_scr5.criterion is None:
             request.session['map_list'].append(old_scr5.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri5') <> '':                                                                                                                                                               
             scr_save5 = Screening_Criteria(criterion = request.POST.get('cri5'), fieldname = 'cri5', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save5.save() 
       try:
          old_scr6 = Screening_Criteria.objects.get(fieldname = 'cri6', dec_id=dec_id)
          old_scr6.criterion = request.POST.get('cri6')
          old_scr6.updated_by = request.session['user']
          old_scr6.updated_date = datetime.datetime.now()
          old_scr6.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr6.criterion == '' or old_scr6.criterion is None:
             request.session['map_list'].append(old_scr6.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri6') <> '':                                                                                                                                                               
             scr_save6 = Screening_Criteria(criterion = request.POST.get('cri6'), fieldname = 'cri6', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save6.save()  
       try:
          old_scr7 = Screening_Criteria.objects.get(fieldname = 'cri7', dec_id=dec_id)
          old_scr7.criterion = request.POST.get('cri7')
          old_scr7.updated_by = request.session['user']
          old_scr7.updated_date = datetime.datetime.now()
          old_scr7.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr7.criterion == '' or old_scr7.criterion is None:
             request.session['map_list'].append(old_scr7.id)
       except ObjectDoesNotExist:  
          if request.POST.get('cri7') <> '':                                                                                                                                                                           
             scr_save7 = Screening_Criteria(criterion = request.POST.get('cri7'), fieldname = 'cri7', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save7.save()  
       try:
          old_scr8 = Screening_Criteria.objects.get(fieldname = 'cri8', dec_id=dec_id)
          old_scr8.criterion = request.POST.get('cri8')
          old_scr8.updated_by = request.session['user']
          old_scr8.updated_date = datetime.datetime.now()
          old_scr8.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr8.criterion == '' or old_scr8.criterion is None:
             request.session['map_list'].append(old_scr8.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri8') <> '':                                                                                                                                                               
             scr_save8 = Screening_Criteria(criterion = request.POST.get('cri8'), fieldname = 'cri8', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save8.save()  
       try:
          old_scr9 = Screening_Criteria.objects.get(fieldname = 'cri9', dec_id=dec_id)
          old_scr9.criterion = request.POST.get('cri9')
          old_scr9.updated_by = request.session['user']
          old_scr9.updated_date = datetime.datetime.now()
          old_scr9.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr9.criterion == '' or old_scr9.criterion is None:
             request.session['map_list'].append(old_scr9.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri9') <> '':                                                                                                                                                               
             scr_save9 = Screening_Criteria(criterion = request.POST.get('cri9'), fieldname = 'cri9', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())                
             scr_save9.save()  
       try:
          old_scr10 = Screening_Criteria.objects.get(fieldname = 'cri10', dec_id=dec_id)
          old_scr10.criterion = request.POST.get('cri10')
          old_scr10.updated_by = request.session['user']
          old_scr10.updated_date = datetime.datetime.now()
          old_scr10.save(update_fields=['criterion','updated_by','updated_date']) 
          if old_scr10.criterion == '' or old_scr10.criterion is None:
             request.session['map_list'].append(old_scr10.id)
       except ObjectDoesNotExist:              
          if request.POST.get('cri10') <> '':                                                                                                                                                               
             scr_save10 = Screening_Criteria(criterion = request.POST.get('cri10'), fieldname = 'cri10', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())               
             scr_save10.save() 
       try:
          old_scr11 = Screening_Criteria.objects.get(fieldname = 'cri11', dec_id=dec_id)
          old_scr11.criterion = request.POST.get('cri11')
          old_scr11.updated_by = request.session['user']
          old_scr11.updated_date = datetime.datetime.now()
          old_scr11.save(update_fields=['criterion','updated_by','updated_date'])
          if old_scr11.criterion == '' or old_scr11.criterion is None:
             request.session['map_list'].append(old_scr11.id)
       except ObjectDoesNotExist:
          if request.POST.get('cri11') <> '':
             scr_save11 = Screening_Criteria(criterion = request.POST.get('cri11'), fieldname = 'cri11', dec_id = request.session['dec_id'], created_by =request.session['user'],created_date = datetime.datetime.now())   
             scr_save11.save()
       try:
          old_scr12 = Screening_Criteria.objects.get(fieldname = 'cri12', dec_id=dec_id)
          old_scr12.criterion = request.POST.get('cri12')
          old_scr12.updated_by = request.session['user']
          old_scr12.updated_date = datetime.datetime.now()
          old_scr12.save(update_fields=['criterion','updated_by','updated_date'])
          if old_scr12.criterion == '' or old_scr12.criterion is None:
             request.session['map_list'].append(old_scr12.id)
       except ObjectDoesNotExist:
          if request.POST.get('cri12') <> '':
             scr_save12 = Screening_Criteria(criterion = request.POST.get('cri12'), fieldname = 'cri12', dec_id = request.session['dec_id'], created_by =request.session['user'],created_date = datetime.datetime.now())   
             scr_save12.save()
       try:
          old_scr13 = Screening_Criteria.objects.get(fieldname = 'cri13', dec_id=dec_id)
          old_scr13.criterion = request.POST.get('cri13')
          old_scr13.updated_by = request.session['user']
          old_scr13.updated_date = datetime.datetime.now()
          old_scr13.save(update_fields=['criterion','updated_by','updated_date'])
          if old_scr13.criterion == '' or old_scr13.criterion is None:
             request.session['map_list'].append(old_scr13.id)
       except ObjectDoesNotExist:
          if request.POST.get('cri13') <> '':
             scr_save13 = Screening_Criteria(criterion = request.POST.get('cri13'), fieldname = 'cri13', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())   
             scr_save13.save()
       try:
          old_scr14 = Screening_Criteria.objects.get(fieldname = 'cri14', dec_id=dec_id)
          old_scr14.criterion = request.POST.get('cri14')
          old_scr14.updated_by = request.session['user']
          old_scr14.updated_date = datetime.datetime.now()
          old_scr14.save(update_fields=['criterion','updated_by','updated_date'])
          if old_scr14.criterion == '' or old_scr14.criterion is None:
             request.session['map_list'].append(old_scr14.id)
       except ObjectDoesNotExist:
          if request.POST.get('cri14') <> '':
             scr_save14 = Screening_Criteria(criterion = request.POST.get('cri14'), fieldname = 'cri14', dec_id = request.session['dec_id'], created_by =request.session['user'],created_date = datetime.datetime.now())   
             scr_save14.save()
       try:
          old_scr15 = Screening_Criteria.objects.get(fieldname = 'cri15', dec_id=dec_id)
          old_scr15.criterion = request.POST.get('cri15')
          old_scr15.updated_by = request.session['user']
          old_scr15.updated_date = datetime.datetime.now()
          old_scr15.save(update_fields=['criterion','updated_by','updated_date'])
          if old_scr15.criterion == '' or old_scr15.criterion is None:
             request.session['map_list'].append(old_scr15.id)
       except ObjectDoesNotExist:
          if request.POST.get('cri15') <> '':
             scr_save15 = Screening_Criteria(criterion = request.POST.get('cri15'), fieldname = 'cri15', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())   
             scr_save15.save() 

       if 'submit' in request.POST:    
           return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
       elif 'map' in request.POST:
           return HttpResponseRedirect('/utility_tool/decisions/solution_options/handsontable.html')   
       elif 'solopt' in request.POST:
           return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_solopt_det.html')
       elif 'st' in request.POST:
           if stakeholdersNow == 'Y':
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html') 
           else:
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_all.html')   
    return render(request,'decisions/solution_options/add_scr_criteria.html',{'qset':qset,'qset2':qset2,'qset3':qset3,'dec_id':dec_id, 'dec_title':dec_title,'mapping_allowed': mapping_allowed, 'solopt_count':solopt_count,'created_by':created_by, 'loggedinuser':loggedinuser, 'stakeholdersNow':stakeholdersNow})

'''
def add_eva_criteria(request):
    context = RequestContext(request)

    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'


    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                                                                                       
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  

    solopt  = Solution_Options.objects.filter(dec_id=dec_id, archived='N')
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'

    if request.method == 'POST':
       for array in request.POST.getlist('getdata'):
           print (array)

       arr = array[1:]                                                                                                                               
       #print arr 
       b = arr.replace('[null,null,null,null],','')
       a = b.replace('[null,null,null,null]','')
       #print a                                                                                                                                      
       # loop through the remaining array of arrays
       while len(a):     
          firstpos = a.find('[') + 1
          lastpos =  a.find(']')
          arr2 = a[firstpos:lastpos]
          #print arr2
          temp_list = []
          # adding each array to a temporary list
          for l2 in arr2.split(','):
             l3 = l2.replace('"', '')     
             temp_list.append(l3)
          if temp_list[0] == 'null':
              m = Evaluation_Criteria(criterion = temp_list[1], dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())
              m.save()   
              something_saved = 'yes'
          elif temp_list[1] == "":
              Importance_Scores.objects.filter(eva_id = temp_list[0], dec_id = request.session['dec_id']).delete() 
              Evaluation_Criteria.objects.get(id = temp_list[0]).delete()
              something_saved = 'yes'
          else:
             try:
                m = Evaluation_Criteria.objects.get(id = temp_list[0]) 
                if (m.criterion != temp_list[1]): 
                   m.criterion = temp_list[1]
                   m.updated_by = request.session['user']
                   m.updated_date = datetime.datetime.now()
                   m.save(update_fields=['criterion','updated_by','updated_date'])                                                                   
                   something_saved = 'yes'
             except ObjectDoesNotExist:
                print 'there is a problem somewhere'
          z = a.replace(arr2, '')
          c = z.replace('[],','')
          print c
          if (c == '[]]') or (c == ']'):
             break;
          a = c
          if something_saved == 'yes':  
             dec.updated_by = request.session['user'] 
             dec.updated_date = datetime.datetime.now()
             dec.save(update_fields=['updated_by','updated_date'])  
    qset = Evaluation_Criteria.objects.filter(dec_id=dec_id)
    return render(request,'decisions/solution_options/add_eva_criteria.html',{'qset':qset,'dec_id':dec_id, 'dec_title':dec_title, 'solopt':solopt,'created_by':created_by, 'loggedinuser':loggedinuser, 'stakeholdersNow':stakeholdersNow}) 
'''

def add_eva_criteria(request):
    context = RequestContext(request)
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    if 'created_by' in request.session:
       created_by = request.session['created_by']                                                                                                         
    else:
       created_by = 'not found'
    #if solopt_allowed == 'Y' and scrcr_allowed == 'Y': 
    if loggedinuser == created_by: 
       mapping_allowed = 'Y'
    else:
       mapping_allowed = 'N'
    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:                                                                                                                                                
       user_email = 'not found'
    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                               
       if std_count > 0:                                                                                                                                 
          stakeholdersNow = 'Y'
       else:
          stakeholdersNow = 'N'
    except ObjectDoesNotExist:                                                                                                                            
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:
       stakeholdersNow = 'Y'
    solopt = Solution_Options.objects.filter(dec_id=dec_id, archived='N')
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    
    try: 
       firstrec = Master_Evaluation_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       orig_qset = CBCSE_Evaluation_Criteria.objects.all()                                                                                                 
       for orig in orig_qset:
           orig_eva_save = Master_Evaluation_Criteria(overreaching_ec = orig.overreaching_ec, granular_ec = orig.granular_ec, suggested_evam = orig.suggested_evam, data = orig.data, dec_id = request.session['dec_id'], created_by = request.session['user'], created_date = datetime.datetime.now())        
           orig_eva_save.save()
    except MultipleObjectsReturned:                                                                                                                    
       print 'multiple rows in master evaluation criteria'

    if request.method == 'POST':
       print request.POST
       '''
       print request.POST.getlist('selected') 
       master_list = ["Addresses the identified need","Equity","External recommendations","Feasibility of implementation", "Fit with local context", "Impact on parent engagement", "Impact on parent engagement", "Impact on student academic performance", "Impact on student socio-emotional development", "Impact on student/staff engagement", "Improves teacher performance", "Meets required standards and regulations", "Quality of implementation (for programs/strategies/tools already in place)", "Support from stakeholders"]
       for val in request.POST.getlist('evacr'):     
           if val not in master_list:
              print val
           try: 
              print 'in try' 
              evadel2 = Evaluation_Criteria.objects.get(or_criterion = str(val), dec_id=dec_id)
              evadel2.delete()
           except ObjectDoesNotExist:
              print 'cannot delete something that does not exist XXX'  
           except MultipleObjectsReturned:     
              print 'multiple' 
              evadel2 = Evaluation_Criteria.objects.filter(or_criterion = str(val), dec_id=dec_id)
              for ee in evadel2:
                  ee.delete()
       '''
       for val in request.POST.getlist('hiddenfield'):                                                                                                                                                           
           if val.endswith('U'):
              print val
              print val[:-1]
              try: 
                 evadel = Evaluation_Criteria.objects.get(orig_eva_id = val[:-1], dec_id=dec_id)
                 evadel.delete()
              except ObjectDoesNotExist:
                 print 'cannot delete something that does not exist'  
       
       for value in request.POST.getlist('evacr_q'):
           #print value
            
           try:
              master_eva = Master_Evaluation_Criteria.objects.get(id = value, dec_id=dec_id)
              or_crit = master_eva.overreaching_ec
              crit =  master_eva.granular_ec
              sugg_evam = master_eva.suggested_evam
              data = master_eva.data
           except ObjectDoesNotExist:
              or_crit = ''
              crit = ''
              sugg_evam = ''
              data = ''

           try: 
              old_eva = Evaluation_Criteria.objects.get(criterion = crit, dec_id=dec_id)
              old_eva_exists = 'Y'   
           except ObjectDoesNotExist:
              old_eva_exists = 'N'

           fieldname = value + 'two'
           if old_eva_exists == 'N':  
              eva_save = Evaluation_Criteria(or_criterion = or_crit, criterion = crit, suggested_evam = sugg_evam, data = data, criterion2 = request.POST.get(fieldname), orig_eva_id = value, dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
              eva_save.save() 
           else:
               old_eva.criterion2 = request.POST.get(fieldname)
               old_eva.orig_eva_id = value
               old_eva.updated_by = request.session['user']
               old_eva.updated_date = datetime.datetime.now()                                                                                                                                                    
               old_eva.save(update_fields=['criterion2','orig_eva_id','updated_by','updated_date'])
       
       try: 
          old_eva1 = Evaluation_Criteria.objects.get(fieldname = 'cri1', dec_id=dec_id)
          old_eva1.criterion = request.POST.get('cri1')
          old_eva1.updated_by = request.session['user']
          old_eva1.updated_date = datetime.datetime.now()
          old_eva1.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri1') <> '':                                                                                                                                                                     
             eva_save1 = Evaluation_Criteria(criterion = request.POST.get('cri1'), fieldname = 'cri1', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now()) 
             eva_save1.save()

       try: 
          old_eva2 = Evaluation_Criteria.objects.get(fieldname = 'cri2', dec_id=dec_id)
          old_eva2.criterion = request.POST.get('cri2')
          old_eva2.updated_by = request.session['user']
          old_eva2.updated_date = datetime.datetime.now()
          old_eva2.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri2') <> '':                                                                                                                                                                     
             eva_save2 = Evaluation_Criteria(criterion = request.POST.get('cri2'), fieldname = 'cri2', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now()) 
             eva_save2.save()

       try: 
          old_eva3 = Evaluation_Criteria.objects.get(fieldname = 'cri3', dec_id=dec_id)
          old_eva3.criterion = request.POST.get('cri3')
          old_eva3.updated_by = request.session['user']
          old_eva3.updated_date = datetime.datetime.now()
          old_eva3.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri3') <> '':                                                                                                                                                                     
             eva_save3 = Evaluation_Criteria(criterion = request.POST.get('cri3'), fieldname = 'cri3', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save3.save()

       try: 
          old_eva4 = Evaluation_Criteria.objects.get(fieldname = 'cri4', dec_id=dec_id)
          old_eva4.criterion = request.POST.get('cri4')
          old_eva4.updated_by = request.session['user']
          old_eva4.updated_date = datetime.datetime.now()
          old_eva4.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri4') <> '':                                                                                                                                                                     
             eva_save4 = Evaluation_Criteria(criterion = request.POST.get('cri4'), fieldname = 'cri4', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save4.save()

       try: 
          old_eva5 = Evaluation_Criteria.objects.get(fieldname = 'cri5', dec_id=dec_id)
          old_eva5.criterion = request.POST.get('cri5')
          old_eva5.updated_by = request.session['user']
          old_eva5.updated_date = datetime.datetime.now()
          old_eva5.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri5') <> '':                                                                                                                                                                     
             eva_save5 = Evaluation_Criteria(criterion = request.POST.get('cri5'), fieldname = 'cri5', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save5.save()

       try: 
          old_eva6 = Evaluation_Criteria.objects.get(fieldname = 'cri6', dec_id=dec_id)
          old_eva6.criterion = request.POST.get('cri6')
          old_eva6.updated_by = request.session['user']
          old_eva6.updated_date = datetime.datetime.now()
          old_eva6.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri6') <> '':                                                                                                                                                                     
             eva_save6 = Evaluation_Criteria(criterion = request.POST.get('cri6'), fieldname = 'cri6', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save6.save()

       try: 
          old_eva7 = Evaluation_Criteria.objects.get(fieldname = 'cri7', dec_id=dec_id)
          old_eva7.criterion = request.POST.get('cri7')
          old_eva7.updated_by = request.session['user']
          old_eva7.updated_date = datetime.datetime.now()
          old_eva7.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri7') <> '':                                                                                                                                                                     
             eva_save1 = Evaluation_Criteria(criterion = request.POST.get('cri7'), fieldname = 'cri7', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save1.save()

       try: 
          old_eva8 = Evaluation_Criteria.objects.get(fieldname = 'cri8', dec_id=dec_id)
          old_eva8.criterion = request.POST.get('cri8')
          old_eva8.updated_by = request.session['user']
          old_eva8.updated_date = datetime.datetime.now()
          old_eva8.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri8') <> '':                                                                                                                                                                     
             eva_save8 = Evaluation_Criteria(criterion = request.POST.get('cri8'), fieldname = 'cri8', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save8.save()

       try: 
          old_eva9 = Evaluation_Criteria.objects.get(fieldname = 'cri9', dec_id=dec_id)
          old_eva9.criterion = request.POST.get('cri9')
          old_eva9.updated_by = request.session['user']
          old_eva9.updated_date = datetime.datetime.now()
          old_eva9.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri9') <> '':                                                                                                                                                                     
             eva_save9 = Evaluation_Criteria(criterion = request.POST.get('cri9'), fieldname = 'cri9', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save9.save()

       try: 
          old_eva10 = Evaluation_Criteria.objects.get(fieldname = 'cri10', dec_id=dec_id)
          old_eva10.criterion = request.POST.get('cri10')
          old_eva10.updated_by = request.session['user']
          old_eva10.updated_date = datetime.datetime.now()
          old_eva10.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri10') <> '':                                                                                                                                                                     
             eva_save10 = Evaluation_Criteria(criterion = request.POST.get('cri10'), fieldname = 'cri10', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save10.save()

       try: 
          old_eva1 = Evaluation_Criteria.objects.get(fieldname = 'cri1', dec_id=dec_id)
          old_eva1.criterion = request.POST.get('cri1')
          old_eva1.updated_by = request.session['user']
          old_eva1.updated_date = datetime.datetime.now()
          old_eva1.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri1') <> '':                                                                                                                                                                     
             eva_save1 = Evaluation_Criteria(criterion = request.POST.get('cri1'), fieldname = 'cri1', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save1.save()

       try: 
          old_eva11 = Evaluation_Criteria.objects.get(fieldname = 'cri11', dec_id=dec_id)
          old_eva11.criterion = request.POST.get('cri11')
          old_eva11.updated_by = request.session['user']
          old_eva11.updated_date = datetime.datetime.now()
          old_eva11.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri11') <> '':                                                                                                                                                                     
             eva_save11 = Evaluation_Criteria(criterion = request.POST.get('cri11'), fieldname = 'cri11', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save11.save()

       try: 
          old_eva12 = Evaluation_Criteria.objects.get(fieldname = 'cri12', dec_id=dec_id)
          old_eva12.criterion = request.POST.get('cri12')
          old_eva12.updated_by = request.session['user']
          old_eva12.updated_date = datetime.datetime.now()
          old_eva12.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri12') <> '':                                                                                                                                                                     
             eva_save12 = Evaluation_Criteria(criterion = request.POST.get('cri12'), fieldname = 'cri12', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save12.save()

       try: 
          old_eva13 = Evaluation_Criteria.objects.get(fieldname = 'cri13', dec_id=dec_id)
          old_eva13.criterion = request.POST.get('cri13')
          old_eva13.updated_by = request.session['user']
          old_eva13.updated_date = datetime.datetime.now()
          old_eva13.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri13') <> '':                                                                                                                                                                     
             eva_save13 = Evaluation_Criteria(criterion = request.POST.get('cri13'), fieldname = 'cri13', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save13.save()

       try: 
          old_eva14 = Evaluation_Criteria.objects.get(fieldname = 'cri14', dec_id=dec_id)
          old_eva14.criterion = request.POST.get('cri14')
          old_eva14.updated_by = request.session['user']
          old_eva14.updated_date = datetime.datetime.now()
          old_eva14.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri14') <> '':                                                                                                                                                                     
             eva_save14 = Evaluation_Criteria(criterion = request.POST.get('cri14'), fieldname = 'cri14', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())  
             eva_save14.save()

       try:
          old_eva15 = Evaluation_Criteria.objects.get(fieldname = 'cri15', dec_id=dec_id)
          old_eva15.criterion = request.POST.get('cri15')
          old_eva15.updated_by = request.session['user']
          old_eva15.updated_date = datetime.datetime.now()
          old_eva15.save(update_fields=['criterion','updated_by','updated_date'])
       except ObjectDoesNotExist:   
          if request.POST.get('cri15') <> '':                                                                                                                                                                    
             eva_save15 = Evaluation_Criteria(criterion = request.POST.get('cri15'), fieldname = 'cri15', dec_id = request.session['dec_id'], created_by = request.session['user'],created_date = datetime.datetime.now())
             eva_save15.save()

       if 'submit' in request.POST:    
           return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
       elif 'st' in request.POST:
           if stakeholdersNow == 'Y': 
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html') 
           else:
              return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_all.html')    
    qset = Master_Evaluation_Criteria.objects.filter(dec_id=dec_id)
    qset_or = qset.values('overreaching_ec').distinct()
    #qset_or_count = qset.values('overreaching_ec').distinct().count() 
    for q in qset_or:
        if q['overreaching_ec'] == 'Addresses the identified need':
           qset_add = qset.filter(overreaching_ec=q['overreaching_ec'])
        elif q['overreaching_ec'] == 'Equity':
           qset_eq = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'External recommendations':                                                                                                                                            
           qset_ext = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Feasibility of implementation':                                                                                                                                            
           qset_feas = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Fit with local context':                                                                                                                                            
           qset_loc = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Impact on parent engagement':                                                                                                                                          
           qset_pe = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Impact on student academic performance':                                                                                                                                            
           qset_aced = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Impact on student socio-emotional development':                                                                                                                                            
           qset_emot = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Impact on student/staff engagement':                                                                                                                                            
           qset_staf = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Improves teacher performance':                                                                                                                                            
           qset_teac = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Meets required standards and regulations':                                                                                                                                            
           qset_stand = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Quality of implementation (for programs/strategies/tools already in place)':                                                                                                                                            
           qset_qual = qset.filter(overreaching_ec=q['overreaching_ec']) 
        elif q['overreaching_ec'] == 'Support from stakeholders':                                                                                                                                            
           qset_stx = qset.filter(overreaching_ec=q['overreaching_ec']) 
    for qq in qset_add:
        print qq.granular_ec
    qset_g = qset.filter(overreaching_ec="Fit with local context")
    qset2 = Evaluation_Criteria.objects.filter(dec_id=dec_id)
    qset3 = qset2.exclude(orig_eva_id__isnull=False)                                                                                                      
    return render(request,'decisions/solution_options/add_eva_criteria.html',{'qset':qset_or,'qset2':qset2,'qset3':qset3,'qset_add':qset_add,'qset_eq':qset_eq,'qset_ext':qset_ext,'qset_feas':qset_feas,'qset_loc':qset_loc,'qset_pe':qset_pe,'qset_aced':qset_aced,'qset_emot':qset_emot,'qset_staf':qset_staf,'qset_teac':qset_teac,'qset_stand':qset_stand,'qset_qual':qset_qual,'qset_stx':qset_stx,'dec_id':dec_id, 'dec_title':dec_title, 'solopt':solopt,'created_by':created_by, 'loggedinuser':loggedinuser, 'stakeholdersNow':stakeholdersNow}) 
 
def add_st_evacr(request):                                                                                                                                                                                      
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and evacr_type = 'Y' and deleted is null) order by firstName", [loggedinuser, dec_id])
    stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and (evacr_type = 'Y' or deleted = 'Y')) order by firstName", [loggedinuser, dec_id])
   
    if request.method == 'POST':
        if 'id' in request.POST:
            if 'submit' in request.POST: 
               for value in request.POST.getlist('id'):
                  try:
                     old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                     old_stdec.evacr_type = 'Y' 
                     old_stdec.updated_by = request.session['user']
                     old_stdec.updated_date = datetime.datetime.now()
                     old_stdec.save(update_fields=['evacr_type','updated_by','updated_date'])
                  except ObjectDoesNotExist:
                     st = Stakeholders.objects.get(pk=value) 
                     st_dec = Stakeholders_Decisions(st_id = value, email=st.email, dec_id = request.session['dec_id'],evacr_type = 'Y',created_by = request.session['user'],created_date = datetime.datetime.now())
                     st_dec.save()
               #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)      
            else:    
                for value in request.POST.getlist('id'):
                    try: 
                       old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                       old_stdec.evacr_type = 'N' 
                       old_stdec.updated_by = request.session['user']
                       old_stdec.updated_date = datetime.datetime.now()
                       old_stdec.save(update_fields=['evacr_type','updated_by','updated_date'])
                    except ObjectDoesNotExist:
                       print 'id does not exist'
                       return HttpResponse('Selected Id does not exist in database. Please contact your Administrator.')
        else:
            return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
    return render(request,'decisions/solution_options/add_st_evacr.html',{'stakeholders':stakeholders,'st_dec': stakeholders_decisions, 'dec_id':dec_id, 'dec_title':dec_title})

def add_scores(request):
    context = RequestContext(request)
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'

    if 'user_email' in request.session:                                                                                                                                                                          
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
       eva = Evaluation_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       print 'eva' 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation criteria so you cannot view this screen.'})
    except MultipleObjectsReturned:                                                                                                                
       print 'eva multiple objects returned' 

    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                                                                                       
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  
    '''
    try:                                                                                                                                           
        setup = PA_Setup.objects.get(dec_id=dec_id)
        group_yn = setup.scores_group_yn
        votes_yn = setup.votes_yn
    except ObjectDoesNotExist:
        setup = PA_Setup(dec_id = dec_id, scores_group_yn = 'Y', votes_yn = 'N', created_date = datetime.datetime.now(), created_by = created_by)
        group_yn = setup.scores_group_yn
        votes_yn = setup.votes_yn
        setup.save()
    '''
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    qset = Importance_Scores.objects.filter(dec_id=dec_id, created_by=request.session['user'])
    eva = Evaluation_Criteria.objects.filter(dec_id=dec_id)
    ids = set(e.id for e in eva)
    print ids
    ids2 = set(q.eva_id for q in qset)
    print ids2
    mylist = ids - ids2
    for l in mylist:
        print l
        e = Evaluation_Criteria.objects.get(id=l)
        sc = Importance_Scores(eva_id = e.id, criterion = e.criterion, score = 0, dec_id = dec_id, created_by=request.session['user'], email=request.session['user_email'],created_date = datetime.datetime.now())
        sc.save()    
    qset = Importance_Scores.objects.filter(dec_id=dec_id, created_by=request.session['user']).order_by('eva_id') 

    MFormSet = modelformset_factory(Importance_Scores, form=ScoresForm, extra=0)
    if request.method == 'POST':
        scoresform = MFormSet(request.POST,request.FILES,prefix="scoresform" )
        if scoresform.is_valid():
           id = scoresform.save(commit=False)
           
           for recs in id:
               recs.updated_by = request.session['user'] 
               recs.updated_date = datetime.datetime.now()
               something_saved = 'yes'
               recs.save(update_fields=['score', 'updated_by','updated_date']) 
           if something_saved == 'yes':  
              dec.updated_by = request.session['user'] 
              dec.updated_date = datetime.datetime.now()
              dec.save(update_fields=['updated_by','updated_date'])   
           if 'submit' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
           elif 'votes' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_iw_votes.html')
           elif 'setup' in request.POST:
               return HttpResponseRedirect('/utility_tool/decisions/pa_setup.html')   
           elif 'st' in request.POST:                                                                                                                                                                            
              if stakeholdersNow == 'Y':
                 return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html') 
              else:
                 return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_all.html')  
        else:
            print scoresform.errors
    else:
        scoresform = MFormSet(queryset = qset,prefix="scoresform")
        for form in scoresform:
           form.fields['criterion'].widget.attrs['readonly'] = True 
           #form.fields['created_by'].widget.attrs['readonly'] = True
    return render(request,'decisions/solution_options/add_scores.html',{'scoresform':scoresform,'dec_id':dec_id, 'dec_title':dec_title, 'created_by':created_by, 'loggedinuser':loggedinuser, 'stakeholdersNow':stakeholdersNow}) 

def add_st_iw(request):                                                                                                                                                                                       
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and iw_type = 'Y' and deleted is null) order by firstName", [loggedinuser, dec_id])
    stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and (iw_type = 'Y' or deleted = 'Y')) order by firstName", [loggedinuser, dec_id]) 
   
    if request.method == 'POST':
        if 'id' in request.POST:
            if 'submit' in request.POST:
               for value in request.POST.getlist('id'):
                  try:
                     old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                     old_stdec.iw_type = 'Y' 
                     st = Stakeholders.objects.get(pk=value)
                     name = st.firstName + ' ' + st.lastName
                     old_stdec.name = name
                     old_stdec.updated_by = request.session['user']
                     old_stdec.updated_date = datetime.datetime.now()
                     old_stdec.save(update_fields=['iw_type','name','updated_by','updated_date'])
                  except ObjectDoesNotExist:
                     st = Stakeholders.objects.get(pk=value) 
                     name = st.firstName + ' ' + st.lastName
                     st_dec = Stakeholders_Decisions(st_id = value, name = name, email=st.email, dec_id = request.session['dec_id'],iw_type = 'Y',created_by = request.session['user'],created_date = datetime.datetime.now())
                     st_dec.save()
               #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)      
            else:
                for value in request.POST.getlist('id'):
                    try:
                       old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                       old_stdec.iw_type = 'N' 
                       old_stdec.updated_by = request.session['user']
                       old_stdec.updated_date = datetime.datetime.now()
                       old_stdec.save(update_fields=['iw_type','updated_by','updated_date']) 
                    except ObjectDoesNotExist:
                       print 'id does not exist'
                       return HttpResponse('Selected Id does not exist in database. Please contact your Administrator.')
        else:
            return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)                                                                                                                         
    return render(request,'decisions/solution_options/add_st_iw.html',{'stakeholders':stakeholders,'st_dec': stakeholders_decisions, 'dec_id':dec_id, 'dec_title':dec_title})


def add_iw_votes(request):                                                                                                                                                                                    
    context = RequestContext(request)
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'user_email' in request.session: 
       user_email = request.session['user_email']
    else:
       user_email = 'not found'

    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id)
       std_count = std.exclude(email = user_email).count()                                                                                                                                                       
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  

    qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type = 'Y')
    qset_count = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type = 'Y').count()
    total_votes = 10 * qset_count
    allowed_votes = 0

    MFormSet = modelformset_factory(Stakeholders_Decisions, form=VotesForm, extra=0)
    dec = Decisions.objects.get(pk=dec_id)
    something_saved = 'no'
 
    if request.method == 'POST':
        votesform = MFormSet(request.POST,request.FILES,prefix="votesform" )
        if votesform.is_valid():
           id = votesform.save(commit=False)
           for recs in id:
               if recs.votes is None:
                  errtext = 'Please enter the number of votes'
                  return render(request,'decisions/solution_options/add_iw_votes.html',{'votesform':votesform,'dec_id':dec_id, 'dec_title':dec_title, 'errtext':errtext, 'total_votes':total_votes, 'total_voters':qset_count})
               allowed_votes = recs.votes + allowed_votes
           print allowed_votes

           if allowed_votes > total_votes:
              errtext = 'The total number of votes cannot exceed '  + str(total_votes) + ', i.e., ten times the number of Stakeholders.' 
              return render(request,'decisions/solution_options/add_iw_votes.html',{'votesform':votesform,'dec_id':dec_id, 'dec_title':dec_title, 'errtext':errtext, 'total_votes':total_votes, 'total_voters':qset_count})
           elif allowed_votes <> total_votes:
              errtext = 'The total number of votes must be equal to ' + str(total_votes) + ', i.e., ten times the number of Stakeholders.'
              return render(request,'decisions/solution_options/add_iw_votes.html',{'votesform':votesform,'dec_id':dec_id, 'dec_title':dec_title, 'errtext':errtext, 'total_votes':total_votes, 'total_voters':qset_count}) 
           else:
               for recs in id:                                                                                                                                                                                   
                  if recs.votes <> '':
                     recs.updated_by = request.session['user'] 
                     recs.updated_date = datetime.datetime.now()
                     recs.save(update_fields=['votes','updated_by', 'updated_date'])
                     something_saved ='yes'
               if something_saved == 'yes':  
                  dec.updated_by = request.session['user'] 
                  dec.updated_date = datetime.datetime.now()
                  dec.save(update_fields=['updated_by','updated_date'])    
               if 'submit' in request.POST:
                  return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
               elif 'scores' in request.POST:
                  return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_scores.html')
               elif 'setup' in request.POST:
                  return HttpResponseRedirect('/utility_tool/decisions/pa_setup.html')                         
               elif 'st' in request.POST:     
                  if stakeholdersNow == 'Y': 
                     return HttpResponseRedirect('/utility_tool/decisions/solution_options/assign_tasks.html') 
                  else:
                     return HttpResponseRedirect('/utility_tool/decisions/solution_options/add_st_all.html')  
        else:
            print votesform.errors
    else:
        votesform = MFormSet(queryset = qset,prefix="votesform")
        for form in votesform:                                                                                                                                                                                   
           form.fields['name'].widget.attrs['readonly'] = True 
           form.fields['updated_by'].widget.attrs['readonly'] = True
           instance = getattr(form, 'instance', None)
           if not instance.votes:
              if instance.votes <> 0:
                 form.initial['votes'] = 10
    return render(request,'decisions/solution_options/add_iw_votes.html',{'votesform':votesform,'dec_id':dec_id, 'dec_title':dec_title, 'total_votes':total_votes, 'total_voters':qset_count})
   
def add_st_scrcr(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']                                                                                                                                                                  
    else:
       dec_title = 'not found'

    stakeholders_decisions = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and scrcr_type = 'Y'  and deleted is null) order by firstName", [loggedinuser, dec_id])

    stakeholders = Stakeholders.objects.raw("SELECT id, firstName, lastName, email, title, organisation from utility_tool_stakeholders where created_by=%s and id not in (SELECT st_id from utility_tool_stakeholders_decisions where dec_id = %s and (scrcr_type = 'Y' or deleted = 'Y')) order by firstName", [loggedinuser, dec_id])

    if request.method == 'POST':
        if 'id' in request.POST:
            if 'submit' in request.POST: 
                for value in request.POST.getlist('id'):
                   try:
                      old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                      old_stdec.scrcr_type = 'Y' 
                      old_stdec.updated_by = request.session['user']
                      old_stdec.updated_date = datetime.datetime.now()
                      old_stdec.save(update_fields=['scrcr_type','updated_by','updated_date'])  
                   except ObjectDoesNotExist:
                      st = Stakeholders.objects.get(pk=value) 
                      st_dec = Stakeholders_Decisions(st_id = value, email=st.email, dec_id = request.session['dec_id'],scrcr_type = 'Y',created_by = request.session['user'],created_date = datetime.datetime.now())
                      st_dec.save()
               #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)
            else:    
                for value in request.POST.getlist('id'):
                   try: 
                       old_stdec = Stakeholders_Decisions.objects.get(dec_id=dec_id,st_id=value) 
                       old_stdec.scrcr_type = 'N' 
                       old_stdec.updated_by = request.session['user']
                       old_stdec.updated_date = datetime.datetime.now()
                       old_stdec.save(update_fields=['iw_type','updated_by','updated_date'])  
                   except ObjectDoesNotExist:
                       print 'id does not exist'
                       return HttpResponse('Selected Id does not exist in database. Please contact your Administrator.')
        else:
            return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)

    return render(request,'decisions/solution_options/add_st_scrcr.html',{'stakeholders':stakeholders,'st_dec': stakeholders_decisions, 'dec_id':dec_id, 'dec_title':dec_title})

def handsontable(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'
    if 'map_list' in request.session:
       map_list = request.session['map_list']
    else:
       map_list = 'not found'
    try: 
       ss = Solution_Options.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       print 'solopt'
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered solution options so you cannot view this screen.'})
    except MultipleObjectsReturned:     
       print 'solopt multiple objects returned' 

    try: 
       ss2 = Screening_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       print 'scrcr'
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered screening criteria so you cannot view this screen.'})
    except MultipleObjectsReturned:     
       print 'scrcr multiple objects returned' 

    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    
    if request.method == 'POST':
       for array in request.POST.getlist('getdata'):
           print (array)
       # insert the handsontable into the mapping table. If it already exists, update it else, create it from Solution Options and Screening Criteria    
       try:
          h = MappingTable.objects.get(dec_id=dec_id)
          h.updated_by = request.session['user']
          h.updated_date = datetime.datetime.now()
          h.table = array
          h.save(update_fields=['table','updated_by', 'updated_date'])
       except ObjectDoesNotExist:
          h = MappingTable(table = array, dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
          h.save()     

       # remove the first [ from the array we got from ajax  
       arr = array[1:]                                                                                                                                                                                           
       # get the first and last postion of the solution options list
       firstpos = arr.find('[') + 1
       lastpos =  arr.find(']') 
       arr1 = arr[firstpos:lastpos]
       #print arr1
       #print 'arr1'
       solopt_list = []
       for l in arr1.split(','):
           ll = l.replace('"','')
           lj = ll.replace('Option: ', '')
           solopt_list.append(lj)
           #print 'in solopt list'
           #print lj    
       # remove the first and last array in the array of arrays - first one is the headings and last one is the empty row  
       a = arr.replace(arr1,'')
       b = a.replace('null,','')
       c = b.replace('[],','')
       y = c.replace(',[null]','')
       #print y
           
       firstpos = y.find('[') + 1
       lastpos =  y.find(']')
       w = y[firstpos:lastpos]
       #print 'w'
       #print w
       z = y.replace('[[','')
       v = z.replace(']]','')
       arr2 = v.replace('"],','",')
       #print 'arr2'
       #print arr2   
       temp_list = []
       # adding each array to a temporary list
       for l2 in arr2.split(','):
           l3 = l2.replace('"', '')
           #print 'l3'
           print l3
           if l3 == "Keep Option" or l3 =="Archive it":
              print l3 
              temp_list.append(l3)
       #for amm in temp_list:
           #print 'amm'
           #print amm   
       if 'Keep Option' in temp_list or 'Archive it' in temp_list:
          counter = 0
          for j in solopt_list: 
              try:
                 sol = Solution_Options.objects.get(dec_id=dec_id, sol_option = j)
                 #print 'temp list counter'
                 #print j
                 #print temp_list[counter]
                 if temp_list[counter] == "Keep Option":
                    sol.archived = "N"
                 elif  temp_list[counter] == "Archive it":
                    sol.archived = "Y"
                 sol.updated_by = request.session['user']
                 sol.updated_date = datetime.datetime.now() 
                 sol.save(update_fields=['archived','updated_by', 'updated_date'])
                 something_saved = 'yes'
                 counter = counter + 1
              except ObjectDoesNotExist:
                 print 'doesnotexist' 
   
       if something_saved == 'yes':  
          dec.updated_by = request.session['user'] 
          dec.updated_date = datetime.datetime.now()
          dec.save(update_fields=['updated_by','updated_date'])  

    solopt = Solution_Options.objects.filter(dec_id=dec_id)
    scrcr = Screening_Criteria.objects.filter(dec_id=dec_id) 
    scrcr_count = Screening_Criteria.objects.filter(dec_id=dec_id).count()
    test = []
    test2 = []
    try:
       mapping = MappingTable.objects.get(dec_id=dec_id)
       maptable =  mapping.table
       print "maptable"
       print maptable
       print 'in map list'                      
       print map_list
       for m in map_list:
           print 'am i in here'
           print m
           #print maptable.find('['+'"964"')
           #print maptable.find('["964"')
           firstposx = maptable.find('["'+ str(m) + '"') + 1
           print firstposx
           if firstposx <> 0:
              lastposx =  maptable.find(']', firstposx)
              print lastposx
              arr1 = maptable[firstposx:lastposx]
              print arr1
              test = maptable.replace(arr1, '')
              print test
              test2 = test.replace('[],', '')
              maptable = test2
              print "maptable and test2"
              print test2
              print maptable
    except ObjectDoesNotExist:
       maptable = 'doesnotexist'

    return render(request,'decisions/solution_options/handsontable.html', {'dec_id':dec_id, 'dec_title': dec_title, 'mapping':maptable, 'solopt':solopt, 'scrcr':scrcr, 'scrcr_count':scrcr_count, 'map_list':map_list})

def summary(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'  

    try: 
       eva = Evaluation_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       print 'eva' 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation criteria so you cannot view this screen.'})
    except MultipleObjectsReturned:                                                                                                                
       print 'eva multiple objects returned' 

    try:
       setup = PA_Setup.objects.get(dec_id = dec_id) 
       votes_yn = setup.votes_yn
       group_yn = setup.scores_group_yn 
    except ObjectDoesNotExist:
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered the setup information for scores so you cannot view this screen.'})

    '''
    EXAMPLE:
    Yilin: 5 votes,  importance score for criterion 1 is 90   
    Fiona: 20  votes, importance score is 80
    Amritha: 5 votes, importance score is  20

    The first step is to calculate the “vote weight” of each stakeholder. 
    Yilin: 5/30 = ⅙
    Fiona: 20/30 = ⅔
    Amritha: 5/30 = ⅙.

    The second step is to weight the importance scores of these three people for one criterion by the vote weight. 

    Weighted importance score = 90 * ⅙ + 80 * 2/3 + 20 * ⅙. 

    Then do this for each criterion. 
    The importance weight for one criterion = the weighted importance score for this criterion/ sum of weighted importance scores for all criteria.  

    try:
       getone = Importance_Scores.objects.get(dec_id = dec_id)
    except ObjectDoesNotExist:
       return HttpResponseRedirect('/utility_tool/decisions/message.html')
    ''' 
    scores = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.score score, i.created_by created_by, s.votes votes FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email order by i.criterion, i.created_by", [dec_id])
    if group_yn == 'N':  
       qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
       qset_count = 1
       qset_count = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y').count()                                                                                            
       total_votes = 10 * qset_count
       total_weight = 0
       weighted_score = 0 
       onerec = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.created_by created_by FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email order by i.criterion, i.created_by limit 1", [dec_id])

       '''
       should think of where to do this calculation 
       '''
       for one in onerec:
          idofrec = one.eva_id 
          crit = one.criterion
       for q in scores:
          if crit <> q.criterion:
             eva = Evaluation_Criteria.objects.get(id = idofrec)
             eva.weight = weighted_score
             eva.save(update_fields=['weight'])
             weighted_score = 0 
          crit = q.criterion
          idofrec = q.eva_id
         
          # if assign votes to stakeholders is Y, then use the assigned votes, if they are not available, give an error
          # if assign votes is N, then give 10 votes to each stakeholder 
          if votes_yn == 'Y': 
             if  q.votes is None:                                                                                                                                                                             
                return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not assigned the number of votes allocated to each stakeholder.'})
             vote_weight = q.votes / float(total_votes)
          else:   
             vote_weight = 10 / float(total_votes)  
 
          if q.score is None:
             q.score = 0 
          weighted_score =  float(weighted_score + (q.score * vote_weight))
 
          eva = Evaluation_Criteria.objects.get(id = idofrec)
          eva.weight = weighted_score
          total_weight = float(total_weight) + float(weighted_score)
          eva.save(update_fields=['weight']) 
          print total_weight 
          for e in Evaluation_Criteria.objects.filter(dec_id=dec_id):
             if total_weight == 0:
                e.adjusted_weight = 0
             else:   
                if e.weight is not None: 
                   e.adjusted_weight = round(float(e.weight) / float(total_weight),2)
             e.updated_by = loggedinuser                                                                                                     
             e.updated_date = datetime.datetime.now()                                                                                                
             e.save(update_fields=['adjusted_weight', 'updated_by','updated_date'])
    else:
           ''' 
           total_weight = 0
           for i in Importance_Scores.objects.filter(dec_id = dec_id, created_by = loggedinuser):
              if i.score is None:
                 i.score = 0
              total_weight = total_weight + i.score
           print total_weight
           
           for i in Importance_Scores.objects.filter(dec_id = dec_id, created_by = loggedinuser):
              if i.score is not None:
                 e = Evaluation_Criteria.objects.get(id = i.eva_id)
                 e.weight = total_weight
                 e.adjusted_weight = round(float(i.score) / float(total_weight),2)
                 e.updated_by = loggedinuser
                 e.updated_date = datetime.datetime.now()
                 e.save(update_fields=['weight','adjusted_weight', 'updated_by','updated_date'])    
            '''

    try:
      Importance_Scores.objects.get(dec_id = dec_id, created_by = loggedinuser)
    except ObjectDoesNotExist:
       print 'is' 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered importance scores so you cannot view this screen.'})
    except MultipleObjectsReturned:                                                                                                                
       print 'is multiple objects returned'

    eva_table = Evaluation_Criteria.objects.filter(dec_id = dec_id)
 
    return render(request,'decisions/solution_options/summary.html', {'dec_id':dec_id, 'dec_title': dec_title, 'scores':scores, 'eva_table':eva_table, 'group_yn':group_yn})

def utility_results(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']               
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found' 

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'

    # using a function here
    '''
    check_required(dec_id, loggedinuser, created_by)
    try:
       setup = PA_Setup.objects.get(dec_id = dec_id) 
       group_yn = setup.scores_group_yn
       votes_yn = setup.votes_yn
    except ObjectDoesNotExist:
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered the setup information for scores so you cannot view this screen. Please go back and complete the information'})
               
    if loggedinuser == created_by:
       if group_yn == 'N':
          group_cal(dec_id, loggedinuser, votes_yn)
       else:
          individual_cal(dec_id, loggedinuser)
       further_cal(dec_id, loggedinuser, request)   
    ''' 
    try: 
       evatable = EvaluationTable.objects.get(dec_id=dec_id)
       table =  evatable.table
    except ObjectDoesNotExist:
       table = 'doesnotexist'

    solopt = Solution_Options.objects.filter(dec_id=dec_id,archived='N')
    solopt_count = Solution_Options.objects.filter(dec_id=dec_id,archived='N').count()                                                                                                                           
    eva_count = Evaluation_Criteria.objects.filter(dec_id=dec_id).count()
    eva = Evaluation_Criteria.objects.filter(dec_id=dec_id)
    imp_scores = Importance_Scores.objects.filter(dec_id = dec_id, created_by = loggedinuser)
    util_res = Cost_Utility.objects.filter(dec_id = dec_id, archived = 'N').order_by('-weighted_utility') 
    qset = Evaluation_Measures.objects.filter(dec_id=dec_id).order_by('opt_id')

    return render(request,'decisions/solution_options/utility_results.html', {'dec_id':dec_id, 'dec_title': dec_title, 'table':table, 'evam':qset, 'util_res':util_res, 'solopt':solopt, 'eva_count':eva_count, 'solopt_count':solopt_count, 'imp_scores':imp_scores, 'eva':eva})
  
def add_measures(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']               
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'

    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'

    evacr = Evaluation_Criteria.objects.filter(dec_id=dec_id)           
    #for e in evacr:
        #print e.criterion
    try: 
       evatable = EvaluationTable.objects.get(dec_id=dec_id)
       table =  evatable.table
    except ObjectDoesNotExist:
       table = 'doesnotexist'
            
    evacr = Evaluation_Criteria.objects.filter(dec_id=dec_id)   
    solopt = Solution_Options.objects.filter(dec_id=dec_id,archived='N')
    #evacr_count = Evaluation_Criteria.objects.filter(dec_id=dec_id).count()                                                                                                                                     
    solopt_count = Solution_Options.objects.filter(dec_id=dec_id,archived='N').count()

    if request.method == 'POST':
       print request.POST.getlist('getdata')
       for array in request.POST.getlist('getdata'):
            print array

       # insert the handsontable into evaluation table. If it already exists, update it else create it
       try: 
          h = EvaluationTable.objects.get(dec_id=dec_id)
          h.updated_by = request.session['user']
          h.updated_date = datetime.datetime.now()
          h.table = array
          something_saved = 'yes'
          h.save(update_fields=['table','updated_by', 'updated_date'])
       except ObjectDoesNotExist:
           h = EvaluationTable(table = array, dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
           something_saved = 'yes'
           h.save()
        
       # insert into evaluation_measures - individual records with only option / criterion combination
       for s in solopt:
          for e in evacr:
             try:
                 m = Evaluation_Measures.objects.get(opt_id=s.id, eva_id = e.id)
             except ObjectDoesNotExist:
                 m = Evaluation_Measures(opt_id = s.id, sol_option = s.sol_option, eva_id = e.id, criterion = e.criterion,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
                 something_saved = 'yes' 
                 m.save()  

       new_list = []
       # remove the first [ from the array we got from ajax  
       arr = array[1:]
       # get the first and last postion of the solution options list
       firstpos = arr.find('[') + 1
       lastpos =  arr.find(']') 
       arr1 = arr[firstpos:lastpos]
       print 'arr1'
       print arr1
         
       # remove the first and last array in the array of arrays - first one is the headings and last one is the empty row  
       a = arr.replace(arr1,'')
       b = a.replace('null,','')
       c = b.replace('[],','')
       w = c.replace(',[null]','')
       print 'w'
       print w
       z = w.replace('[[','[')
       y = z.replace('"],"','","')
       print y
       # loop through the remaining array of arrays
       while len(y): 
          firstpos = y.find('[') + 1
          lastpos =  y.find(']')
          #print firstpos
          #print lastpos
          arr2 = y[firstpos:lastpos]
          #print arr2
          temp_list = []
          # adding each array to a temporary list
          for l2 in arr2.split(','):
             l3 = l2.replace('"', '')
             temp_list.append(l3)
          print temp_list  
          print len(temp_list)         
          if len(temp_list) > 7:   
             entering_loop_first_time = 6 
             for s in solopt:
                for evam in Evaluation_Measures.objects.filter(dec_id = dec_id, criterion = temp_list[0], opt_id = s.id):
                    # update each evaluation measure record with the values in the evaluation table
                    # lowest value, highest value etc. are float values
                    # higher_better is only one character
                    m = Evaluation_Measures.objects.get(id = evam.id) 
                    #measure | unit | lowest_value | highest_value | higher_better | option_value
                    m.measure = temp_list[1]
                    print temp_list[1]
                    m.unit = temp_list[2]
                    m.lowest_value = float(temp_list[3])
                    m.highest_value = float(temp_list[4])
                    m.higher_better = temp_list[5][0][0]
                    #print s.id
                    #print entering_loop_first_time
                    if entering_loop_first_time == 6:
                       m.option_value = float(temp_list[6])  
                       entering_loop_first_time = entering_loop_first_time + 1
                    else:
                       m.option_value = float(temp_list[entering_loop_first_time])   
                       entering_loop_first_time = entering_loop_first_time + 1
                    m.updated_by = request.session['user']
                    m.updated_date = datetime.datetime.now() 
                    m.save(update_fields=['measure','unit','lowest_value','highest_value', 'higher_better', 'option_value', 'updated_by', 'updated_date'])
                    something_saved ='yes'
          # till here  
          z = y.replace(arr2, '')
          c = z.replace('[],','')
          # break out of the loop when only []] remains
          if (c == '[]]'):
             break;
          y = c

       if something_saved == 'yes':  
          dec.updated_by = request.session['user'] 
          dec.updated_date = datetime.datetime.now()
          dec.save(update_fields=['updated_by','updated_date'])  
       #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)       
    return render(request,'decisions/solution_options/add_measures.html', {'dec_id':dec_id, 'dec_title': dec_title, 'evacr':evacr, 'table':table, 'solopt':solopt,  'solopt_count':solopt_count, 'loggedinuser':loggedinuser, 'created_by':created_by})

'''
def add_eva_results(request):
    if 'dec_id' in request.session:
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']               
    else:
       dec_title = 'not found'
    dec = Decisions.objects.get(pk=dec_id) 
    something_saved = 'no'
    if request.method == 'POST':
       print request.POST.getlist('getdata')
       for array in request.POST.getlist('getdata'):
          print (array)
          # insert the handsontable into evaluation_measures table. If it already exists, update it else create it
       try:
          h = Evaluation_Measures.objects.get(dec_id=dec_id)
          h.updated_by = request.session['user']
          h.updated_date = datetime.datetime.now()
          h.table = array
          something_saved = 'yes'
          h.save(update_fields=['table','updated_by', 'updated_date'])
       except ObjectDoesNotExist:
          h = Evaluation_Measures(table = array, dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
          something_saved = 'yes' 
          h.save()      
       if something_saved == 'yes':  
          dec.updated_by = request.session['user'] 
          dec.updated_date = datetime.datetime.now()
          dec.save(update_fields=['updated_by','updated_date'])  
    evacr = Evaluation_Criteria.objects.filter(dec_id=dec_id)      
    for e in evacr:
        print e.criterion
    try:
       evatable = Evaluation_Measures.objects.get(dec_id=dec_id)
       table =  evatable.table
    except ObjectDoesNotExist:
       table = 'doesnotexist'
    evacr = Evaluation_Criteria.objects.filter(dec_id=dec_id)   
    return render(request,'decisions/solution_options/add_eva_results.html', {'dec_id':dec_id, 'dec_title': dec_title, 'evacr':evacr, 'table':table})


def cost_setup(request):
    if 'dec_id' in request.session:                                                                                                                
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']     
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'
 
    context = RequestContext(request)

    try: 
       c = Cost_Setup.objects.get(dec_id = dec_id) 
    except ObjectDoesNotExist: 
       c = Cost_Setup(type_of_cost = 'Total', dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
       c.save()  
       c = Cost_Setup.objects.get(dec_id = dec_id) 

    dec = Decisions.objects.get(pk=dec_id) 
    if request.method == 'POST':
        print request.POST.get('no_of_part')
        setupform = CostSetupForm(request.POST)
        if setupform.is_valid():
           id = setupform.save(commit=False) 
           c.updated_by = request.session['user']
           c.updated_date = datetime.datetime.now()
           c.type_of_cost = id.type_of_cost
           c.save(update_fields=['type_of_cost', 'updated_by','updated_date',])
           dec.updated_by = request.session['user'] 
           dec.updated_date = datetime.datetime.now()
           dec.save(update_fields=['updated_by','updated_date'])
           return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id)  
        else:
            print setupform.errors
    else:
        setupform = CostSetupForm(instance=c)

        if loggedinuser != created_by:
           setupform.fields['type_of_cost'].widget.attrs['disabled'] = True
    return render(request,'decisions/solution_options/costs1.html',{'dec_id':dec_id, 'dec_title':dec_title, 'setupform':setupform, 'loggedinuser':loggedinuser, 'created_by':created_by})
'''
def cost_table(request):                                                                                                                           
    if 'dec_id' in request.session:                                                                                                                
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']     
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'
 
    context = RequestContext(request)
    dec = Decisions.objects.get(pk=dec_id) 
    try: 
       c = Cost_Setup.objects.get(dec_id = dec_id) 
       type_of_cost = c.type_of_cost
       if type_of_cost == "Total":
          cost_text = "Total Cost"
       elif type_of_cost == "Avg":
          cost_text = "Average Cost"
       else:
          cost_text = "Marginal Cost"
    except ObjectDoesNotExist: 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered costs so you cannot view this screen.'})   

    try:
       costs = Cost_Utility.objects.get(dec_id = dec_id)
    except ObjectDoesNotExist:
       for s in Solution_Options.objects.filter(dec_id=dec_id,archived='N'):
           costs  = Cost_Utility(opt_id = s.id, sol_option = s.sol_option,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
           costs.save()
       dec.updated_by = request.session['user'] 
       dec.updated_date = datetime.datetime.now()
       dec.save(update_fields=['updated_by','updated_date'])          
    except MultipleObjectsReturned:
       print 'multiple objects returned'

    costs = Cost_Utility.objects.filter(dec_id = dec_id, archived = 'N')

    if request.method == 'POST':
       #print request.POST.get('id') 
       if 'id' in request.POST:
          #changed = False
          c = Cost_Utility.objects.get(pk=request.POST.get('id'))
          '''
          if int(c.no_of_participants) != int(request.POST.get('no_of_participants')):
             c.no_of_participants = request.POST.get('no_of_participants')
             changed = True 
          if float(c.cost) != float(request.POST.get('cost')):
             c.cost = request.POST.get('cost')
             changed = True

          if changed == True:
          '''
          if request.POST.get('no_of_participants') == "None":
             c.no_of_participants = 0
          else:
             c.no_of_participants = request.POST.get('no_of_participants')
          c.cost = request.POST.get('cost')
          c.updated_by = request.session['user']
          c.updated_date = datetime.datetime.now()
          c.save(update_fields=['no_of_participants','cost','updated_by','updated_date'])
          dec.updated_by = request.session['user'] 
          dec.updated_date = datetime.datetime.now()
          dec.save(update_fields=['updated_by','updated_date'])
       #return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id) 

    return render(request,'decisions/solution_options/cost_table.html',{'dec_id':dec_id, 'dec_title':dec_title, 'costs_table':costs, 'type_of_cost':type_of_cost, 'cost_text':cost_text, 'loggedinuser':loggedinuser, 'created_by':created_by})


def cost_setup(request):
    if 'dec_id' in request.session:                                                                                                                
       dec_id = request.session['dec_id']
    else:
       dec_id = 0
    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']     
    else:
       dec_title = 'not found'
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'
    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'
 
    context = RequestContext(request)
    print 'I AM IN COST SETUP'
    try: 
       c = Cost_Setup.objects.get(dec_id = dec_id) 
       type_of_cost = c.type_of_cost
       if type_of_cost == "Total":
          cost_text = "Total Costs"
       elif type_of_cost == "Avg":
          cost_text = "Average Costs"
       else:                                                                                                                                                                                                     
          cost_text = "Marginal Costs"
    except ObjectDoesNotExist:
       c = Cost_Setup(type_of_cost = 'Total', dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
       c.save()  
       c = Cost_Setup.objects.get(dec_id = dec_id) 
       type_of_cost = c.type_of_cost
       if type_of_cost == "Total":
          cost_text = "Total Costs"
       elif type_of_cost == "Avg":
          cost_text = "Average Costs"
       else:
          cost_text = "Marginal Costs"

    dec = Decisions.objects.get(pk=dec_id) 

    for s in Solution_Options.objects.filter(dec_id=dec_id, archived = 'N'):
        try:
           costs = Cost_Utility.objects.get(opt_id = s.id)
           if costs.sol_option <> s.sol_option:
              costs.sol_option = s.sol_option
              costs.archived = s.archived
              costs.updated_by = request.session['user']
              costs.updated_date = datetime.datetime.now()
              costs.save(update_fields=['sol_option','archived','updated_by','updated_date'])
        except ObjectDoesNotExist:
           costs  = Cost_Utility(opt_id = s.id, sol_option = s.sol_option, archived = s.archived,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
           costs.save()
          
        try: 
           detcosts = Detailed_Costs.objects.get(opt_id = s.id)
           if s.archived == 'Y':
              Detailed_Costs.objects.get(opt_id = s.id).delete()
           elif detcosts.sol_option <> s.sol_option:
              detcosts.sol_option = s.sol_option
              detcosts.updated_by = request.session['user']
              detcosts.updated_date = datetime.datetime.now()
              detcosts.save(update_fields=['sol_option','updated_by','updated_date'])
        except ObjectDoesNotExist:
           if s.archived == 'N':  
              detcosts  = Detailed_Costs(opt_id = s.id, sol_option = s.sol_option,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
              detcosts.save()
    '''       
    try:
       costs = Cost_Utility.objects.get(dec_id = dec_id)
    except ObjectDoesNotExist:
       for s in Solution_Options.objects.filter(dec_id=dec_id,archived='N'):
           costs  = Cost_Utility(opt_id = s.id, sol_option = s.sol_option,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
           costs.save()
       dec.updated_by = request.session['user'] 
       dec.updated_date = datetime.datetime.now()
       dec.save(update_fields=['updated_by','updated_date'])          
    except MultipleObjectsReturned:
       print 'multiple objects returned'
    ''' 
    cost_table = Cost_Utility.objects.filter(dec_id = dec_id, archived <> 'Y')
    '''
    try: 
       detcosts = Detailed_Costs.objects.get(dec_id = dec_id)
    except ObjectDoesNotExist:
       for s in Solution_Options.objects.filter(dec_id=dec_id,archived='N'):
           detcosts  = Detailed_Costs(opt_id = s.id, sol_option = s.sol_option,  dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
           detcosts.save()
    except MultipleObjectsReturned:
       print 'multiple objects returned'
    '''
    detcosts = Detailed_Costs.objects.filter(dec_id = dec_id)

    if request.method == 'POST':
       if request.POST.get('id'): 
          costs = Cost_Utility.objects.get(pk=request.POST.get('id'))
          if request.POST.get('no_of_participants') == "None":
             costs.no_of_participants = 0
          else:
             costs.no_of_participants = request.POST.get('no_of_participants')
          costs.cost = request.POST.get('cost')
          costs.updated_by = request.session['user']
          costs.updated_date = datetime.datetime.now()
          print request.POST.get('cost')
          costs.save(update_fields=['no_of_participants','cost','updated_by','updated_date'])
          c.type_of_cost = request.POST.get('radioValue')
          c.updated_by = request.session['user']
          c.updated_date = datetime.datetime.now()
          c.save(update_fields=['type_of_cost','updated_by','updated_date'])
          type_of_cost = c.type_of_cost
          if type_of_cost == "Total":
             cost_text = "Total Cost"
          elif type_of_cost == "Avg":
             cost_text = "Average Cost"
          else:
             cost_text = "Marginal Cost"    
       if request.POST.get('d_id'):
          dcosts = Detailed_Costs.objects.get(pk=request.POST.get('d_id'))
          dcosts.personnel_cost = request.POST.get('personnel_cost')
          dcosts.facilities_cost = request.POST.get('facilities_cost')
          dcosts.materials_cost = request.POST.get('materials_cost')
          dcosts.training_cost = request.POST.get('training_cost')
          dcosts.other_cost = request.POST.get('other_cost')
          dcosts.total_cost = float(request.POST.get('personnel_cost')) + float(request.POST.get('facilities_cost'))  + float(request.POST.get('materials_cost')) + float(request.POST.get('training_cost'))  + float(request.POST.get('other_cost')) 
          dcosts.updated_by = request.session['user']
          dcosts.updated_date = datetime.datetime.now()
          dcosts.save(update_fields=['personnel_cost','facilities_cost','materials_cost','training_cost','other_cost','total_cost','updated_by','updated_date'])
    return render(request,'decisions/solution_options/costs1.html',{'dec_id':dec_id, 'dec_title':dec_title, 'loggedinuser':loggedinuser, 'created_by':created_by, 'type_of_cost':type_of_cost, 'cost_text':cost_text, 'cost_table':cost_table, 'detcosts':detcosts})

def decision_made(request):                                                                                                                                                                                         
    if 'dec_id' in request.session:                                                                                                                     
       dec_id = request.session['dec_id']
    else:
       dec_id = 0

    if 'dec_title' in request.session:
       dec_title = request.session['dec_title']          
    else:
       dec_title = 'not found'

    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    if 'created_by' in request.session:
       created_by = request.session['created_by']
    else:
       created_by = 'not found'
 
    if 'user_email' in request.session: 
       user_email = request.session['user_email']                                                                                                     
    else:
       user_email = 'not found'

    context = RequestContext(request)
    
       # using a function here
    check_required(request, dec_id, loggedinuser, created_by)
    '''
    try:
       setup = PA_Setup.objects.get(dec_id = dec_id) 
       group_yn = setup.scores_group_yn
       votes_yn = setup.votes_yn
    except ObjectDoesNotExist:
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered the setup information for scores so you cannot view this screen.'})
    ''' 
    try: 
       std = Stakeholders_Decisions.objects.filter(dec_id = dec_id, iw_type = 'Y')                                                                                   
       std_count = std.exclude(email = user_email).count()                                                                                            
       if std_count > 0: 
          stakeholdersNow = 'Y'   
       else:
          stakeholdersNow = 'N'  
    except ObjectDoesNotExist:
       stakeholdersNow = 'N'
    except MultipleObjectsReturned:                                                                                                                
       stakeholdersNow = 'Y'  
    print 'in dec made'          
    if loggedinuser == created_by:
       print stakeholdersNow 
       if stakeholdersNow == 'Y':
          individual_cal(dec_id, loggedinuser, request)
       else:
          print 'before group cal' 
          group_cal(dec_id, loggedinuser, request)
       further_cal(dec_id, loggedinuser, request)   

    try: 
       c = Cost_Setup.objects.get(dec_id = dec_id) 
       type_of_cost = c.type_of_cost
       if type_of_cost == "Total":
          cost_text = "Total Cost"
       elif type_of_cost == "Avg":
          cost_text = "Average Cost"
       else:                                                                                                                                                                                                     
          cost_text = "Marginal Cost"
    except ObjectDoesNotExist:
       return render(request,'decisions/message.html', {'dec_id':dec_id,'mess':'You have not entered costs so you cannot view this screen.'})   
    
    try: 
       costs = Cost_Utility.objects.get(dec_id = dec_id)
       if costs.cost is None or costs.weighted_utility is None:
          return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered costs so you cannot view this screen.'})   
    except ObjectDoesNotExist:
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered costs so you cannot view this screen.'})  
    except MultipleObjectsReturned:
       print 'multiple objects returned'

    cost_utility = Cost_Utility.objects.filter(dec_id = dec_id,archived = 'N')
    dec = Decisions.objects.get(pk=dec_id) 
    for cu in cost_utility:
        print cu.sol_option
        cu.type_of_cost = type_of_cost
        if cu.weighted_utility is not None and cu.cost is not None:
           if cu.weighted_utility <> 0: 
              cu.cost_utility_ratio = "%.2f" %  round(float(cu.cost) / float(cu.weighted_utility),2)
           else:
              cu.cost_utility_ratio = None
        cu.updated_by = request.session['user']
        cu.updated_date = datetime.datetime.now()
        cu.save(update_fields=['type_of_cost','cost_utility_ratio','updated_by','updated_date'])    
        dec.updated_by = request.session['user']
        dec.updated_date = datetime.datetime.now()
        dec.save(update_fields=['updated_by','updated_date'])
    cc = cost_utility.order_by('-weighted_utility')
    #onerec = cc.first()                                                                                                                                                                                     
    #wu = onerec.weighted_utility 
    #so1 = onerec.sol_option
   
    #cd = cost_utility.order_by('cost')
    #onerec2 = cd.first()                                                                                                                                                                                     
    #co = onerec2.cost
    #so2 = onerec2.sol_option

    #ce = cost_utility.order_by('cost_utility_ratio')                                                                                                                                                                          
    #onerec3 = ce.first()                                                                                                                                                                                     
    #cur = onerec3.cost_utility_ratio
    #so3 = onerec3.sol_option

    onerec = cc.first()
    type_of_cost = onerec.type_of_cost
    wu = onerec.weighted_utility
    so1 = ""
    for c in cc:
        if wu == c.weighted_utility:
          if so1 <> "":
             so1 = so1 + ", " + c.sol_option
          else:
             so1 = so1 + " " + c.sol_option 
        else: 
           so1 = onerec.sol_option         
            
    cd = cost_utility.order_by('cost')
    onerec2 = cd.first()                                                                                                                                                                                     
    co = onerec2.cost
    so2 = ""
    for c in cd:
        if co == c.cost:
           if so2 <> "":
              so2 = so2 + ", " + c.sol_option
           else:
              so2 = so2 + " " + c.sol_option
        else: 
           so2 = onerec2.sol_option 

    ce = cost_utility.order_by('cost_utility_ratio')                                                                                                                                                          
    onerec3 = ce.first()                                                                                                                                                                                     
    cur = onerec3.cost_utility_ratio
    so3 = ""
    for c in ce:
        if cur == c.cost_utility_ratio:
           if so3 <> "":
              so3 = so3 + ", " + c.sol_option
           else:
              so3 = so3 + " " + c.sol_option 
        else: 
           so3 = onerec3.sol_option 
    try: 
       dec_made = Decision_Made.objects.get(dec_id = dec_id)                                                                                                                                                         
       reason = dec_made.reason
       sol_opt = dec_made.sol_option
       none = dec_made.none
    except ObjectDoesNotExist:
       dec_made  = Decision_Made(dec_id = dec_id,created_by = request.session['user'],created_date = datetime.datetime.now())
       reason = ''
       sol_opt = ''
       none = ''
       dec_made.save() 
       dec.updated_by = request.session['user']
       dec.updated_date = datetime.datetime.now()
       dec.save(update_fields=['updated_by','updated_date'])

    query = Solution_Options.objects.filter(dec_id = dec_id, archived = 'N')
    if request.method == 'POST':
       #print request.POST.getlist('id') 
       mystring = request.POST.get('reason')
       mystring = mystring.replace('\n', '##').replace('\r', '')
       dec_made.updated_by = request.session['user']
       dec_made.updated_date = datetime.datetime.now()
       dec_made.reason = mystring
       dec_made.sol_option = request.POST.getlist('id') 
       dec_made.none = request.POST.get('none')
       dec_made.save(update_fields=['sol_option','reason', 'none','updated_by','updated_date'])
       dec.updated_by = request.session['user']
       dec.updated_date = datetime.datetime.now()
       dec.save(update_fields=['updated_by','updated_date'])             
       return HttpResponseRedirect('/utility_tool/decisions/%s/menu.html' % dec_id) 
        
       #if loggedinuser != created_by:
           #decmadeform.fields['sol_option'].widget.attrs['disabled'] = True
           #decmadeform.fields['reason'].widget.attrs['disabled'] = True
    return render(request,'decisions/solution_options/decision_made.html',{'query':query,'dec_id':dec_id, 'dec_title':dec_title, 'cost_utility':cost_utility, 'loggedinuser':loggedinuser, 'created_by':created_by, 'cost_text':cost_text, 'reason': reason, 'sol_opt': sol_opt, 'noneX':none, 'wu':wu,'so1':so1, 'co':co, 'so2':so2, 'cur':cur, 'so3':so3}) 

# Pa_setup, Add_iw_votes, Summary table, Utility results, Check add_measures, Cost_setup, Cost_table, Cost_utility, Decision_made
# when registration code is written, the new user created should be added as a stakeholder
def login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        loginform = LoginForm(data=request.POST)
        if loginform.is_valid():
           login = loginform.save(commit=False)
           request.session['user'] = login.user
            #request.session['password'] = login.password
           try:
               #login2 = m.Login.objects.filter(user=login.user).latest('startDate')
               login2 = Users.objects.get(user = login.user)
               request.session['user_email'] = login2.email 
               return HttpResponseRedirect('/utility_tool/decisions/decisions_list.html')
           except ObjectDoesNotExist:
               return render_to_response('users/login.html',{'loginform': loginform, 'err': 'Invalid user or password'}, context)

        else:
           form_errors = 'Yes'
           print form_errors

    else:
        loginform = LoginForm()

    return render(request,'users/login.html', {'loginform':loginform})

def register(request):
   context = RequestContext(request)
   if request.method == 'POST':
      registerform = RegisterForm(data=request.POST)
      if registerform.is_valid():
         register = registerform.save(commit=False)
         try: 
            r = Users.objects.filter(email = register.email).count()                                                                                                                
            if r > 0: 
               return render_to_response('users/register.html',{'registerform': registerform,'err':'Another user has the same email address entered. Please enter a different email address.'}, context)
         except ObjectDoesNotExist:
             print 'something wrong in email unique check'
         try: 
            r = Users.objects.filter(user = register.user).count()                                                                                                                
            if r > 0: 
               return render_to_response('users/register.html',{'registerform': registerform,'err':'Another user has the same user name entered. Please enter a different user name.'}, context)
         except ObjectDoesNotExist:
             print 'something wrong in email unique check'
         if register.password != register.passwordagain:                                                                                   
            return render_to_response('users/register.html',{'registerform': registerform, 'err': 'Password does not match Confirm Password.'}, context)              
         if register.email != register.emailagain:
            return render_to_response('users/register.html',{'registerform': registerform, 'err': 'Email address does not match Confirm Email address.'}, context)
         register.save()
         st = Stakeholders(firstName = register.firstName, lastName = register.lastName, email=register.email, created_by = register.user, created_date = datetime.datetime.now())
         st.save()
         return HttpResponseRedirect('/utility_tool/users/login.html') 
      else:
         print registerform.errors
          
   else:                                                                                                                            
      registerform = RegisterForm()
                                                             
   return render(request, 'users/register.html',{'registerform': registerform})

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    if 'user_email' in request.session:
       del request.session['user_email']
    if 'dec_id' in request.session:
       del request.session['dec_id']

    return render(request,'about.html')

def import_excel(request):                                                                                                                                                                                       
    # Open the workbook and define the worksheet
    book = xlrd.open_workbook("/home/amritha/costutility/documents/Stakeholders.xlsx")
    sheet = book.sheet_by_name("Stakeholders")
    
    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costutility")
    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    
    # Create the INSERT INTO sql query
    query = """INSERT INTO utility_tool_stakeholders (firstName, lastName, title, organisation, email, phone, notes, created_by, created_date) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)""" 
    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    
    for r in range(1, sheet.nrows):
        firstName = sheet.cell(r,0).value
        lastName = sheet.cell(r,1).value
        title = sheet.cell(r,2).value
        organisation = sheet.cell(r,3).value
        email = sheet.cell(r,4).value
        phone = sheet.cell(r,5).value
        notes = sheet.cell(r,6).value
        created_by = request.session['user']
        created_date = datetime.datetime.now()
        # Assign values from each row
        values = (firstName, lastName, title, organisation, email, phone, notes,created_by, created_date)
        # Execute sql Query
        cursor.execute(query, values)
    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()
    
    # Close the database connection
    database.close()
    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/utility_tool/stakeholders/stakeholders.html')

def export_stakeholders(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mystakeholders.xls'                                                                                                                            
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Stakeholders")
    row_num = 0
    
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costutility")
    user = request.session['user']
    cursor = database.cursor ()
    # Create the INSERT INTO sql query
    sql = """SELECT firstName, lastName, title, organisation, email, phone, notes FROM utility_tool_stakeholders WHERE created_by = %(user)s"""
    columns = [
        (u"First Name", 6000),
        (u"Last Name", 6000),
        (u"Title", 6000),
        (u"Organization", 12000),
        (u"Email", 8000),
        (u"Phone", 6000),
        (u"Notes", 20000)
    ]
    
    a = xlwt.Alignment()
    a.wrap = True 
    a.vert = a.VERT_CENTER
    a.horz = a.HORZ_CENTER
    font_style = xlwt.XFStyle()
    font_style.font.bold = True 
    font_style.alignment = a

    aL = xlwt.Alignment()
    aL.horz = a.HORZ_LEFT
    aL.wrap = True
    font_style2 = xlwt.XFStyle()
    font_style2.alignment = aL

    for col_num in xrange(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]
    try:
    # Execute the SQL command
       cursor.execute(sql,{'user' : user})
       # Fetch all the rows in a list of lists.
       results = cursor.fetchall()
       for row in results:
          row_num += 1
          firstName = row[0]
          lastName = row[1]
          title = row[2]
          organisation = row[3]
          email = row[4]
          phone = row[5] 
          notes = row[6]
          for col_num in xrange(len(row)):
             ws.write(row_num, col_num, row[col_num], font_style2)
    except:
       print "Error: unable to fetch data"
    # disconnect from server
    database.close()
    wb.save(response)
    return response

def imports(request):                                                                                                                                    
    if 'user' in request.session:
       loggedinuser = request.session['user']
    else:
       loggedinuser = 'not found'

    return render(request,'admin/imports.html', {'loggedinuser':loggedinuser})

def import_cbcse_scrcr(request):
    # Open the workbook and define the worksheet                                                                                                         
    book = xlrd.open_workbook("/home/amritha/costutility/documents/CBCSE_screening_criteria.xlsx")
    sheet = book.sheet_by_name("Sheet1")
    CBCSE_Screening_Criteria.objects.all().delete()
    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costutility")
    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    # Create the INSERT INTO sql query
    query = """INSERT INTO utility_tool_cbcse_screening_criteria (criterion) VALUES (%s)"""
    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        print sheet.cell(r,0).value
        list_one      = str(sheet.cell(r,0).value)
        # Execute sql Query
        cursor.execute(query, (list_one,))
    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()
    # Close the database connection
    database.close()
    columns = str(sheet.ncols)                                                                                                                           
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/utility_tool/admin/imports.html')

def import_cbcse_evacr(request):
    # Open the workbook and define the worksheet                                                                                                         
    book = xlrd.open_workbook("/home/amritha/costutility/documents/CBCSE_evaluation_criteria.xlsx")
    sheet = book.sheet_by_name("Granular evaluation criteria")
    CBCSE_Evaluation_Criteria.objects.all().delete()
    # Establish a MySQL connection
    database = MySQLdb.connect (host="amritha.mysql.pythonanywhere-services.com", user = "amritha", passwd = "lilies19", charset="utf8", db = "amritha$costutility")    
    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()
    # Create the INSERT INTO sql query
    query = """INSERT INTO utility_tool_cbcse_evaluation_criteria (overreaching_ec, granular_ec, suggested_evam, data) VALUES (%s, %s, %s, %s)"""
    # Create a For loop to iterate through each row in the XLS file, starting at row 2 to skip the headers
    for r in range(1, sheet.nrows):
        orec = str(sheet.cell(r,0).value)
        gran = str(sheet.cell(r,1).value)                                                                                
        sugg = str(sheet.cell(r,2).value)
        data = str(sheet.cell(r,3).value)        
        values  = (orec, gran, sugg, data)
        # Execute sql Query
        cursor.execute(query, values)
    # Close the cursor
    cursor.close()
    # Commit the transaction
    database.commit()
    # Close the database connection
    database.close()
    columns = str(sheet.ncols)                                                                                                                           
    rows = str(sheet.nrows)
    return HttpResponseRedirect('/utility_tool/admin/imports.html')
