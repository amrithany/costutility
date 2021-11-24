from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned                                                                                                                                  
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect,render, render_to_response
from .models import Decisions, Solution_Options, Screening_Criteria, Evaluation_Criteria, Importance_Scores, Users, Stakeholders, Stakeholders_Decisions, MappingTable, SummaryTable, Evaluation_Measures, PA_Setup, EvaluationTable,  Cost_Setup, Cost_Utility, Decision_Made, Detailed_Costs
import datetime 

def check_required(request, dec_id, loggedinuser, created_by):
    ids = {}
    ids2 = {}
    ids3 = {}
    ids4 = {}
    ids5 = {} 
    try:
       solopt = Solution_Options.objects.get(dec_id=dec_id,archived='N')
    except ObjectDoesNotExist:
       print 'solopt'
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered solution options so you cannot view this screen. Please go back and complete the information.'})  
    except MultipleObjectsReturned:                                                                                                           
       print 'solopt multiple objects returned'
       solopt = Solution_Options.objects.filter(dec_id=dec_id,archived='N')
       ids = set(s.id for s in solopt) 
       print ids
      
    try: 
       eva = Evaluation_Criteria.objects.get(dec_id=dec_id)
    except ObjectDoesNotExist:
       print 'eva' 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation criteria so you cannot view this screen. Please go back and complete the information.'})  
    except MultipleObjectsReturned:                                                                                                                
       print 'eva multiple objects returned' 
       eva = Evaluation_Criteria.objects.filter(dec_id=dec_id)
       ids3 = set(q.id for q in eva)
       print ids3

    try: 
       Importance_Scores.objects.get(dec_id = dec_id, created_by = loggedinuser)
    except ObjectDoesNotExist:
       print 'iw'
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered importance scores so you cannot view this screen. Please go back and complete the information.'})   
    except MultipleObjectsReturned:                                                                                                                
       print 'iw multiple objects returned' 
       i = Importance_Scores.objects.filter(dec_id=dec_id, created_by = loggedinuser)
       ids5 = set(q.eva_id for q in i)
       print ids5

    try: 
       qset = Evaluation_Measures.objects.get(dec_id=dec_id) 
    except ObjectDoesNotExist:
       print 'evam' 
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation measures so you cannot view this screen. Please go back and complete the information.'}) 
       #return HttpResponseRedirect('/utility_tool/decisions/message.html')
    except MultipleObjectsReturned:                                                                                                                     
       print 'evam multiple objects returned'
       qset = Evaluation_Measures.objects.filter(dec_id=dec_id) 
       ids2 = set(q.opt_id for q in qset)
       print ids2                                                                                                                                                                                                
       ids4 = set(q.eva_id for q in qset)
       print ids4

    if ids != {} and ids2 != {}:
       mylist = ids - ids2 
       for l in mylist:
           return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered average rating or score for one or more option values. Please go back to Evaluation Measures and complete the information.'})    
    if ids3 != {} and ids4 != {}:
       mylist2 = ids3 - ids4 
       for l in mylist2:
           return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation measures for one or more evaluation criteria. Please go back to Evaluation Measures and complete the information.'})    
    if ids3 != {} and ids5 != {}:
       mylist3 = ids3 - ids5 
       for l in mylist3:
           return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered the score for a new evaluation criteria. Please go back and complete the information.'})
    return 1

def group_cal(dec_id, loggedinuser, request):
    scores = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.score score, i.created_by created_by, s.votes votes FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type= 'Y' AND i.email = s.email order by i.criterion, i.created_by", [dec_id])
                       
    qset = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y')
    qset_count = Stakeholders_Decisions.objects.filter(dec_id=dec_id, created_by=loggedinuser, iw_type='Y').count()                          
    #total_votes = 10 * qset_count
    weighted_score = 0 
    total_weight = 0
    '''
    onerec = Importance_Scores.objects.raw("SELECT i.id, i.eva_id eva_id, i.criterion criterion, i.created_by created_by FROM utility_tool_importance_scores i, utility_tool_stakeholders_decisions s WHERE i.dec_id = s.dec_id AND i.dec_id=%s AND s.iw_type = 'Y' AND i.email = s.email order by i.criterion, i.created_by limit 1", [dec_id])   
    print 'in here' 
    for one in onerec:                                                                                                                       
        idofrec = one.eva_id 
        print idofrec 
        crit = one.criterion
    '''    
    for q in scores:
        eva = Evaluation_Criteria.objects.get(id = q.eva_id)                                                                                
        eva.weight = q.score
        print 'SCORE!'
        print eva.weight
        #total_weight = float(total_weight) + float(weighted_score)
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
            #return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not assigned the number of votes allocated to each stakeholder.'})  
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
    for e in Evaluation_Criteria.objects.filter(dec_id=dec_id):
       if total_weight == 0:
          e.adjusted_weight = 0
       else:  
          if e.weight is not None: 
             e.adjusted_weight = round(float(e.weight) / float(total_weight),2)
       e.weight = total_weight
       print 'what is going on'
       print e.weight
       print e.adjusted_weight
       e.updated_by = loggedinuser                                                                                                     
       e.updated_date = datetime.datetime.now()                                                                                              
       e.save(update_fields=['weight','adjusted_weight', 'updated_by','updated_date'])
    '''   
    return 1

def individual_cal(dec_id, loggedinuser, request):
    #do the weight calculation here   
    total_weight = 0
    #dec 7 took out created_by = loggedinuser 
    for i in Importance_Scores.objects.filter(dec_id = dec_id):
        if i.score is None:
           i.score = 0 
        total_weight = total_weight + i.score
    print 'total weight'    
    print total_weight
    for i in Importance_Scores.objects.filter(dec_id = dec_id):
        if i.score is not None:
           e = Evaluation_Criteria.objects.get(id = i.eva_id)           
           if total_weight == 0:
              e.adjusted_weight = 0
           else:   
              e.adjusted_weight = round(float(i.score) / float(total_weight),2)
           e.weight = total_weight
           e.updated_by = loggedinuser                                                                                                     
           e.updated_date = datetime.datetime.now()                                                                                          
           print 'weight and adjusted weight'
           print e.weight
           print e.adjusted_weight
           e.save(update_fields=['weight','adjusted_weight', 'updated_by','updated_date'])

def further_cal(dec_id, loggedinuser, request):
    '''
    Negative relationship between the observed values and the utility values
    Formula: utility value = 10 * (plausible max - observed value)/(plausible max - plausible min)
    utility value = (plausible max - observed value) / (plausible max - plausible min)* 10
    Positive relationship between the observed values and the utility values
    Formula: utility value = (observed value - plausible min ) / (plausible max - plausible min)* 10 
    '''
    qset = Evaluation_Measures.objects.filter(dec_id=dec_id).order_by('opt_id')
    onerec = qset.first()
    solopt = onerec.sol_option
    opt_id = onerec.opt_id
    if onerec.lowest_value is None or onerec.highest_value is None or onerec.higher_better is None or onerec.option_value is None:              
       print 'first redirect'
       return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation measures so you cannot view this.'})   
    total_value = 0
    for q in qset:
       if q.lowest_value is None or q.highest_value is None or q.higher_better is None or q.option_value is None:         
          print 'second redirect'
          return render(request,'decisions/message.html', {'dec_id':dec_id, 'mess':'You have not entered evaluation measures so you cannot view this.'})
       if q.higher_better == 'Y':                                                                                                               
          q.utility_value = (float(q.option_value) - float(q.lowest_value)) / (float(q.highest_value) - float(q.lowest_value)) * 10
          print 'utility value'
          print q.utility_value
       elif q.higher_better == 'N':
            q.utility_value = 10 * (float(q.highest_value) - float(q.option_value)) / (float(q.highest_value) - float(q.lowest_value))
       if solopt == q.sol_option:
          # total value is utility value weighted by weight 
          req_weight = Evaluation_Criteria.objects.get(id = q.eva_id)
          print total_value
          print q.utility_value
          print req_weight.adjusted_weight
          total_value = float(total_value) + float(q.utility_value) * float(req_weight.adjusted_weight)
       else:
          try:
             u = Cost_Utility.objects.get(dec_id = dec_id, opt_id = opt_id)
             u.updated_by = loggedinuser
             u.updated_date = datetime.datetime.now()
             u.weighted_utility = round(total_value, 1)
             u.save(update_fields=['weighted_utility', 'updated_by','updated_date'])
          except ObjectDoesNotExist:                                                                                                                     
             total_value = round(total_value, 1)
             u = Cost_Utility(sol_option = solopt, opt_id = opt_id,  dec_id = dec_id, weighted_utility = total_value, created_by = loggedinuser, created_date = datetime.datetime.now()) 
             u.save()
          solopt = q.sol_option
          opt_id = q.opt_id
          req_weight = Evaluation_Criteria.objects.get(id = q.eva_id)
          total_value = float(q.utility_value) * float(req_weight.adjusted_weight)
       q.utility_value = round(q.utility_value, 1)   
       q.updated_by = loggedinuser
       q.updated_date = datetime.datetime.now()
       q.save(update_fields=['utility_value', 'updated_by','updated_date'])
       try: 
          u = Cost_Utility.objects.get(dec_id = dec_id, opt_id = opt_id) 
          u.weighted_utility = round(total_value, 1)   
          u.updated_by = loggedinuser
          u.updated_date = datetime.datetime.now()
          u.save(update_fields=['weighted_utility', 'updated_by','updated_date'])
       except ObjectDoesNotExist:   
          total_value = round(total_value, 1)
          u = Cost_Utility(sol_option = solopt, opt_id = opt_id,  dec_id = dec_id, weighted_utility = total_value , created_by = loggedinuser, created_date = datetime.datetime.now())
          u.save()                                                                                                                                       
          #util_res = Cost_Utility.objects.filter(dec_id = dec_id).order_by('-weighted_utility') 

    return 1
