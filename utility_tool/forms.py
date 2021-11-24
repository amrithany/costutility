from django import forms
from django.forms import Textarea, ComboField
from utility_tool.models import Decisions, Solution_Options, Screening_Criteria, Evaluation_Criteria, Importance_Scores, Users, Stakeholders, Stakeholders_Decisions, PA_Setup, Cost_Setup, Decision_Made, Solution_Options_Storage, SD_dec_file, SD_dec_link, SD_st_file, SD_st_link, SD_solopt_file, SD_solopt_link, SD_scr_file, SD_scr_link, SD_mapp_file, SD_mapp_link, SD_eva_file, SD_eva_link, SD_iw_file, SD_iw_link, SD_evam_file, SD_evam_link, SD_cost_file, SD_cost_link,SD_makedec_file, SD_makedec_link, FileUpload
from django.core.validators import URLValidator
from django.template.defaultfilters import filesizeformat
import selectable.forms as selectable
from selectable.forms import AutoCompleteSelectField, AutoCompleteWidget, AutoComboboxSelectWidget

class StakeholdersForm(forms.ModelForm):
    firstName = forms.CharField(label = "First Name")
    lastName = forms.CharField(label = "Last Name")
    title  = forms.CharField(required=False, label = "Title")
    email = forms.CharField(label = "Email")
    phone = forms.IntegerField(required=False, label = "Phone")
    organisation = forms.CharField(required=False, label = "Organization")
    notes = forms.CharField(required=False, widget=forms.Textarea(), label = "Notes")

    class Meta:
       model = Stakeholders
       fields = ('firstName','lastName','title','email','phone','organisation','notes', )

    def __init__(self, *args, **kwargs):
        super(StakeholdersForm, self).__init__(*args, **kwargs)
        self.fields['notes'].widget.attrs['style'] = 'width:700px; height:180px;'

class DecisionForm(forms.ModelForm):
   short_title = forms.CharField(label = "* Short title for this decision (about 50 characters or less)") 
   title = forms.CharField(label = "* Describe the problem that needs to be addressed", widget=forms.Textarea())
   #type_of_dec =  forms.ChoiceField(widget=forms.RadioSelect, choices=(('Related to curricula or instructional strategies/tools', 'Related to curricula or instructional strategies/tools'),('Related to logistics or school organization','Related to logistics or school organization'),('Other','Other')), label="*What type of decision is this?")
   decision_prob = forms.CharField(label = "* In one sentence, what is the decision you need to make?")
   name_decisionmaker = forms.CharField(label="* What is the name of the institution/department/person who needs to make this decision?")
   real_dec_yn = forms.ChoiceField(widget=forms.RadioSelect, choices=(('R', 'Real decision'), ('T' , 'Training/Demonstration decision'),('X','Test decision')), label="* Is this a real decision problem you are working on or for training/demonstration purposes?")
   evidence = forms.CharField(required=False, widget=forms.Textarea(), label = "What evidence do you have that this issue needs to be addressed?")
   goal = forms.CharField(required=False, widget=forms.Textarea(),label = "What is your goal for this decision?")
   target_audience = forms.CharField(required=False, widget=forms.Textarea(), label = "Who will be served by the program/strategy you choose?")
   stakeholders = forms.CharField(required=False, widget=forms.Textarea(),label = "Who are the stakeholders in this decision (i.e., people who will be affected by the decision)?")
   participating_stakeholders = forms.CharField(required=False, widget=forms.Textarea(),label = "Which of these stakeholders will you invite to participate in making this decision?")
   potential_sources = forms.CharField(required=False, widget=forms.Textarea(),label = "What are some potential sources of solutions to  address this decision problem?")
   by_when = forms.DateField(required=False, widget=forms.widgets.DateInput(attrs={'type': 'date'}), label = "By when do you need to make this decision?")

   class Meta:
      model = Decisions
      fields = ('short_title','title','decision_prob', 'name_decisionmaker', 'real_dec_yn', 'evidence', 'target_audience', 'goal','stakeholders','participating_stakeholders','potential_sources','by_when', )

   def __init__(self, *args, **kwargs):
        super(DecisionForm, self).__init__(*args, **kwargs)
        self.fields['short_title'].widget.attrs['style'] = 'width:350px;'
        self.fields['title'].widget.attrs['style'] = 'width:700px;height:80px;'
        self.fields['name_decisionmaker'].widget.attrs['style'] = 'width:700px;'
        self.fields['decision_prob'].widget.attrs['style'] = 'width:700px;'
        self.fields['evidence'].widget.attrs['style'] = 'width:700px; height:80px;'
        self.fields['goal'].widget.attrs['style'] = 'width:700px; height:180px;'
        self.fields['target_audience'].widget.attrs['style'] = 'width:700px; height:80px;'
        self.fields['stakeholders'].widget.attrs['style'] = 'width:700px; height:80px;'
        self.fields['participating_stakeholders'].widget.attrs['style'] = 'width:700px; height:80px;'
        self.fields['potential_sources'].widget.attrs['style'] = 'width:700px; height:80px;'

class SetupForm(forms.ModelForm):
    scores_group_yn = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Y', 'Single importance score on behalf of all stakeholders'),('N','Individual scores from 2 or more stakeholders')), label="Are you going to assign the importance scores in a group or do it individually?")
    votes_yn = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Y', 'Yes'),('N','No')), label="Do you want to assign different votes to different stakeholders?")

    class Meta:
        model = PA_Setup
        fields = ('scores_group_yn', 'votes_yn',)

class SolOptForm(forms.ModelForm):
    sol_option = forms.CharField(required=False, label = "Option")
    created_by = forms.CharField(required=False, label = "Created By")
    updated_by = forms.CharField(required=False, label = "Updated By") 
 
    class Meta:
      model = Solution_Options
      fields = ('sol_option', 'created_by','updated_by', )

    def __init__(self, *args, **kwargs):
        super(SolOptForm, self).__init__(*args, **kwargs)
        self.fields['sol_option'].widget.attrs['style'] = 'width:750px;'

class SDForm_dec_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_dec_file
      fields = ('filename','file_attachment',)


class SDForm_dec_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False, label="Enter a Link")
 
    class Meta:
      model = SD_dec_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_dec_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_st_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_st_file
      fields = ('filename','file_attachment',)

class SDForm_st_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False, label="Enter a Link")
 
    class Meta:
      model = SD_st_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_st_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_solopt_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_solopt_file
      fields = ('filename','file_attachment',)

class SDForm_solopt_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_solopt_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_solopt_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_scr_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_scr_file
      fields = ('filename','file_attachment',)

class SDForm_scr_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False, label="Enter a Link")
 
    class Meta:
      model = SD_scr_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_scr_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_mapp_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_mapp_file
      fields = ('filename','file_attachment',)

class SDForm_mapp_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_mapp_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_mapp_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_eva_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_eva_file
      fields = ('filename','file_attachment',)

class SDForm_eva_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_eva_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_eva_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_iw_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_iw_file
      fields = ('filename','file_attachment',)

class SDForm_iw_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_iw_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_iw_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_evam_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_evam_file
      fields = ('filename','file_attachment',)

class SDForm_evam_link(forms.ModelForm):                                                                                                                                                                         
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_evam_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_evam_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_cost_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_cost_file
      fields = ('filename','file_attachment',)

class SDForm_cost_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_cost_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_cost_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class SDForm_makedec_file(forms.ModelForm):
    filename = forms.CharField(required=False, label = "File Name")
    file_attachment = forms.FileField(required=False, label='Select a file from your computer to upload',)
 
    class Meta:
      model = SD_makedec_file
      fields = ('filename','file_attachment',)

class SDForm_makedec_link(forms.ModelForm):                                                                                                                                                                          
    linkname = forms.CharField(required=False, label = "Link Name")
    link = forms.CharField(required=False,  label="Enter a Link")
 
    class Meta:
      model = SD_makedec_link
      fields = ('linkname','link',)

    def __init__(self, *args, **kwargs):
        super(SDForm_makedec_link, self).__init__(*args, **kwargs)
        self.fields['link'].widget.attrs['style'] = 'width:600px;'

class Solopt_Storage(forms.ModelForm):
    solopt_file = forms.FileField(required=False, label='Select an Excel sheet to upload Solution Options into DecisionMaker',)
 
    class Meta:
      model = Solution_Options_Storage
      fields = ('solopt_file',)

class FileUploadForm(forms.ModelForm):                                                                                                    
    docfile = forms.FileField(required=False, label='',)
    
    class Meta:
      model = FileUpload
      fields = ('docfile',)

class SolOptForm2(forms.ModelForm):
    sol_option = forms.CharField(required=False, label = "Option")
    source = forms.CharField(required=False, label = "Source") 
    option_details = forms.CharField(required=False,  widget=forms.Textarea(), label = "Option Details")
    filename1 = forms.CharField(required=False, label = "File Name")
    file_attachment1 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename2 = forms.CharField(required=False, label = "File Name")
    file_attachment2 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename3 = forms.CharField(required=False, label = "File Name")
    file_attachment3 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename4 = forms.CharField(required=False, label = "File Name")
    file_attachment4 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    linkname1 = forms.CharField(required=False, label = "Link Name")
    link1 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link")                                                                                                                                                   
    linkname2 = forms.CharField(required=False, label = "Link Name")
    link2 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
    linkname3 = forms.CharField(required=False, label = "Link Name")
    link3 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
    linkname4 = forms.CharField(required=False, label = "Link Name")
    link4 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
    archived = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Y', 'Put this away for now'),), label="Do you wish to archive this option?", initial='N')
    deleted = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Y', 'Delete this solution option permanently'),), label="", initial='N')
    #archived = forms.ChoiceField(choices=(('Y', 'Y'),('N','No')),required=False,label="Do you wish to archive this option?", widget=forms.CheckboxSelectMultiple())
    created_by = forms.CharField(required=False, label = "Created By")
    updated_by = forms.CharField(required=False, label = "Updated By") 
 
    class Meta:
      model = Solution_Options
      fields = ('sol_option', 'source','option_details','filename1', 'file_attachment1','filename2', 'file_attachment2','filename3', 'file_attachment3','filename4','file_attachment4','linkname1','link1','linkname2','link2','linkname3','link3','linkname4','link4', 'created_by','updated_by','archived','deleted',)

    def __init__(self, *args, **kwargs):
        super(SolOptForm2, self).__init__(*args, **kwargs)
        self.fields['sol_option'].widget.attrs['style'] = 'width:750px;'
        self.fields['source'].widget.attrs['style'] = 'width:750px;'
        self.fields['option_details'].widget.attrs['style'] = 'width:700px; height:180px;'
        self.fields['link1'].widget.attrs['style'] = 'width:750px;'
        self.fields['link2'].widget.attrs['style'] = 'width:750px;'
        self.fields['link3'].widget.attrs['style'] = 'width:750px;'
        self.fields['link4'].widget.attrs['style'] = 'width:750px;'
    '''
    def clean_link1(self):
        try:
           data = self.cleaned_data['link1']
        except ValidationError:
            raise self.fields['link1'].error_messages['Invalid URL VV']
        return data
    https://whoisnicoleharris.com/2015/01/06/implementing-django-formsets.html
    def clean(self):
        if any(self.errors):
            return

        options = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                sol_option = form.cleaned_data['sol_option']

                # Check for duplicates
                if sol_option:
                    if sol_option in options:
                        duplicates = True
                    options.append(sol_option)


                if duplicates:
                    raise forms.ValidationError(
                        'Option Name should be unique..',
                        code='duplicate_options'
                    )
    '''
class SolOptArchive(forms.ModelForm):
    sol_option = forms.CharField(required=False, label = "Option", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    option_details = forms.CharField(required=False,  label = "Option Details", widget=forms.Textarea(attrs={'readonly':'readonly'}))
    filename1 = forms.CharField(required=False, label = "File Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment1 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename2 = forms.CharField(required=False, label = "File Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment2 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename3 = forms.CharField(required=False, label = "File Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment3 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename4 = forms.CharField(required=False, label = "File Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment4 = forms.FileField(required=False, label='Select a file from your computer to upload')
    linkname1 = forms.CharField(required=False, label = "Link Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link1 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link", widget=forms.TextInput(attrs={'readonly':'readonly'}))                                                                                                                   
    linkname2 = forms.CharField(required=False, label = "Link Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link2 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link", widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    linkname3 = forms.CharField(required=False, label = "Link Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link3 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link", widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    linkname4 = forms.CharField(required=False, label = "Link Name", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link4 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link", widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    unarchived = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Y', 'Restore this to the Solution Options list for further consideration'),), label="Do you wish to un-archive this option?", initial='N')
    created_by = forms.CharField(required=False, label = "Created By", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    updated_by = forms.CharField(required=False, label = "Updated By", widget=forms.TextInput(attrs={'readonly':'readonly'})) 
 
    class Meta:
      model = Solution_Options
      fields = ('sol_option', 'option_details','filename1', 'file_attachment1','filename2', 'file_attachment2','filename3', 'file_attachment3','filename4', 'file_attachment4','linkname1','link1','linkname2','link2','linkname3','link3','linkname4','link4', 'created_by','updated_by','unarchived',)

    def __init__(self, *args, **kwargs):
        super(SolOptArchive, self).__init__(*args, **kwargs)
        self.fields['sol_option'].widget.attrs['style'] = 'width:750px;'
        self.fields['option_details'].widget.attrs['style'] = 'width:700px; height:180px;'
        self.fields['link1'].widget.attrs['style'] = 'width:750px;'
        self.fields['link2'].widget.attrs['style'] = 'width:750px;'                                                                                                                                              
        self.fields['link3'].widget.attrs['style'] = 'width:750px;'
        self.fields['link4'].widget.attrs['style'] = 'width:750px;'

class SolOptView(forms.ModelForm):
    sol_option = forms.CharField(required=False, label = "Option", widget=forms.TextInput(attrs={'readonly':'readonly'}))                                                                                                                                                  
    source = forms.CharField(required=False, label = "Source", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    option_details = forms.CharField(required=False, label = "Option Details", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    filename1 = forms.CharField(required=False, label = "File Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment1 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename2 = forms.CharField(required=False, label = "File Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment2 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename3 = forms.CharField(required=False, label = "File Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment3 = forms.FileField(required=False, label='Select a file from your computer to upload')
    filename4 = forms.CharField(required=False, label = "File Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    file_attachment4 = forms.FileField(required=False, label='Select a file from your computer to upload')
    linkname1 = forms.CharField(required=False, label = "Link Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link1 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link",widget=forms.TextInput(attrs={'readonly':'readonly'}))                                                                                                                   
    linkname2 = forms.CharField(required=False, label = "Link Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link2 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link",widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    linkname3 = forms.CharField(required=False, label = "Link Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link3 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link",widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    linkname4 = forms.CharField(required=False, label = "Link Name",widget=forms.TextInput(attrs={'readonly':'readonly'}))
    link4 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link",widget=forms.TextInput(attrs={'readonly':'readonly'})) 
    created_by = forms.CharField(required=False, label = "Created By", widget=forms.TextInput(attrs={'readonly':'readonly'}))
    updated_by = forms.CharField(required=False, label = "Updated By", widget=forms.TextInput(attrs={'readonly':'readonly'})) 
 
    class Meta:
      model = Solution_Options
      fields = ('sol_option', 'source','option_details','filename1', 'file_attachment1','filename2', 'file_attachment2','filename3', 'file_attachment3','filename4', 'file_attachment4','linkname1','link1','linkname2','link2','linkname3','link3','linkname4','link4','created_by','updated_by', )   

    def __init__(self, *args, **kwargs):
        super(SolOptView, self).__init__(*args, **kwargs)
        self.fields['sol_option'].widget.attrs['style'] = 'width:750px;'
        self.fields['source'].widget.attrs['style'] = 'width:750px;'
        self.fields['option_details'].widget.attrs['style'] = 'width:700px; height:180px;'
        self.fields['link1'].widget.attrs['style'] = 'width:750px;'
        self.fields['link2'].widget.attrs['style'] = 'width:750px;'
        self.fields['link3'].widget.attrs['style'] = 'width:750px;'
        self.fields['link4'].widget.attrs['style'] = 'width:750px;'

class ScrCriteriaForm(forms.ModelForm):
    criterion = forms.CharField(required=False, label = "Criterion")

    class Meta:
      model = Screening_Criteria
      fields = ('criterion',)

    def __init__(self, *args, **kwargs):
        super(ScrCriteriaForm, self).__init__(*args, **kwargs)
        self.fields['criterion'].widget.attrs['style'] = 'width:1000px;' 

class EvaCriteriaForm(forms.ModelForm):
    criterion = forms.CharField(required=False, label = "Criterion")
    #criterion = forms.ComboField(fields=[forms.CharField(max_length=20), forms.ChoiceField(widget=forms.RadioSelect, choices=(('Total', 'Total'),('Avg','Average'))),required=False, label = "Criterion")
    created_by = forms.CharField(required=False, label = "Created By")
    updated_by = forms.CharField(required=False, label = "Updated By") 

    class Meta:
      model = Evaluation_Criteria
      fields = ('criterion','created_by','updated_by', )

    def __init__(self, *args, **kwargs):
        super(EvaCriteriaForm, self).__init__(*args, **kwargs)
        self.fields['criterion'].widget.attrs['style'] = 'width:1000px;' 

class ScoresForm(forms.ModelForm):
    criterion = forms.CharField(required=False, label = "Criterion")
    score = forms.IntegerField(required=False, label = "Score", initial="50") 
    created_by = forms.CharField(required=False, label = "Added By")

    class Meta:
      model = Importance_Scores
      fields = ('criterion', 'score','created_by', )

    def __init__(self, *args, **kwargs):
        super(ScoresForm, self).__init__(*args, **kwargs)
        self.fields['criterion'].widget.attrs['style'] = 'width:500px;' 
        self.fields['score'].widget.attrs['style'] = 'width:50px;' 
        self.fields['created_by'].widget.attrs['style'] = 'width:150px;'

class VotesForm(forms.ModelForm):
    name = forms.CharField(required=False, label = "name")
    votes = forms.IntegerField(required=False, label = "Votes", min_value = 0) 
    updated_by = forms.CharField(required=False, label = "Updated By")

    class Meta:
      model = Stakeholders_Decisions
      fields = ('name','votes','updated_by', )

    def has_changed(self):
      changed_data = super(forms.ModelForm, self).has_changed()
      return bool(self.initial or changed_data)  


class CostSetupForm(forms.ModelForm):
    type_of_cost = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=(('Total', 'Total program costs for all participants served'),('Avg','Average program costs per student or teacher served'), ('Marginal','The marginal costs of adding each additional participant to an established program')), label="Which cost metric is most informative for your decision making?", initial="Total")

    class Meta:
        model = Cost_Setup
        fields = ('type_of_cost', )

class DecisionMadeForm(forms.ModelForm):
   sol_option = forms.ModelMultipleChoiceField(Solution_Options.objects.filter(dec_id = 0, archived = 'N').values_list('id', flat=True), required=False)
   reason = forms.CharField(required=False, widget=forms.Textarea(), label = "In one or two sentences, please explain how the decision between these solution options was made and the thinking behind the decision.")

   class Meta:
      model = Decision_Made
      fields = ('sol_option','reason', )

   '''
   def __unicode__(self):
        return unicode(self.sol_option)
   def __init__(self, *args, **kwargs):
        dec_id = kwargs.pop("dec_id")
        super(DecisionMadeForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        query = Solution_Options.objects.filter(dec_id = dec_id, archived = 'N').values_list('sol_option', flat=True).distinct()                                                                               
        query_choices =  [(id, id) for id in query] + [('None of the above','None of the above')] 
        self.fields['sol_option']=forms.ModelMultipleChoiceField(Solution_Options.objects.filter(dec_id = dec_id, archived = 'N'), required=False, widget=forms.CheckboxSelectMultiple,label="Which option(s) did you choose? (Please check ALL that apply)") 
        thismodel = Decision_Made.objects.filter(dec_id = dec_id).values_list('sol_option', flat=True)
        thischoice = [(id, id) for id in thismodel]
        print 'thischoice'
        print thischoice
        print 'opt list'
        print opt_list
        self.initial['sol_option']= opt_list
        self.fields['reason'].widget.attrs['style'] = 'width:700px; height:80px;'
        #if self.instance:
           #self.fields['sol_option'].initial = opt_list 

class ScrCriteriaForm2(forms.ModelForm):
    criterion = forms.CharField(required=False, label = "Criterion")
    scr_details = forms.CharField(required=False, widget=forms.Textarea(), label = "Criterion Details")
    filename1 = forms.CharField(required=False, label = "File Name")
    file_attachment1 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename2 = forms.CharField(required=False, label = "File Name")
    file_attachment2 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename3 = forms.CharField(required=False, label = "File Name")
    file_attachment3 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    filename4 = forms.CharField(required=False, label = "File Name")
    file_attachment4 = forms.FileField(required=False, label='Select a file from your computer to upload',)
    linkname1 = forms.CharField(required=False, label = "Link Name")
    link1 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link")                                                                                                                   
    linkname2 = forms.CharField(required=False, label = "Link Name")
    link2 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
    linkname3 = forms.CharField(required=False, label = "Link Name")
    link3 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
    linkname4 = forms.CharField(required=False, label = "Link Name")
    link4 = forms.CharField(required=False, validators=[URLValidator()], label="Enter a Link") 
  
    class Meta:
      model = Screening_Criteria
      fields = ('criterion','scr_details',  'filename1', 'file_attachment1','filename2', 'file_attachment2','filename3', 'file_attachment3','filename4', 'file_attachment4','linkname1','link1','linkname2','link2', 'link3','linkname3','link4','linkname4',)
   

    def __init__(self, *args, **kwargs):
        super(ScrCriteriaForm2, self).__init__(*args, **kwargs)
        self.fields['criterion'].widget.attrs['style'] = 'width:750px;' 
        self.fields['scr_details'].widget.attrs['style'] = 'width:700px; height:180px;'
        self.fields['link1'].widget.attrs['style'] = 'width:750px;'
        self.fields['link2'].widget.attrs['style'] = 'width:750px;'
        self.fields['link3'].widget.attrs['style'] = 'width:750px;'
        self.fields['link4'].widget.attrs['style'] = 'width:750px;' 
'''

class LoginForm(forms.ModelForm):
    user = forms.CharField(label="User Name")
    password = forms.CharField(label="Password",widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ('user', 'password')

class ForgotForm(forms.ModelForm):                                                                                                                                                                               
   email = forms.EmailField(label="Email address")
   class Meta:
      model = Users
      fields = ('email',)

class ChangeForm(forms.ModelForm):
    oldpassword = forms.CharField(label="Enter the current Password",widget=forms.PasswordInput)                                             
    password = forms.CharField(label="Enter the new Password",widget=forms.PasswordInput)
    passwordagain = forms.CharField(label="Confirm the new Password again",widget=forms.PasswordInput)
    class Meta:
        model = Users
        fields = ('oldpassword','password', 'passwordagain')

class RegisterForm(forms.ModelForm):
   user = forms.CharField(label="User Name")
   email = forms.EmailField(label="Email address")
   emailagain = forms.EmailField(label="Confirm Email address")
   password = forms.CharField(label="Password",widget=forms.PasswordInput)
   passwordagain = forms.CharField(label="Confirm Password",widget=forms.PasswordInput)
   firstName = forms.CharField(label="First Name")
   lastName = forms.CharField(label="Last Name")
   state = forms.CharField(label="State/Province/Region")
   country = forms.CharField(label="Country")
   organisation = forms.CharField(label="Organization Name")
   type_of_org = forms.ChoiceField(choices=(('',''),('Board of Education (State, District, or School)','Board of Education (State, District, or School)'), ('Consulting organization', 'Consulting organization'),('Educational / social program provider', 'Educational / social program provider'),('Policy development organization','Policy development organization'),('Research / evaluation organization', 'Research / evaluation organization'),('School','School'),('School district / Local Education Agency', 'School district / Local Education Agency'),('School Support Organization / Charter Management Organization','School Support Organization / Charter Management Organization'), ('State Education Agency','State Education Agency'),('Technical assistance provider','Technical assistance provider'),('Think tank', 'Think tank'), ('University / College', 'University / College'),('University-based research / policy analysis center', 'University-based research / policy analysis center'),('Other','Other')), label="Type of Organization")
   other_org = forms.CharField(required=False, label="Other Organization")
   position = forms.ChoiceField(label="Position", choices=(('',''),('Administrator','Administrator'),('Analyst','Analyst'),('Board Member', 'Board Member'),('Doctoral student', 'Doctoral student'),('Evaluator','Evaluator'),('Masters degree student','Masters degree student'),('Other student','Other student'), ('Policy advisor','Policy advisor'),('Professor / Instructor / Lecturer', 'Professor / Instructor / Lecturer'),('Researcher','Researcher'),('Senior executive','Senior executive'),('Teacher','Teacher'),('Other','Other')))                                                                              
   other_pos = forms.CharField(required=False, label="Other Position")
   hearaboutus = forms.ChoiceField(label="How did you hear about DecisionMaker?",choices=(('',''),('I found it through an online search engine','I found it through an online search engine'),('Social media (Twitter, Facebook, LinkedIn etc.)','Social media (Twitter, Facebook, LinkedIn etc.)') , ('I attended a training session in which it was used','I attended a training session in which it was used'),('Recommendation from a colleague','Recommendation from a colleague'), ('Other (please specify)','Other (please specify)')))
   other_hear = forms.CharField(required=False, label="")
   updates = forms.ChoiceField(required=False, choices=(('',''),('Y', 'Yes'),('N','No')), label="Would you like to receive occasional updates if we add new features or provide training opportunities related to DecisionMaker?") 
   education = forms.ChoiceField(required=False, label="Highest level of education completed:", choices=(('',''),('Doctorate/Ph.D.', 'Doctorate/Ph.D.'),  ('Professional Degree','Professional Degree'),('Masters Degree','Masters Degree'), ('Bachelors Degree','Bachelors Degree'), ('Associates Degree (2-year degree)','Associates Degree (2-year degree)'), ('Some university/college courses, but no degree','Some university/college courses, but no degree'), ('Secondary School/High School','Secondary School/High School')))
   age = forms.ChoiceField(label="Age:", required=False, choices=(('',''),('13-17','13-17'),('18-29','18-29'),('30-39','30-39'),('40-49','40-49'),('50+','50+')))
   gender = forms.ChoiceField(label="Gender:", required=False, choices=(('',''), ('Female','Female'),('Male','Male'), ('Non-binary','Non-binary')))
   race = forms.ChoiceField(label="Race/Ethnicity:", required=False, choices=(('',''),('Hispanic','Hispanic'),('White', 'White'),('Black or African American', 'Black or African American'),('Asian', 'Asian'),('American Indian', 'American Indian'),('Multiracial','Multiracial'),('Other','Other')))
   other_race = forms.CharField(required=False, label="")
   publicOrPrivate = forms.ChoiceField(choices=(('Public','Public Institution'), ('Private','Private Institution/Individual')),label="For the purpose of the license agreement, are you signing as a public institution or a private institution/individual?")
  
   class Meta:
      model = Users
      fields = ('user', 'email','emailagain','password','passwordagain','firstName', 'lastName','state', 'country', 'organisation','type_of_org','other_org','position','other_pos','hearaboutus','other_hear','updates','education','age','gender','race','other_race','publicOrPrivate')

class License(forms.ModelForm):
   licenseSigned = forms.ChoiceField(widget=forms.RadioSelect, choices=(('Yes', 'Yes, I agree to the terms of the DecisionMaker License Agreement'),('No','No, please log me out')), label="")

   class Meta:
       model = Users
       fields = ('licenseSigned',)

