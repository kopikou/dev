from django.forms import  ModelForm,  CharField, PasswordInput, TextInput, DateInput, Textarea, ModelChoiceField,  RadioSelect, IntegerField, FloatField
from .models import Patient, Ethnicity,Visit, Appointment, Doctor, Ultrasound, Laboratory_test
from django.contrib.auth.models import User



class FullForm(ModelForm):
	class Meta:
		model = Patient
		sex				 = IntegerField()
		urban_rural		 = IntegerField()
		fields=['patient_name','day_of_birth','ethnicity_key','card_number','barcode','sex','place_of_birth','urban_rural','day_of_begin']
		ethnicity_key=ModelChoiceField(
				queryset=Ethnicity.objects.all(), 
				empty_label=None)
		widgets={
			"patient_name":TextInput(attrs={
				'class':'form-control',
				'placeholder':'ФИО пациента'
				}),
			"day_of_birth":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата рождения',
				'input_type' : 'text',
				'type': 'date'
				}), 
			"card_number":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Номер карты'
				}),
			"barcode":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Штрих-код'
				}),
			"place_of_birth":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Место рождения'
				}),
			"day_of_begin":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата начала диспансерного наблюдения',
				'input_type' : 'text',
				'type': 'date'
				}), 
		};



class PatientForm(ModelForm):
	class Meta:
		model = Patient
		sex				 = IntegerField()
		urban_rural		 = IntegerField()
		fields=['patient_name','day_of_birth','ethnicity_key','card_number','barcode','sex','place_of_birth','urban_rural','day_of_begin']
		ethnicity_key=ModelChoiceField(
				queryset=Ethnicity.objects.all(), 
				empty_label=None)
		widgets={
			"patient_name":TextInput(attrs={
				'class':'form-control',
				'placeholder':'ФИО пациента'
				}),
			"day_of_birth":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата рождения',
				'input_type' : 'text',
				'type': 'date'
				}), 
			"card_number":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Номер карты'
				}),
			"barcode":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Штрих-код'
				}),
			"place_of_birth":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Место рождения'
				}),
			"day_of_begin":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата начала диспансерного наблюдения',
				'input_type' : 'text',
				'type': 'date'
				}), 
		};



class VisitForm(ModelForm):
	class Meta:
		model=Visit
		fields=['patient_key','doctor_key','date','age_visit', 'height','weight','BMI','SBP',
		'DBP','pulse','inform_consent', 'comply_all_study', 'female_age',	'current_preg_lact',
		 'history_hysterectomy', 'risk_no_compliance', 'unwillingness', 'medicince_listed_now_10',
		'medicince_listed_3month_10','pnya','PCOS','Exclusion','Grey', 'Phenotype', 'PCOS_text', 'Exclusion_text']
		patient_key=ModelChoiceField(
				queryset=Patient.objects.all(), 
				empty_label=None)
		doctor_key=ModelChoiceField(
				queryset=Doctor.objects.all(), 
				empty_label=None)

		height							= FloatField()
		weight							= FloatField()
		BMI								= FloatField()
		SBP								= IntegerField()
		DBP								= IntegerField()
		pulse							= IntegerField()

		age_visit						= IntegerField()
		inform_consent					= RadioSelect()
		comply_all_study				= RadioSelect()
		female_age						= RadioSelect()
		current_preg_lact				= RadioSelect()
		history_hysterectomy			= RadioSelect()
		risk_no_compliance				= RadioSelect()
		unwillingness					= RadioSelect()
		medicince_listed_now_10			= RadioSelect()
		medicince_listed_3month_10		= RadioSelect()
		pnya							= RadioSelect()
		PCOS 		=	IntegerField()
		Exclusion 	= 	IntegerField()
		Grey		=	IntegerField()

		widgets={
			"date":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата визита',
				'input_type' : 'text',
				'type': 'date'
				}),
			"Phenotype":TextInput(attrs={
				'class':'form-control',
				'placeholder':'Фенотип'
				}),
			"PCOS_text":Textarea(attrs={
				'class':'form-control',
				'placeholder':'Текст заключения'
				}), 
			"Exclusion_text":Textarea(attrs={
				'class':'form-control',
				'placeholder':'Текст исключения'
				}),         
		};
	
class AppointmentForm(ModelForm):
	class Meta:
		model = Appointment
		fields=['patient_key','doctor_key','visit_key','date','periods','type_menstrual_disorders_1',
		'type_menstrual_disorders_3','type_menstrual_disorders_4','min_menstrual','max_menstrual',
		'sum_physician','hirsutism']
		patient_key=ModelChoiceField(
				queryset=Patient.objects.all(), 
				empty_label=None)
		doctor_key=ModelChoiceField(
				queryset=Doctor.objects.all(), 
				empty_label=None)
		visit_key=ModelChoiceField(
				queryset=Visit.objects.all(), 
				empty_label=None)
		periods:IntegerField()
		type_menstrual_disorders_1:IntegerField()
		type_menstrual_disorders_3:RadioSelect()
		type_menstrual_disorders_4:RadioSelect()
		min_menstrual:IntegerField()
		max_menstrual:IntegerField()
		sum_physician:IntegerField()
		hirsutism:IntegerField()
		widgets={	
			"date":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата приема',
				'input_type' : 'text',
				'type': 'date'
				}),  
			"type_menstrual_disorders_3":RadioSelect(attrs={
				'class':'form-control'
				}),
			"type_menstrual_disorders_4":RadioSelect(attrs={
				'class':'form-control'
				}),      
		}

class UltrasoundForm(ModelForm):
	class Meta:
		model = Ultrasound
		fields=['patient_key','visit_key', 'doctor_key','date','left_ovary_key','right_ovary_key',
		'right_volume_total','right_follicle_total','diameter_right_total','left_volume_total',
		'left_follicle_total','diameter_left_total','left_ovary_front', 'right_ovary_front','left_ovary_posterior',
		'right_ovary_posterior','left_ovary_side','right_ovary_side']
		patient_key=ModelChoiceField(
				queryset=Patient.objects.all(), 
				empty_label=None)
		doctor_key=ModelChoiceField(
				queryset=Doctor.objects.all(), 
				empty_label=None)
		visit_key=ModelChoiceField(
				queryset=Visit.objects.all(), 
				empty_label=None)
		left_ovary_key		=IntegerField()
		right_ovary_key		=IntegerField()
		right_volume_total	:FloatField()
		right_follicle_total:IntegerField()
		diameter_right_total:FloatField()
		left_volume_total	:FloatField()
		left_follicle_total	:IntegerField()
		diameter_left_total	:FloatField()
		left_ovary_front	:FloatField()
		right_ovary_front	:FloatField()
		left_ovary_posterior	:FloatField()	
		right_ovary_posterior	:FloatField()
		left_ovary_side		:FloatField()
		right_ovary_side	:FloatField()
		widgets={
			"date":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата приема',
				'input_type' : 'text',
				'type': 'date'
				}),
			      
		}

class LaboratoryForm(ModelForm):
	class Meta:
		model = Laboratory_test
		fields=['patient_key','visit_key','date', 'value_testosteron', 'value_shbg','value_tsh', 'day_mens_prl', 
		'value_17hp','value_prl', 'value_dheas','value_testosteron_max','value_dheas_max',
		'value_tsh_min', 'value_tsh_max','value_IFA_max', 'value_17hp_max_1','value_prl_max_1',
		'value_prl_max_2']
		patient_key=ModelChoiceField(
				queryset=Patient.objects.all(), 
				empty_label=None)
		visit_key=ModelChoiceField(
				queryset=Visit.objects.all(), 
				empty_label=None)
		
		value_testosteron:FloatField()
		value_shbg 		 :FloatField()
		value_tsh 		 :FloatField()
		day_mens_prl 	 :IntegerField()
		value_17hp 		 :FloatField()
		value_prl 		 :FloatField()
		value_dheas		 :FloatField()
		#*****нормативы*****************************
		
		value_testosteron_max:FloatField()
		

		value_IFA_max 		 :FloatField()
		value_dheas_max		 :FloatField()

		value_tsh_min 		 :FloatField()
		value_tsh_max 		 :FloatField()
		value_17hp_max_1 	 :FloatField()
		value_prl_max_1 	 :FloatField()
		value_prl_max_2 	 :FloatField()
		widgets={
			"date":DateInput(format=('%Y-%m-%d'), attrs={
				'class':'form-control',
				'placeholder':'Дата приема',
				'input_type' : 'text',
				'type': 'date'
				}),       
		}
