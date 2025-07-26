from django.shortcuts import render,redirect
from .models import Patient, Doctor, Ethnicity, Visit, Appointment, Ultrasound, Laboratory_test
from .forms import  FullForm, PatientForm, VisitForm, AppointmentForm, UltrasoundForm, LaboratoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse, JsonResponse
from datetime import datetime, date
from django.utils.dateformat import DateFormat
#from docx import *
#from docx.shared import Inches
#from io import BytesIO
from docxtpl import DocxTemplate
import os




def pcos(request):
	if request.user.is_authenticated:
		logout(request)
	username=request.POST.get('username')
	password=request.POST.get('password')
	user=authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		return redirect('/pcos/patients_list')
	return render(request, 'Pcos/patients/auth.html')





@login_required(login_url='/pcos/auth')
def patients_list(request):
	request.session['av']=0
	request.session['aa']=0
	request.session['al']=0
	request.session['au']=0
	try:
		patients_ = Patient.objects.order_by('id')
	except:
		raise Http404("Пациенты не найдены!")
	return render(request, 'Pcos/patients/patients_list.html',{'patients_':patients_})


@login_required(login_url='/pcos/auth')
def view_full(request, pk):
	patient_=Patient.objects.get(id=pk)
	request.session['id']=pk
	visits_ = Visit.objects.filter(patient_key=pk)
	appointments_ = Appointment.objects.filter(patient_key=pk)
	ultrasounds_ = Ultrasound.objects.filter(patient_key=pk)
	laboratory_results_=Laboratory_test.objects.filter(patient_key=pk)
	form= FullForm(instance=patient_)
	context = {
		'form':form,
		'patient_':patient_, 
		'visits_': visits_, 
		'appointments_':appointments_,
		'ultrasounds_':ultrasounds_,
		'laboratory_results_':laboratory_results_,
		'active_visit':request.session['av'],
		'active_appointment':request.session['aa'], 
		'active_ultrasound':request.session['au'], 
		'active_laboratory':request.session['al'],
		}

	request.session['av']=0
	request.session['aa']=0
	request.session['al']=0
	request.session['au']=0
	return render(request, 'Pcos/forms/full_form.html', context)

@login_required(login_url='/pcos/auth')
def add_patient(request):

	form=PatientForm()
	if request.method=='POST':
		form=PatientForm(request.POST)
		if form.is_valid():
			form.save()
			request.session['id']=form.instance.id
			request.session['av']=0
			request.session['aa']=0
			request.session['al']=0
			request.session['au']=0
			return redirect('/pcos/view_full/'+str(form.instance.id))
	context = {'form':form, 'new':1}
	return render(request, 'Pcos/forms/patient_form.html',context)

@login_required(login_url='/pcos/auth')
def edit_patient(request,pk):
	patient=Patient.objects.get(id=pk)
	form= PatientForm(instance=patient)
	if request.method=='POST':
		form=PatientForm(request.POST, instance=patient)
		if form.is_valid():
			form.save()
			request.session['id']=pk
			return redirect('/pcos/view_full/'+pk)
	context = {'form':form, 'new':0}
	return render(request, 'Pcos/forms/patient_form.html', context)

@login_required(login_url='/pcos/auth')
def add_visit(request, pk):
	form=VisitForm()

	form.fields['patient_key'].initial=Patient.objects.get(id=pk)
	form.fields['patient_key'].queryset = Patient.objects.filter(id=pk)
	if request.method=='POST':
		form=VisitForm(request.POST)
		if form.is_valid():
			form.save()
			request.session['av']=form.instance.id
			request.session['aa']=0
			request.session['au']=0
			request.session['al']=0
			return redirect('/pcos/view_full/'+pk)
	context = {'form':form, 'new':1, 'patient_key':pk}
	return render(request, 'Pcos/forms/visit_form.html',context)

@login_required(login_url='/pcos/auth')
def edit_visit(request, vk):
	visit=Visit.objects.get(id=vk)
	form= VisitForm(instance=visit)
	form.fields['patient_key'].queryset = Patient.objects.filter(id=visit.patient_key.id)
	request.session['av']=visit.id
	request.session['aa']=0
	request.session['au']=0
	request.session['al']=0
	if request.method=='POST':
		form=VisitForm(request.POST, instance=visit)
		if form.is_valid():
			form.save()
			return redirect('/pcos/view_full/'+str(visit.patient_key.id))
	context = {'form':form, 'new':0, 'patient_key':visit.patient_key.id}
	return render(request, 'Pcos/forms/visit_form.html', context)


@login_required(login_url='/pcos/auth')
def add_appointment(request, pk, vk):
	form=AppointmentForm()
	form.fields['patient_key'].initial=Patient.objects.get(id=pk)
	form.fields['visit_key'].initial=Visit.objects.get(id=vk)

	form.fields['patient_key'].queryset = Patient.objects.filter(id=pk)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=vk)
	request.session['av']=int(vk)
	request.session['aa']=0
	request.session['au']=0
	request.session['al']=0
	if request.method=='POST':
		form=AppointmentForm(request.POST)
		if form.is_valid():
			form.save()
			request.session['aa']=form.instance.id
			return redirect('/pcos/view_full/'+pk)

	context = {'form':form, 'new':1, 'patient_key':pk}
	return render(request, 'Pcos/forms/appointment_form.html',context)

@login_required(login_url='/pcos/auth')
def edit_appointment(request, ak):
	appointment=Appointment.objects.get(id=ak)
	form= AppointmentForm(instance=appointment)

	form.fields['patient_key'].queryset = Patient.objects.filter(id=appointment.patient_key.id)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=appointment.visit_key.id)
	request.session['aa']=appointment.id
	request.session['av']=appointment.visit_key.id
	request.session['au']=0
	request.session['al']=0
	if request.method=='POST':
		form=AppointmentForm(request.POST, instance=appointment)
		if form.is_valid():
			form.save()
			return redirect('/pcos/view_full/'+str(appointment.patient_key.id))

	context = {'form':form, 'new':0, 'patient_key':appointment.patient_key.id}
	return render(request, 'Pcos/forms/appointment_form.html', context)

@login_required(login_url='/pcos/auth')
def add_ultrasound(request, pk, vk):
	form=UltrasoundForm()
	form.fields['patient_key'].initial=Patient.objects.get(id=pk)
	form.fields['visit_key'].initial=Visit.objects.get(id=vk)

	form.fields['patient_key'].queryset = Patient.objects.filter(id=pk)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=vk)
	request.session['av']=int(vk)
	request.session['aa']=0
	request.session['au']=0
	request.session['al']=0
	if request.method=='POST':
		form=UltrasoundForm(request.POST)
		if form.is_valid():
			form.save()
			request.session['au']=form.instance.id
			return redirect('/pcos/view_full/'+pk)

	context = {'form':form, 'new':1, 'patient_key':pk}
	return render(request, 'Pcos/forms/ultrasound_form.html',context)

@login_required(login_url='/pcos/auth')
def edit_ultrasound(request, uk):
	ultrasound=Ultrasound.objects.get(id=uk)
	form= UltrasoundForm(instance=ultrasound)
	form.fields['patient_key'].queryset = Patient.objects.filter(id=ultrasound.patient_key.id)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=ultrasound.visit_key.id)
	request.session['au']=ultrasound.id
	request.session['aa']=0
	request.session['av']=ultrasound.visit_key.id
	request.session['al']=0
	if request.method=='POST':
		form=UltrasoundForm(request.POST, instance=ultrasound)
		if form.is_valid():
			form.save()
			return redirect('/pcos/view_full/'+str(ultrasound.patient_key.id))
	context = {'form':form, 'new':0, 'patient_key':ultrasound.patient_key.id}
	return render(request, 'Pcos/forms/ultrasound_form.html', context)

@login_required(login_url='/pcos/auth')
def add_laboratory(request, pk, vk):
	form=LaboratoryForm()
	form.fields['patient_key'].initial=Patient.objects.get(id=pk)
	form.fields['visit_key'].initial=Visit.objects.get(id=vk)
	form.fields['patient_key'].queryset = Patient.objects.filter(id=pk)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=vk)
	request.session['al']=0
	request.session['aa']=0
	request.session['av']=int(vk)
	request.session['au']=0
	if request.method=='POST':
		form=LaboratoryForm(request.POST)
		if form.is_valid():
			form.save()
			request.session['al']=form.instance.id
			return redirect('/pcos/view_full/'+pk)
	context = {'form':form, 'new':1, 'patient_key':pk}
	return render(request, 'Pcos/forms/laboratory_form.html',context)

@login_required(login_url='/pcos/auth')
def edit_laboratory(request, lk):
	laboratory=Laboratory_test.objects.get(id=lk)
	form= LaboratoryForm(instance=laboratory)
	form.fields['patient_key'].queryset = Patient.objects.filter(id=laboratory.patient_key.id)
	form.fields['visit_key'].queryset = Visit.objects.filter(id=laboratory.visit_key.id)
	request.session['al']=laboratory.id
	request.session['aa']=0
	request.session['av']=laboratory.visit_key.id
	request.session['au']=0
	if request.method=='POST':
		form=LaboratoryForm(request.POST, instance=laboratory)
		if form.is_valid():
			form.save()
			return redirect('/pcos/view_full/'+str(laboratory.patient_key.id))
	context = {'form':form, 'new':0, 'patient_key':laboratory.patient_key.id}
	return render(request, 'Pcos/forms/laboratory_form.html', context)

def calculate_age(request):
	if request.method == 'GET':
		patient_key 	= 	request.GET.get('patient_key')
		now_date 		= 	request.GET.get('now_date')
		patient 		=	Patient.objects.get(id=patient_key)
		birth	=	patient.day_of_birth
		now=datetime.strptime(now_date, "%Y-%m-%d").date()
		age= now.year - birth.year - ((now.month, now.day) < (birth.month, birth.day))
		return JsonResponse({
			"age"	:age,
		})
def get_ethnicity(request):
	if request.method == 'GET':
		patient_key 	= 	request.GET.get('patient_key')
		patient 		=	Patient.objects.get(id=patient_key)
		if patient.ethnicity_key==None:
			ethnicity_key = None
		else:	
			ethnicity_key	=	patient.ethnicity_key.id
		return JsonResponse({
			"ethnicity_key"	:ethnicity_key,
		})
def execute_query(request):
	if request.method == 'GET':
		patient_key 		= request.GET.get('patient_key')
		visit_key 	= request.GET.get('visit_key')
		patient =Patient.objects.get(id=patient_key)
		visit	=Visit.objects.get(id=visit_key)
		if patient.ethnicity_key==None:
			ethnicity_key = None
		else:	
			ethnicity_key	=	patient.ethnicity_key.id
		day_of_begin = patient.day_of_begin	
		appointments 	= Appointment.objects.filter(patient_key=patient_key, visit_key=visit_key)
		if not appointments:
			periods=None
			type_menstrual_disorders_1=None
			type_menstrual_disorders_2=None
			type_menstrual_disorders_3=None
			type_menstrual_disorders_4=None
			min_menstrual			  =None
			max_menstrual			  =None
			sum_physician			  =None
		else:
			last_appointment=appointments.latest('date')
			periods					  =last_appointment.periods
			type_menstrual_disorders_1=last_appointment.type_menstrual_disorders_1
			type_menstrual_disorders_3=last_appointment.type_menstrual_disorders_3
			type_menstrual_disorders_4=last_appointment.type_menstrual_disorders_4
			min_menstrual			  =last_appointment.min_menstrual
			max_menstrual			  =last_appointment.max_menstrual
			sum_physician			  =last_appointment.sum_physician

		
		ultrasounds 	= Ultrasound.objects.filter(patient_key=patient_key, visit_key=visit_key)
		if not ultrasounds:
			right_volume_total	=None
			right_follicle_total=None
			diameter_right_total=None
			left_volume_total	=None
			left_follicle_total	=None
			diameter_cyst_left	=None
		else:
			last_ultrasound	=ultrasounds.latest('date')
			right_volume_total	=last_ultrasound.right_volume_total
			right_follicle_total=last_ultrasound.right_follicle_total
			diameter_right_total=last_ultrasound.diameter_right_total
			left_volume_total	=last_ultrasound.left_volume_total
			left_follicle_total	=last_ultrasound.left_follicle_total
			diameter_left_total	=last_ultrasound.diameter_left_total

		laboratory_tests= Laboratory_test.objects.filter(patient_key=patient_key, visit_key=visit_key)
		if not laboratory_tests:
			value_testosteron	=None
			value_shbg 			=None
			value_dheas			=None
			value_tsh			=None
			day_mens_prl		=None
			value_17ph			=None
			value_prl 			=None
		else:
			last_laboratory_test	=laboratory_tests.latest('date')
			value_testosteron	=last_laboratory_test.value_testosteron
			value_shbg 			=last_laboratory_test.value_shbg
			value_dheas			=last_laboratory_test.value_dheas
			value_tsh			=last_laboratory_test.value_tsh
			day_mens_prl		=last_laboratory_test.day_mens_prl
			value_17ph			=last_laboratory_test.value_17hp
			value_prl 			=last_laboratory_test.value_prl

			value_testosteron_max	=last_laboratory_test.value_testosteron_max
			value_IFA_max	        =last_laboratory_test.value_IFA_max
			value_dheas_max			=last_laboratory_test.value_dheas_max
			value_tsh_min			=last_laboratory_test.value_tsh_min
			value_tsh_max			=last_laboratory_test.value_tsh_max
			value_17hp_max_1		=last_laboratory_test.value_17hp_max_1
			value_prl_max_1			=last_laboratory_test.value_prl_max_1
			value_prl_max_2			=last_laboratory_test.value_prl_max_2




		df=DateFormat(day_of_begin)
		day_of_begin= df.format('d.m.Y')
		

		return JsonResponse({
			"ethnicity"					:ethnicity_key,
			"periods"					:periods,
			"type_menstrual_disorders_1":type_menstrual_disorders_1,
			"type_menstrual_disorders_3":type_menstrual_disorders_3,
			"type_menstrual_disorders_4":type_menstrual_disorders_4,
			"min_menstrual"				:min_menstrual,
			"max_menstrual"				:max_menstrual,
			"sum_physician"				:sum_physician,

		
			"right_volume_total"		:right_volume_total,
			"right_follicle_total"		:right_follicle_total,
			"diameter_right_total"		:diameter_right_total,
			"left_volume_total"			:left_volume_total,
			"left_follicle_total"		:left_follicle_total,
			"diameter_left_total"		:diameter_left_total,


			"day_of_begin"			:day_of_begin,
			
			
			"value_testosteron"			:value_testosteron,
			"value_shbg"				:value_shbg,
			"value_dheas"				:value_dheas,
			"value_tsh"					:value_tsh,
			"day_mens_prl"				:day_mens_prl,
			"value_17hp"				:value_17ph,
			"value_prl"					:value_prl,

			"value_testosteron_max"		:value_testosteron_max,
			"value_IFA_max"	        	:value_IFA_max,
			"value_dheas_max"			:value_dheas_max,
			"value_tsh_min"				:value_tsh_min,
			"value_tsh_max"				:value_tsh_max,
			"value_17hp_max_1"			:value_17hp_max_1,
			"value_prl_max_1"			:value_prl_max_1,
			"value_prl_max_2"			:value_prl_max_2,
		
			"age_visit1"				:visit.age_visit,
			"inform_consent"			:visit.inform_consent,
			"comply_all_study"			:visit.comply_all_study,
			"female_age"				:visit.female_age,
			"current_preg_lact"			:visit.current_preg_lact, 
			"history_hysterectomy"		:visit.history_hysterectomy,
			"risk_no_compliance"		:visit.risk_no_compliance,
			"unwillingness"				:visit.unwillingness,
			"medicince_listed_now___10"	 	:visit.medicince_listed_now_10,
			"medicince_listed_3month___10"	:visit.medicince_listed_3month_10,
			"pnya"						:visit.pnya,



		})





def logout_user(request):

	logout(request)
	return redirect('/pcos/auth')
		

@login_required(login_url='/pcos/auth')
def export_to_document(request):
  
  path=os.path.abspath(os.getcwd() +'/Pcos/static/Pcos/word_templates/pcos_template.docx')
 # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
 # print(os.getcwd())
  doc = DocxTemplate(path) 
  context = { 'diagnosis' : request.GET.get('text'),
  						'date' 			: request.GET.get('date'),
  						'doctor' 		: request.user,
  }  
  response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
  response["Content-Disposition"] = 'filename="generated_doc.docx"' 
  doc.render(context)
  doc.save(response)
  return response

@login_required(login_url='/pcos/auth')
def report_filework(request):
	return render(request, 'Pcos/reports/report_filework.html')


@login_required(login_url='/pcos/auth')
def report_exportdata(request):
	return render(request, 'Pcos/reports/report_exportdata.html')