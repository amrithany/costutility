# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models as m
import datetime
from django.core.files.storage import FileSystemStorage
from django.core.validators import URLValidator, MinValueValidator

class Stakeholders(m.Model):
    firstName = m.CharField(max_length=200, null=True, blank=True)
    lastName = m.CharField(max_length=200, null=True, blank=True)
    title  = m.CharField(max_length=200, null=True, blank=True)
    email = m.CharField(max_length=200, null=True, blank=True)
    phone = m.BigIntegerField(null=True,blank=True)
    organisation = m.CharField(max_length=2000,null=True, blank=True)
    notes = m.CharField(max_length=8000,null=True,blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return self.id

class Decisions(m.Model):
    short_title = m.CharField(max_length=200,null=True, blank=True)
    title = m.CharField(max_length=3000,null=True, blank=True)
    name_decisionmaker = m.CharField(max_length=200,null=True, blank=True)
    type_of_dec = m.CharField(max_length=200,null=True, blank=True)
    decision_prob = m.CharField(max_length=5000, null=True, blank=True)
    evidence = m.CharField(max_length=4000, null=True, blank=True) 
    goal = m.CharField(max_length=4000, null=True, blank=True)
    target_audience = m.CharField(max_length=1000, null=True, blank=True)
    stakeholders = m.CharField(max_length=1500, null=True, blank=True)
    participating_stakeholders = m.CharField(max_length=1000, null=True, blank=True)
    potential_sources = m.CharField(max_length=1000, null=True, blank=True)
    by_when = m.DateField(null=True, blank=True)
    real_dec_yn  = m.CharField(max_length=1, null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
    shared =  m.CharField(max_length=1,null=True, blank=True)
    demoDec = m.CharField(max_length=1,null=True, blank=True)

    def __unicode__(self):
        return self.id

class SharedDec(m.Model):
     dec_id = m.IntegerField(null=True,blank=True)
     shared_user =  m.CharField(max_length=200,null=True, blank=True)
     shared =  m.CharField(max_length=1,null=True, blank=True)
     created_by = m.CharField(max_length=200,null=True, blank=True)
     created_date = m.DateTimeField(null=True, blank=True)
     updated_date = m.DateTimeField(null=True, blank=True)
     updated_by = m.CharField(max_length=200,null=True, blank=True)

     def __unicode__(self):
         return self.id                                                                                                                                 

class Stakeholders_Decisions(m.Model):
    st_id = m.IntegerField()
    dec_id = m.IntegerField()
    solopt_type  = m.CharField(max_length=1, null=True, blank=True)
    solopt_date = m.DateField(null=True, blank=True)
    scrcr_type  = m.CharField(max_length=1, null=True, blank=True)
    scrcr_date = m.DateField(null=True, blank=True)
    evacr_type  = m.CharField(max_length=1, null=True, blank=True)
    evacr_date = m.DateField(null=True, blank=True)
    iw_type  = m.CharField(max_length=1, null=True, blank=True)
    iw_date = m.DateField(null=True, blank=True)
    name = m.CharField(max_length=400, null=True, blank=True)
    email = m.CharField(max_length=200, null=True, blank=True)
    votes = m.IntegerField(null=True, blank=True)
    deleted = m.CharField(max_length=1, null=True, blank=True)
    PA = m.CharField(max_length=1, null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return self.id

class PA_Setup(m.Model):
    dec_id = m.IntegerField()
    scores_group_yn = m.CharField(max_length=1,null=True, blank=True)
    votes_yn = m.CharField(max_length=1, null=True, blank=True)                                                                                                                                          
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.id

class MyFileStorage(FileSystemStorage):
    # This method is actually defined in Storage
    def get_available_name(self, name,  max_length=None):
        self.delete(name)
        return name

class FileUpload(m.Model):
    docfile = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    docName = m.CharField(max_length=256, null=True, blank=True)
    docDate = m.DateTimeField(default=datetime.datetime.now)
    def __unicode__(self):
        return self.id

class SD_dec_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_dec_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)                                                                                                                                                 
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_st_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_st_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_solopt_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_solopt_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_scr_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_scr_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_mapp_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_mapp_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_eva_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_eva_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_iw_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_iw_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_evam_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_evam_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_cost_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_cost_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class SD_makedec_file(m.Model):
    filename = m.CharField(max_length=200,null=True, blank=True)
    file_attachment = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class SD_makedec_link(m.Model):
    linkname = m.CharField(max_length=200,null=True, blank=True)    
    link = m.CharField(max_length=1000,null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
                                                                                                                                                                                                                 
    def __unicode__(self):
        return self.id

class Solution_Options_Storage(m.Model):
    solopt_file = m.FileField(storage=MyFileStorage(),upload_to='/costutility/static',null=True, blank=True)
    dec_id = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Solution_Options(m.Model):
    sol_option = m.CharField(max_length=2000)
    option_details = m.CharField(max_length=8000, null=True, blank=True)
    source = m.CharField(max_length=2000,null=True, blank=True)
    filename1 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment1 = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    filename2 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment2 = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    filename3 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment3 = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    filename4 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment4 = m.FileField(storage=MyFileStorage(),upload_to='documents',null=True, blank=True)
    linkname1 = m.CharField(max_length=200,null=True, blank=True)
    link1 = m.CharField(max_length=1000,null=True, blank=True)
    linkname2 = m.CharField(max_length=200,null=True, blank=True)
    link2 = m.CharField(max_length=1000,null=True, blank=True) 
    linkname3 = m.CharField(max_length=200,null=True, blank=True)
    link3 = m.CharField(max_length=1000,null=True, blank=True) 
    linkname4 = m.CharField(max_length=200,null=True, blank=True)
    link4 = m.CharField(max_length=1000,null=True, blank=True)  
    dec_id = m.IntegerField()
    archived = m.CharField(max_length=1,null=True, blank=True) 
    archived_date = m.DateTimeField(null=True, blank=True)
    archived_by = m.CharField(max_length=200,null=True, blank=True)
    unarchived = m.CharField(max_length=1,null=True, blank=True) 
    unarchived_date = m.DateTimeField(null=True, blank=True)
    unarchived_by = m.CharField(max_length=200,null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True) 
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Screening_Criteria(m.Model):
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    criterion2 = m.CharField(max_length=2000, null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    orig_scr_id = m.IntegerField(null=True, blank=True)
    fieldname =  m.CharField(max_length=100, null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class CBCSE_Screening_Criteria(m.Model):
    criterion = m.CharField(max_length=2000, null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class CBCSE_Evaluation_Criteria(m.Model):                                                                                                                 
    overreaching_ec = m.CharField(max_length=2000, null=True, blank=True)
    granular_ec = m.CharField(max_length=2000, null=True, blank=True)
    suggested_evam = m.CharField(max_length=2000, null=True, blank=True)
    data = m.CharField(max_length=2000, null=True, blank=True) 
 
    def __unicode__(self):
        return self.id

class Master_Screening_Criteria(m.Model):
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return self.id

class Master_Evaluation_Criteria(m.Model):                                                                                                                
    overreaching_ec = m.CharField(max_length=2000, null=True, blank=True)
    granular_ec = m.CharField(max_length=2000, null=True, blank=True)
    suggested_evam = m.CharField(max_length=2000, null=True, blank=True)
    data = m.CharField(max_length=2000, null=True, blank=True) 
    dec_id = m.IntegerField(null=True, blank=True) 
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
         
    def __unicode__(self):
        return self.id

class Evaluation_Criteria(m.Model):
    or_criterion = m.CharField(max_length=2000, null=True, blank=True)
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    suggested_evam = m.CharField(max_length=2000, null=True, blank=True)
    data = m.CharField(max_length=2000, null=True, blank=True) 
    criterion2 = m.CharField(max_length=2000, null=True, blank=True)
    combined = m.CharField(max_length=3000, null=True, blank=True)
    orig_eva_id = m.IntegerField(null=True, blank=True)
    fieldname =  m.CharField(max_length=100, null=True, blank=True)
    weight = m.FloatField(null=True, blank=True)
    adjusted_weight = m.FloatField(null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True) 
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Importance_Scores(m.Model):
    eva_id = m.IntegerField(null=True, blank=True)
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    score = m.IntegerField(null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)                                                                                                                                               
    email = m.CharField(max_length=200, null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Scores_Setup(m.Model):
    dec_id = m.IntegerField()
    thinking = m.CharField(max_length=2000,null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return self.id

class Evaluation_Measures(m.Model):
    eva_id = m.IntegerField(null=True, blank=True)
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    opt_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,  null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    measure = m.CharField(max_length=2000, null=True, blank=True)
    unit = m.CharField(max_length=200, null=True, blank=True)
    lowest_value = m.FloatField(null=True, blank=True)
    highest_value = m.FloatField(null=True, blank=True)
    higher_better = m.CharField(max_length=1, null=True, blank=True)
    option_value = m.FloatField(null=True, blank=True)
    utility_value = m.FloatField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)    
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id
'''
class Utility_Results(m.Model):
    opt_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,  null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    total_value = m.FloatField(null=True, blank=True)                                                                                                                                                            
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)    
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id
'''
class EvaluationTable(m.Model):
    table = m.TextField(null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class IdentifyTable(m.Model):
    table = m.TextField(null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
    def __unicode__(self):
        return self.id

class Identify_Data(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    sol_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,null=True, blank=True)
    sol_position = m.IntegerField(null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    ec_id = m.IntegerField(null=True, blank=True)
    measure = m.CharField(max_length=2000,null=True, blank=True)
    data = m.CharField(max_length=2000,null=True, blank=True)
    criterion = m.CharField(max_length=2000,null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True)
    result = m.CharField(max_length=2000,null=True, blank=True)
    created_date = m.DateTimeField(null=True, blank=True)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
    def __unicode__(self):
        return self.id

class MappingTable(m.Model):
    table = m.TextField(null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id


class Mapping_Data(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    sol_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,null=True, blank=True)
    sol_position = m.IntegerField(null=True, blank=True)
    sc_id = m.IntegerField(null=True, blank=True)
    criterion = m.CharField(max_length=2000,null=True, blank=True)
    result = m.CharField(max_length=2000,null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    created_date = m.DateTimeField(null=True, blank=True)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return self.id

class temp_table(m.Model):                                                                                                              
    field1 = m.CharField(max_length=2000,null=True, blank=True)
    def __unicode__(self):
        return self.id

class Temp_Mapping(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    sol_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,null=True, blank=True)
    sol_position = m.IntegerField(null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    def __unicode__(self):
        return self.id

class Cri_Temp_Mapping(m.Model):
    cri_id = m.IntegerField(null=True, blank=True)
    value = m.CharField(max_length=2000,null=True, blank=True)
    position = m.IntegerField(null=True, blank=True)
    deleted = m.CharField(max_length=1,null=True, blank=True)
    def __unicode__(self):                                                                                                                
        return self.id

class SummaryTable(m.Model):
    table = m.TextField(null=True, blank=True)
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Cost_Setup(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    type_of_cost = m.CharField(max_length=200,null=True, blank=True)
    source = m.CharField(max_length=2000,null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id


class Detailed_Costs(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    opt_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,  null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    personnel_cost = m.FloatField(null=True, blank=True, default=0.0)      
    facilities_cost = m.FloatField(null=True, blank=True, default=0.0)
    materials_cost = m.FloatField(null=True, blank=True, default=0.0)
    training_cost = m.FloatField(null=True, blank=True, default=0.0)
    other_cost = m.FloatField(null=True, blank=True, default=0.0)
    total_cost = m.FloatField(null=True, blank=True, default=0.0)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id


class Cost_Utility(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    opt_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,  null=True, blank=True)
    archived = m.CharField(max_length=1,null=True, blank=True)
    type_of_cost = m.CharField(max_length=200,null=True, blank=True)  
    cost = m.FloatField(null=True, blank=True, default=0.0, validators=[MinValueValidator(0.0)])          
    no_of_participants = m.IntegerField(null=True, blank=True, default=0)
    weighted_utility = m.FloatField(null=True, blank=True) 
    cost_utility_ratio = m.FloatField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id

class Decision_Made(m.Model):
    dec_id = m.IntegerField(null=True, blank=True)
    sol_option = m.CharField(max_length=2000,  null=True, blank=True)
    reason = m.CharField(max_length=8000, null=True, blank=True)
    primary_factor = m.CharField(max_length=2000,  null=True, blank=True)
    none = m.CharField(max_length=1, null=True, blank=True)
    other_cons = m.CharField(max_length=2000,  null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id
    
'''
class Screening_Criteria(m.Model):
    criterion = m.CharField(max_length=2000, null=True, blank=True)
    scr_details = m.CharField(max_length=8000, null=True, blank=True)
    filename1 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment1 = m.FileField(storage=MyFileStorage(),upload_to='scrcr',null=True, blank=True)
    filename2 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment2 = m.FileField(storage=MyFileStorage(),upload_to='scrcr',null=True, blank=True)
    filename3 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment3 = m.FileField(storage=MyFileStorage(),upload_to='scrcr',null=True, blank=True)
    filename4 = m.CharField(max_length=200,null=True, blank=True)
    file_attachment4 = m.FileField(storage=MyFileStorage(),upload_to='scrcr',null=True, blank=True)
    linkname1 = m.CharField(max_length=200,null=True, blank=True)
    link1 = m.CharField(max_length=1000,null=True, blank=True)
    linkname2 = m.CharField(max_length=200,null=True, blank=True)
    link2 = m.CharField(max_length=1000,null=True, blank=True) 
    linkname3 = m.CharField(max_length=200,null=True, blank=True)
    link3 = m.CharField(max_length=1000,null=True, blank=True) 
    linkname4 = m.CharField(max_length=200,null=True, blank=True)
    link4 = m.CharField(max_length=1000,null=True, blank=True)  
    dec_id = m.IntegerField(null=True, blank=True)
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200,null=True, blank=True)
    updated_date = m.DateTimeField(default=datetime.datetime.now)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
 
    def __unicode__(self):
        return self.id
'''

class Users(m.Model):
    user = m.CharField(max_length=200)
    oldemail = m.CharField(max_length=200, null=True, blank=True)
    email = m.CharField(max_length=200, null=True, blank=True)
    emailagain = m.CharField(max_length=200, null=True, blank=True)
    oldpassword = m.CharField(max_length=200, null=True, blank=True)
    password = m.CharField(max_length=200)
    passwordagain = m.CharField(max_length=200)
    firstName = m.CharField(max_length=200, null=True, blank=True)
    lastName = m.CharField(max_length=200, null=True, blank=True)
    addressline1 =  m.CharField(max_length=2000, null=True, blank=True)
    addressline2 = m.CharField(max_length=2000, null=True, blank=True)
    city = m.CharField(max_length=200, null=True, blank=True)
    state = m.CharField(max_length=200, null=True, blank=True)
    zip = m.CharField(max_length=200, null=True, blank=True)
    country = m.CharField(max_length=200, null=True, blank=True)
    phone = m.BigIntegerField(null=True,blank=True)
    organisation = m.CharField(max_length=2000,null=True, blank=True)
    type_of_org = m.CharField(max_length=1000,null=True, blank=True) 
    other_org = m.CharField(max_length=1000,null=True, blank=True) 
    position = m.CharField(max_length=2000,null=True, blank=True)
    other_pos = m.CharField(max_length=1000,null=True, blank=True)
    hearaboutus = m.CharField(max_length=100,null=True, blank=True) 
    other_hear = m.CharField(max_length=100,null=True, blank=True)
    updates = m.CharField(max_length=10,null=True, blank=True) 
    education = m.CharField(max_length=200,null=True, blank=True) 
    age = m.CharField(max_length=100,null=True, blank=True) 
    gender = m.CharField(max_length=100,null=True, blank=True) 
    race = m.CharField(max_length=200,null=True, blank=True)
    other_race = m.CharField(max_length=100,null=True, blank=True)
    publicOrPrivate = m.CharField(max_length=8,null=True, blank=True)
    licenseSigned = m.CharField(max_length=3,null=True, blank=True)
    startDate = m.DateField(default=datetime.datetime.now,null=True, blank=True)
    endDate = m.DateField(null=True, blank=True)
    lastLogin = m.DateField(null=True, blank=True)
    timesLoggedin = m.IntegerField(null=True,blank=True)
    uniqueRandomId = m.IntegerField(null=True,blank=True)
    orig_reg_date = m.DateField(null=True, blank=True)
    updated_date = m.DateTimeField(null=True, blank=True)
    updated_by = m.CharField(max_length=200,null=True, blank=True)
    def __unicode__(self):
        return self.id

class Login(m.Model):
    user = m.CharField(max_length=200)
    email = m.CharField(max_length=200, null=True, blank=True)
    loggedindate = m.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.id

class Duplicated_DecIds(m.Model):
    dec_id_for_dupl = m.IntegerField()
    created_date = m.DateTimeField(default=datetime.datetime.now)
    created_by = m.CharField(max_length=200)
 
    def __unicode__(self):
        return self.id


'''class TempTable(m.Model):
    temptext = m.CharField(max_length=1000)
 
    def __unicode__(self):
        return self.id'''
