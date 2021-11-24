from __future__ import division
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned                                                                                                                                  
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect,render, render_to_response
from .models import Decisions, Solution_Options, Screening_Criteria, Evaluation_Criteria, Importance_Scores, Users, Stakeholders, Stakeholders_Decisions, MappingTable, SummaryTable, Evaluation_Measures, PA_Setup, EvaluationTable,  Cost_Setup, Cost_Utility, Decision_Made, Detailed_Costs
import datetime 
import math

def check_required(request, dec_id, loggedinuser, created_by):
    ids = {}
    ids2 = {}
    ids3 = {}
    ids4 = {}
    ids5 = {} 
    retval = ''
    try:
       solopt = Solution_Options.objects.get(dec_id=dec_id,archived='N')
    except ObjectDoesNotExist:
       retval = 'solopt'
    except MultipleObjectsReturned:                                                                                                           
       print 'solopt multiple objects returned'
       solopt = Solution_Options.objects.filter(dec_id=dec_id,archived='N')
       ids = set(s.id for s in solopt) 
       print ids
      
    try: 
       eva = Evaluation_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
        retval = retval +  ',eva' 
    except MultipleObjectsReturned:                                                                                                                
       print 'eva multiple objects returned' 
       eva = Evaluation_Criteria.objects.filter(dec_id=dec_id).exclude(deleted = 'Y') 
       ids3 = set(q.id for q in eva)
       print ids3

    try: 
       Importance_Scores.objects.get(dec_id = dec_id, created_by = loggedinuser)
    except ObjectDoesNotExist:
       retval = retval + ',iw'
    except MultipleObjectsReturned:                                                                                                                
       print 'iw multiple objects returned' 
       i = Importance_Scores.objects.filter(dec_id=dec_id, created_by = loggedinuser).exclude(deleted = 'Y')
       ids5 = set(q.eva_id for q in i)
       print ids5

    try: 
       qset = Evaluation_Measures.objects.get(dec_id=dec_id, archived = 'N')
    except ObjectDoesNotExist:
       retval = retval + ',mea' 
       #return HttpResponseRedirect('/utility_tool/decisions/message.html')
    except MultipleObjectsReturned:                                                                                                                     
       print 'evam multiple objects returned'
       qset1 = Evaluation_Measures.objects.filter(dec_id=dec_id, archived = 'N') 
       qset = qset1.exclude(deleted = 'Y')   
       ids2 = set(q.opt_id for q in qset)
       print ids2                                                                                                                                                                                                
       ids4 = set(q.eva_id for q in qset)
       print ids4

    if ids != {} and ids2 != {}:
       mylist = ids - ids2 
       for l in mylist:
           retval = retval + ' ,listerr1'
    if ids3 != {} and ids4 != {}:
       mylist2 = ids3 - ids4 
       for l in mylist2:
           retval = retval + ' ,listerr2' 
    if ids3 != {} and ids5 != {}:
       mylist3 = ids3 - ids5 
       for l in mylist3:
           retval = retval + ' ,listerr3' 
    return retval

def group_cal(dec_id, loggedinuser, request):
    scores = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.score score, i.created_by created_by, s.votes votes FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type= 'Y' AND i.email = s.email AND (i.deleted = 'N' OR i.deleted IS NULL) order by i.criterion, i.created_by", [dec_id])
    print 'in here group cal'                   
    qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
    qset_count = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y').count()                          
    #total_votes = 10 * qset_count
    weighted_score = 0 
    total_weight = 0
    '''
    onerec = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.created_by created_by FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email AND (i.deleted = 'N' OR i.deleted IS NULL) order by i.criterion, i.created_by limit 1", [dec_id])   
    print 'in here' 
    for one in onerec:                                                                                                                       
        idofrec = one.eva_ne 
        print idofrec 
        crit = one.criterion
    '''    
    for q in scores:
        eva = Evaluation_Criteria.objects.get(id = q.eva_id)
        eva.weight = q.score
        print 'SCORE!'
        print eva.weight
        total_weight = float(total_weight) + float(eva.weight)
        eva.save(update_fields=['weight'])
        #weighted_score = 0 
        #crit = q.criterion
        #idofrec = q.eva_id
        # if assign votes to stakeholders is Y, then use the assigned votes, if they are not available, give an error
        # if assign votes is N, then give 10 votes to each stakeholder  
        #if votes_yn == 'Y':
        '''
        if  q.votes is None:
            q.votes = 10 
            print "q.votes"
            print q.votes 
            #return render(request,'decisions/.html', {'dec_id':dec_id, 'mess':'You have not assigned the number of votes allocated to each stakeholder.'})  
            vote_weight = q.votes / float(total_votes)
        else:   
            vote_weight = 10 / float(total_votes) 
        if q.score is None:
           q.score = 0 
        weighted_score =  float(weighted_score) + (float(q.score) * float(vote_weight))                                                       
        print 'weighted score'
        print weighted_score
    print idofrec
    eva = Evaluation_Criteria.objects.get(id = idofrec)
    eva.weight = weighted_score
    total_weight = float(total_weight) + float(weighted_score)
    eva.save(update_fields=['weight']) 
    print total_weight 
    '''
    for e in Evaluation_Criteria.objects.filter(dec_id=dec_id).exclude(deleted = 'Y') :
       if total_weight == 0:
          e.adjusted_weight = 0
       else:  
          if e.weight is not None: 
             e.adjusted_weight = float(e.weight) / float(total_weight)
       #e.weight = total_weight
       print 'what is going on'
       print e.weight
       print e.adjusted_weight
       print 'total weight'
       print total_weight
       e.updated_by = loggedinuser                                                                                                     
       e.updated_date = datetime.datetime.now()                                                                                              
       e.save(update_fields=['adjusted_weight', 'updated_by','updated_date'])
    return 1

def individual_cal(dec_id, loggedinuser, request):
    scores = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.score score, i.created_by created_by, s.votes votes FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email AND (i.deleted = 'N' OR i.deleted IS NULL) order by i.criterion, i.created_by", [dec_id])
    qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
    qset_count = 1
    qset_count = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y').count()                                
    total_votes = 10 * qset_count
    total_weight = 0
    weighted_score = 0 
    total_weighted_score = 0  
    # get first criterion
    onerec = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.created_by created_by FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email AND (i.deleted = 'N' OR i.deleted IS NULL) order by i.criterion, i.created_by limit 1", [dec_id])
    for one in onerec:
        idofrec = one.eva_id 
        crit = one.criterion
    for q in scores:
        print 'criterion'
        print q.eva_id
        # get total weighted score for EACH criterion
        # then set total weighted score to 0 and weighted score to 0 
        print idofrec
        if idofrec != q.eva_id:
          eva = Evaluation_Criteria.objects.get(id = idofrec)
          eva.weight = total_weighted_score
          eva.save(update_fields=['weight'])
          weighted_score = 0
          print 'i shud not be in here'
          total_weighted_score = 0
        crit = q.criterion
        idofrec = q.eva_id
         
        # if assign votes to stakeholders is Y, then use the assigned votes, if they are not available, give an error                               
        # if assign votes is N, then give 10 votes to each stakeholder 
        print 'total_votes'
        print total_votes
        if  q.votes is None:
            vote_weight = 10 / float(total_votes)
        else:   
            vote_weight = q.votes / float(total_votes) 
        print 'vote weight'    
        print vote_weight 
        if q.score is None:
           q.score = 0 
        # weighted score is for each score 
        weighted_score =  float(q.score * vote_weight)
        print 'weighted score'
        print q.score
        print q.created_by
        print weighted_score
        print total_weighted_score
        # total weighted score is total of weighted scores for EACH criterion
        total_weighted_score = float(total_weighted_score) + float(weighted_score) 
        print 'total weighted score'
        print total_weighted_score
        eva = Evaluation_Criteria.objects.get(id = idofrec)
        eva.weight = total_weighted_score
        # total weight is the grand total of every score and criteria
        total_weight = float(total_weight) + float(weighted_score)
        eva.save(update_fields=['weight']) 
    print 'total weight'
    print total_weight 
    # divide each weighted score by grand total to get adjusted weight 
    for e in Evaluation_Criteria.objects.filter(dec_id=dec_id).exclude(deleted = 'Y'):
        if total_weight == 0:
           e.adjusted_weight = 0
        else:                                                                                                                                    
           if e.weight is not None:
              e.adjusted_weight = float(e.weight) / float(total_weight)
        e.updated_by = loggedinuser
        e.updated_date = datetime.datetime.now()                                                                                                
        e.save(update_fields=['adjusted_weight', 'updated_by','updated_date'])
    return 1

def further_cal(dec_id, loggedinuser, request):
    '''
    Negative relationship between the observed values and the utility values
    Formula: utility value = 10 * (plausible max - observed value)/(plausible max - plausible min)
    utility value = (plausible max - observed value) / (plausible max - plausible min)* 10
    Positive relationship between the observed values and the utility values
    Formula: utility value = (observed value - plausible min ) / (plausible max - plausible min)* 10 
    '''
    qset = Evaluation_Measures.objects.filter(dec_id=dec_id, archived='N').exclude(deleted = 'Y').order_by('opt_id')
    onerec = qset.first()
    solopt = onerec.sol_option
    opt_id = onerec.opt_id
    if onerec.lowest_value is None or onerec.highest_value is None or onerec.higher_better is None or onerec.option_value is None:              
       print 'first redirect'
       return 'em'
    total_value = 0
    for q in qset:
       print 'inside qset' 
       #print q.lowest_value
       #print q.highest_value
       #print q.higher_better
       if q.lowest_value is None or q.highest_value is None or q.higher_better is None or q.option_value is None:         
          print 'second redirect'
          return 'em'
       if q.higher_better == 'Y' or q.higher_better == 'y':                                                                                                               
          q.utility_value = (float(q.option_value) - float(q.lowest_value)) / (float(q.highest_value) - float(q.lowest_value)) * 10
          print 'utility value'
          print q.utility_value
       elif q.higher_better == 'N' or q.higher_better == 'n':
            q.utility_value = 10 * (float(q.highest_value) - float(q.option_value)) / (float(q.highest_value) - float(q.lowest_value))
            print 'elif'
       if solopt == q.sol_option:
          # total value is utility value weighted by weight 
          req_weight = Evaluation_Criteria.objects.get(id = q.eva_id) 
          #print total_value
          #print q.utility_value
          #print 'req weight'
          #print req_weight.adjusted_weight
          total_value = float(total_value) + float(q.utility_value) * float(req_weight.adjusted_weight)
          print 'total value'
          print total_value
       else:
          try:
             u1 = Cost_Utility.objects.filter(dec_id = dec_id, opt_id = opt_id)
             u = u1.exclude(archived = 'Y')
             for u2 in u:
                 u2.updated_by = loggedinuser
                 u2.updated_date = datetime.datetime.now()
                 u2.weighted_utility = total_value
                 print 'in else try'
                 print u2.weighted_utility
                 u2.save(update_fields=['weighted_utility', 'updated_by','updated_date'])
          except ObjectDoesNotExist:                                                                                                                     
             total_value = total_value
             print 'in else does not exist'
             print total_value
             u = Cost_Utility(sol_option = solopt, opt_id = opt_id,  dec_id = dec_id, weighted_utility = total_value, created_by = loggedinuser, created_date = datetime.datetime.now()) 
             u.save()
          solopt = q.sol_option
          opt_id = q.opt_id
          req_weight = Evaluation_Criteria.objects.get(id = q.eva_id) 
          total_value = float(q.utility_value) * float(req_weight.adjusted_weight)
       q.utility_value = q.utility_value
       q.updated_by = loggedinuser
       q.updated_date = datetime.datetime.now()
       q.save(update_fields=['utility_value', 'updated_by','updated_date'])
       print 'opt_id'
       print opt_id

       try: 
          u = Cost_Utility.objects.get(dec_id = dec_id, opt_id = opt_id) 
          #u = u1.exclude(archived = 'Y')
          if u.archived <> 'Y': 
             u.weighted_utility = total_value
             u.updated_by = loggedinuser
             u.updated_date = datetime.datetime.now()
             u.save(update_fields=['weighted_utility', 'updated_by','updated_date'])
       except ObjectDoesNotExist:   
          total_value = total_value
          print 'insert'
          print total_value
          u = Cost_Utility(sol_option = solopt, opt_id = opt_id,  dec_id = dec_id, weighted_utility = total_value , created_by = loggedinuser, created_date = datetime.datetime.now())
          u.save()                                                                   
       except MultipleObjectsReturned:       
          u1 = Cost_Utility.objects.filter(dec_id = dec_id, opt_id = opt_id) 
          u = u1.exclude(archived = 'Y')
          for u2 in u:  
              u2.weighted_utility = total_value
              print 'before update'
              print u2.weighted_utility
              u2.updated_by = loggedinuser
              u2.updated_date = datetime.datetime.now()
              u2.save(update_fields=['weighted_utility', 'updated_by','updated_date'])
    return 1

def update_text_criteria(request, cri, fieldname, dec_id, loggedinuser):
    theid = 0
    try:
       old_eva1 = Evaluation_Criteria.objects.get(fieldname=fieldname, dec_id=dec_id)
       cri = cri.replace(",",";")  
       cri = cri.replace("&#39;","'")
       old_eva1.criterion = cri
       old_eva1.combined = cri
       if cri  == '':
          old_eva1.deleted = 'Y'
          old_eva1.suggested_evam = ''
          old_eva1.data = ''
       else:
          old_eva1.deleted = 'N'
       old_eva1.updated_by = loggedinuser
       old_eva1.updated_date = datetime.datetime.now()
       theid = old_eva1.id
       old_eva1.save(update_fields=['criterion','combined','suggested_evam', 'data','deleted','updated_by','updated_date'])                                                                                                                       
    except ObjectDoesNotExist:   
       if cri <> '':
          cri = cri.replace(",",";") 
          cri = cri.replace("&#39;","'")
          eva_save1 = Evaluation_Criteria(criterion = cri, combined = cri, fieldname = fieldname, dec_id = dec_id, created_by = loggedinuser,created_date = datetime.datetime.now())      
          eva_save1.save()
          theid = eva_save1.id  

    # update importance scores as well if cri is not '' 
    try:           
        for isw in Importance_Scores.objects.filter(eva_id = theid, dec_id=dec_id):
           if cri == '':
              isw.delete() 
           else:   
              isw.deleted = 'N'  
              cri = cri.replace(",",";")    
              cri = cri.replace("&#39;","'")
              isw.criterion = cri
              isw.updated_by = loggedinuser
              isw.updated_date = datetime.datetime.now()
              isw.save(update_fields=['deleted','criterion','updated_by','updated_date'])
    except ObjectDoesNotExist:
       print 'should we move the code from add scores to here' 

    try: 
       for evm in Evaluation_Measures.objects.filter(eva_id = theid, dec_id=dec_id):
           if cri == '':     
              evm.delete()
           else:   
              evm.deleted = 'N' 
              cri = cri.replace(",",";")    
              cri = cri.replace("&#39;","'")
              evm.criterion = cri
              evm.updated_by = loggedinuser
              evm.updated_date = datetime.datetime.now()                                                                                                                                                  
              evm.save(update_fields=['deleted','criterion','updated_by','updated_date']) 
    except ObjectDoesNotExist:
       print 'evam troubles'   

    return 1

def redistribution_func(dec_id, loggedinuser, request):
    qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
    qset_count = 1 
    qset_count = qset.count()    
    actual_votes = 0
    total_votes = 10 * qset_count
    print qset_count 
    if qset_count == 1:
       q = Stakeholders_Decisions.objects.get(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
       if q.votes != total_votes:
          q.votes = total_votes
          q.updated_by = request.session['user']
          q.updated_date = datetime.datetime.now()
          q.save(update_fields=['votes','updated_by','updated_date'])
    else:
       print 'in here'   
       for q in qset:
           if q.votes is None:
              q.votes = 10 
           actual_votes = actual_votes + q.votes 
       for q in qset:
           #print 'final loop'
           print q.votes
           #print actual_votes
           #print total_votes
           if q.votes is None:
              q.votes = 10 
           q.votes = q.votes / actual_votes * total_votes
           q.votes = normal_round(q.votes)
           print q.votes
           q.updated_by = request.session['user']
           q.updated_date = datetime.datetime.now()
           q.save(update_fields=['votes','updated_by','updated_date'])      
    return 1

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)
