from django import forms
from bfrs.models import (Bushfire, AreaBurnt, Damage, Injury,
        Region, District, Profile
    )
from datetime import datetime, timedelta
from django.conf import settings
from django.forms import ValidationError
from django.forms.models import inlineformset_factory, formset_factory, BaseInlineFormSet
#from django.forms.formsets import BaseFormSet
from django.contrib import messages
from django.contrib.auth.models import User, Group

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML
from crispy_forms.bootstrap import TabHolder, Tab
from django.utils.safestring import mark_safe
from django.forms.widgets import Widget

YESNO_CHOICES = (
    (True, 'Yes'),
    (False, 'No')
)


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'&nbsp;&nbsp;&nbsp;&nbsp;\n'.join([u'%s&nbsp;&nbsp;&nbsp;&nbsp;\n' % w for w in self]))


class VerticalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'<br />'.join([u'%s<br />' % w for w in self]))


class DisplayOnlyField(Widget):

    def __init__(self,attrs=None):
        self.attrs = attrs or {}
        self.required = False

    def render(self, name, value="", attrs=None):
        try:
            val = value
        except AttributeError:
            val = ""
        return val


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].label = ("Approved User (i.e. enable login for this user?)")
        #import ipdb; ipdb.set_trace()
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True

    class Meta:
        model = User
        fields = ('is_active', 'groups', 'user_permissions',)


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ()



class BaseFormHelper(FormHelper):
    """
    Base helper class for rendering forms via crispy_forms.
    To remove the default "Save" button from the helper, instantiate it with
    inputs=[]
    E.g. helper = BaseFormHelper(inputs=[])
    """
    def __init__(self, *args, **kwargs):
        super(BaseFormHelper, self).__init__(*args, **kwargs)
        self.form_class = 'horizontal col-lg-2'
        self.help_text_inline = True
        self.form_method = 'POST'
        save_btn = Submit('submit', 'Save')
        save_btn.field_classes = 'btn btn-primary'
        cancel_btn = Submit('cancel', 'Cancel')
        self.add_input(save_btn)
        self.add_input(cancel_btn)


class HelperModelForm(forms.ModelForm):
    """
    Stock ModelForm with a property named ``helper`` (used by crispy_forms to
    render in templates).
    """
    @property
    def helper(self):
        helper = BaseFormHelper()
        return helper


class ProfileForm(HelperModelForm):
#class ProfileForm(forms.ModelForm):
    def clean(self):
        """District must be child of Region.
        """
        cleaned_data = super(ProfileForm, self).clean()
        district = cleaned_data.get('district', None)
        if district and district.region != cleaned_data.get('region'):
            self._errors['district'] = self.error_class(
                ['Please choose a valid District for this Region (or leave it blank).'])
        # District may not be chosen if archive_date is set.
        if district and district.archive_date:
            self._errors['district'] = self.error_class(
                ['Please choose a current District for this Region (or leave it blank).'])
        return cleaned_data

    class Meta:
        model = Profile
        exclude = ('user',)


class BushfireFilterForm(forms.ModelForm):
    """
    Used to pass region and district to the filter template (in bushfire template)
    django-filter module does not allow filter chaining

    So passing a both form and filter to the context in the BushfireView, and still allowing the BushfireFilter to filter using the
    region and district passed from this form (i.e. region and filter are also declared in the BushfireFilter class)
    """

    include_archived = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super(BushfireFilterForm, self).__init__(*args, **kwargs)

        self.fields['region'].required = False
        self.fields['district'].required = False

    class Meta:
        fields = ('region', 'district', 'include_archived')
        model = Bushfire


class BushfireForm(forms.ModelForm):
    """
    Final and Review Form
    """
    fire_level = forms.ChoiceField(choices=Bushfire.FIRE_LEVEL_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    arson_squad_notified = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)

    class Meta:
        model = Bushfire
        fields = ('fire_contained_date', 'fire_controlled_date', 'fire_safe_date',
                  'first_attack', 'initial_control', 'final_control',
                  'other_first_attack', 'other_initial_control', 'other_final_control',
                  'area', 'area_limit', 'fire_level', 'arson_squad_notified', 'offence_no', 'job_code', 'reporting_year',
        )
        #exclude = ('initial_snapshot', 'init_authorised_by', 'init_authorised_date',
        #   )

#    def save(self, commit=True, *args, **kwargs):
#        m = super(BushfireForm, self).save(commit=False, *args, **kwargs)
#        import ipdb; ipdb.set_trace()

    def clean(self):
        cleaned_data = super(BushfireForm, self).clean()

        #import ipdb; ipdb.set_trace()
        # FINAL Form
        first_attack = self.cleaned_data['first_attack']
        if not first_attack:
            self.add_error('first_attack', 'Must specify First attack agency.')
        if first_attack and first_attack.name.upper().startswith('OTHER'):
            if not self.cleaned_data['other_first_attack']:
                self.add_error('other_first_attack', 'Must specify, if Initial attack agency is Other.')

        initial_control = self.cleaned_data['initial_control']
        if not initial_control:
            self.add_error('initial_control', 'Must specify Initial control agency.')
        if initial_control and initial_control.name.upper().startswith('OTHER'):
            if not self.cleaned_data['other_initial_control']:
                self.add_error('other_initial_control', 'Must specify, if Initial control agency is Other.')

        final_control = self.cleaned_data['final_control']
        if not final_control:
            self.add_error('final_control', 'Must specify Final control agency.')
        if final_control and final_control.name.upper().startswith('OTHER'):
            if not self.cleaned_data['other_final_control']:
                self.add_error('other_final_control', 'Must specify, if Final control agency is Other.')


class BushfireCreateBaseForm(forms.ModelForm):
    days = forms.IntegerField(label='Days', required=False)
    hours = forms.IntegerField(label='Hours', required=False)
    dispatch_pw = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    dispatch_aerial = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    fire_level = forms.ChoiceField(choices=Bushfire.FIRE_LEVEL_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    investigation_req = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    cause_state = forms.ChoiceField(choices=Bushfire.CAUSE_STATE_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    origin_point_str = forms.CharField(required=False, widget=DisplayOnlyField())#, widget=forms.TextInput(attrs={'readonly':'readonly'}))
    media_alert_req = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    park_trail_impacted = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)
    assistance_req = forms.ChoiceField(choices=YESNO_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer), required=False)

    class Meta:
        model = Bushfire
        fields = ('region', 'district', 'dfes_incident_no',
        #fields = ('region', 'district', 'fire_number', 'job_code', 'dfes_incident_no',
                  'name', 'year', 'fire_level', 'field_officer', 'duty_officer', 'init_authorised_by', 'init_authorised_date',
                  'media_alert_req', 'park_trail_impacted', 'fire_position', 'fire_position_override',
                  'fire_detected_date', 'dispatch_pw_date', 'dispatch_aerial_date', 'fuel_type',
                  'assistance_req', 'assistance_details', 'communications', 'other_info',
                  'cause', 'cause_state', 'other_cause', 'tenure', 'other_tenure',
                  'days','hours',
                  'dispatch_pw', 'dispatch_aerial',
                  'investigation_req',
		  'area', 'area_unknown', 'origin_point_str', 'origin_point', 'fire_boundary',
                 )

#    def clean_investigation_req(self):
#        if not self.cleaned_data.has_key('investigation_req'):
#            raise ValidationError('Must specify investigation required')
#
#        investigation_req = eval(self.cleaned_data['investigation_req'])
#        return investigation_req


    def clean(self):
        cleaned_data = super(BushfireCreateBaseForm, self).clean()

        #import ipdb; ipdb.set_trace()
        # Resetting forms fields declared above to None (from '') if None if not set in form
        if not self.cleaned_data['dispatch_pw']: self.cleaned_data['dispatch_pw'] = None
        if not self.cleaned_data['dispatch_aerial']: self.cleaned_data['dispatch_aerial'] = None
        if not self.cleaned_data['fire_level']: self.cleaned_data['fire_level'] = None
        if not self.cleaned_data['investigation_req']: self.cleaned_data['investigation_req'] = None
        if not self.cleaned_data['cause_state']: self.cleaned_data['cause_state'] = None
        if not self.cleaned_data['media_alert_req']: self.cleaned_data['media_alert_req'] = None
        if not self.cleaned_data['park_trail_impacted']: self.cleaned_data['park_trail_impacted'] = None
        if not self.cleaned_data['assistance_req']: self.cleaned_data['assistance_req'] = None


        if self.cleaned_data['dispatch_pw'] and eval(self.cleaned_data['dispatch_pw']):
            if not self.cleaned_data['dispatch_pw_date']:
                self.add_error('dispatch_pw_date', 'Must specify Date and Time of dispatch, if resource is dispatched.')
            if not self.cleaned_data['field_officer']:
                self.add_error('field_officer', 'Must specify Field Officer, if resource is dispatched.')

        if self.cleaned_data['dispatch_aerial'] and eval(self.cleaned_data['dispatch_aerial']):
            if not self.cleaned_data['dispatch_aerial_date']:
                self.add_error('dispatch_aerial_date', 'Must specify Date and Time of dispatch, if resource is dispatched.')

#        if self.cleaned_data['fire_not_found']:
#            if self.cleaned_data['area']:
#                area = round(float(self.cleaned_data['area']), 2)
#                if area < 0.01:
#                    self.add_error('area', 'Must specify Area, if Fire Not Found.')
#            else:
#                self.add_error('area', 'Must specify Area, if Fire Not Found.')

        if self.cleaned_data['cause']:
            cause = self.cleaned_data['cause']
            if cause.name.upper().startswith('OTHER'):
                if not self.cleaned_data['other_cause']:
                    self.add_error('other_cause', 'Must specify, if Fire Cause is Other.')

        if self.cleaned_data['tenure']:
            tenure = self.cleaned_data['tenure']
            if tenure.name.upper().startswith('OTHER'):
                if not self.cleaned_data['other_tenure']:
                    self.add_error('other_tenure', 'Must specify, if Tenure of ignition point is Other.')




class BushfireCreateForm(BushfireCreateBaseForm):
    def __init__(self, *args, **kwargs):
        super(BushfireCreateForm, self).__init__(*args, **kwargs)

#    def clean(self):
#	cleaned_data = super(BushfireCreateForm, self).clean()
#        import ipdb; ipdb.set_trace()
#        district = self.cleaned_data['district']
#        fire_number = self.cleaned_data['fire_number']
#        year = self.cleaned_data['year']
#        bushfire = Bushfire.objects.filter(fire_number=fire_number)
#        if bushfire:
#            raise ValidationError('There is already a Bushfire with this Fire Number {}'.format(fire_number))


class BushfireInitUpdateForm(BushfireCreateBaseForm):
    def clean(self):
        """
        Form can be saved prior to sign-off, without checking req'd fields.
        Required fields are checked during Authorisation sign-off, therefore checking and adding error fields manually
        """
	cleaned_data = super(BushfireInitUpdateForm, self).clean()
        req_fields = [
            'name', 'fire_level', 'init_authorised_by', 'init_authorised_date',
            'cause',
            'field_officer',
            #'known_possible',
        ]

        req_dep_fields = { # required dependent fields
            'cause': 'other_cause',
        }

        if self.cleaned_data['init_authorised_by']:
            # check all required fields
            #import ipdb; ipdb.set_trace()
            [self.add_error(field, 'This field is required.') for field in req_fields if not self.cleaned_data.has_key(field) or not self.cleaned_data[field]]

            # check if 'Other' has been selected from drop down and field has been set
            for field in req_dep_fields.keys():
                if self.cleaned_data.has_key(field) and 'other' in str(self.cleaned_data[field]).lower():
                    other_field = self.cleaned_data[req_dep_fields[field]]
                    if not other_field:
                        self.add_error(req_dep_fields[field], 'This field is required.')

#class BaseAreaBurntFormSet(BaseInlineFormSet):
#    def clean(self):
#        """
#        Adds validation to check:
#            1. no duplicate (tenure, fuel_type) combination
#        """
#        #import ipdb; ipdb.set_trace()
#        if any(self.errors):
#            return
#
#        duplicates = False
#        tenures = []
#
#        #import ipdb; ipdb.set_trace()
#        for form in self.forms:
#            if form.cleaned_data:
#                tenure = form.cleaned_data['tenure'] if form.cleaned_data.has_key('tenure') else None
#                area = form.cleaned_data['area'] if form.cleaned_data.has_key('area') else None
#                remove = form.cleaned_data['DELETE'] if form.cleaned_data.has_key('DELETE') else False
#
#                if not remove:
#                    # Check that no two records have the same (tenure and fuel_type) combination
#                    #if tenure and fuel_type and area:
#                    if tenure and area:
#                        if set([(tenure.name)]).issubset(tenures):
#                            duplicates = True
#                        tenures.append((tenure.name))
#
#                    if duplicates:
#			form.add_error('tenure', 'Duplicate: Tenure must be unique')

#class BaseInjuryFormSet(BaseInlineFormSet):
#    def clean(self):
#        """
#        Adds validation to check:
#            1. no duplicate (injury_type) combination
#            2. all fields are filled
#        """
#        #import ipdb; ipdb.set_trace()
#        if any(self.errors):
#            return
#
#        duplicates = False
#        injuries = []
#
#        import ipdb; ipdb.set_trace()
#        for form in self.forms:
#            if form.cleaned_data:
#                tenure = form.cleaned_data['injury_type'] if form.cleaned_data.has_key('tenure') else None
#                area = form.cleaned_data['number'] if form.cleaned_data.has_key('number') else None
#                remove = form.cleaned_data['DELETE'] if form.cleaned_data.has_key('DELETE') else False
#
#                if not remove:
#                    # Check that no two records have the same (tenure and fuel_type) combination
#                    #if tenure and fuel_type and area:
#                    if injury_type and number:
#                        if set([(injury_type.name)]).issubset(injuries):
#                            duplicates = True
#                        injuries.append((injury_type.name))
#
#                    if duplicates:
#                        form.add_error('injury_type', 'Duplicate: Injury type must be unique')
#
#                    # check all fields have been filled
#                    if not (injury_type and number):
#                        if not injury_type:
#                            form.add_error('injury_type', 'Injury type required')
#                        if not number:
#                            form.add_error('number', 'Number required')


class AreaBurntForm(forms.ModelForm):
    class Meta:
        model = AreaBurnt
        fields = ('tenure', 'area',)

    def __init__(self, *args, **kwargs):
        super(AreaBurntForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['tenure'].widget.attrs['readonly'] = True
            self.fields['area'].widget.attrs['readonly'] = True

#AreaBurntFormSet            = inlineformset_factory(Bushfire, AreaBurnt, formset=BaseAreaBurntFormSet, extra=0, min_num=1, validate_min=True, exclude=())
#AreaBurntFormSet            = inlineformset_factory(Bushfire, AreaBurnt, extra=0, min_num=1, validate_min=True, exclude=())
AreaBurntFormSet            = inlineformset_factory(Bushfire, AreaBurnt, extra=0, min_num=0, exclude=(), form=AreaBurntForm)
#AreaBurntFormSet            = inlineformset_factory(Bushfire, AreaBurnt, extra=0, min_num=0, exclude=())
#InjuryFormSet               = inlineformset_factory(Bushfire, Injury, formset=BaseInjuryFormSet, extra=1, max_num=7, min_num=0, exclude=())
InjuryFormSet               = inlineformset_factory(Bushfire, Injury, extra=1, max_num=7, min_num=0, exclude=())
DamageFormSet               = inlineformset_factory(Bushfire, Damage, extra=1, max_num=7, min_num=0, exclude=())


"""
NEXT - For Testing ONLY
"""

from bfrs.models import (BushfireTest)
class BushfireTestForm(forms.ModelForm):
    class Meta:
        model = BushfireTest
        fields = ('region', 'district')



