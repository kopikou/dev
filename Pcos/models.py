import datetime
from django.db import models

from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator



BOOL_CHOICES = ((True,'Есть'), (False,'Нет'))	

class Ethnicity(models.Model):
	name_ethnicity = models.CharField('Наименование ethnicity', max_length=50)
	def __str__(self):
		return self.name_ethnicity

class Doctor(models.Model):
	name_doctor = models.CharField('Имя доктора', max_length=200)
	def __str__(self):
		return self.name_doctor



class Patient(models.Model):
	Sex = (
    ('1','Мужской'),
    ('2','Женский'),
)
	Urban = (
    ('1','Город'),
    ('2','Сельская местность'),
)
	patient_name 	 = models.CharField('ФИО', max_length=200)
	day_of_birth     = models.DateField('Дата рождения')
	ethnicity_key    = models.ForeignKey(Ethnicity, 	  blank=True, null=True, on_delete=models.CASCADE)
	card_number		 = models.CharField('Номер карты',  max_length=20)
	barcode			 = models.CharField('Штрих-код', 	  blank=True, null=True, max_length=20)
	sex				 = models.CharField(max_length=15, choices=Sex, default='2')
	place_of_birth   = models.CharField('Место рождения', blank=True, null=True, max_length=20)
	urban_rural		 = models.CharField(max_length=15, 	  blank=True, null=True, choices=Urban, default='1')
	day_of_begin     = models.DateField('Дата начала диспансерного наблюдения')
	def __str__(self):
		return self.patient_name

class Visit(models.Model):
	patient_key			= models.ForeignKey(Patient, on_delete=models.CASCADE)
	doctor_key			= models.ForeignKey(Doctor, on_delete=models.CASCADE)
	date 				= models.DateField()
	age_visit			= models.PositiveIntegerField()
	height				= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	weight				= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	BMI					= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	SBP					= models.PositiveIntegerField(blank=True, null=True)
	DBP					= models.PositiveIntegerField(blank=True, null=True)
	pulse  				= models.PositiveIntegerField(blank=True, null=True)

	inform_consent		= models.BooleanField(default=True)
	comply_all_study	= models.BooleanField(default=True)
	female_age			= models.BooleanField(default=True)
	current_preg_lact	= models.BooleanField(default=False)
	history_hysterectomy= models.BooleanField(default=False)
	risk_no_compliance	= models.BooleanField(default=False)
	unwillingness		= models.BooleanField(default=False)
	medicince_listed_now_10		= models.BooleanField(default=True)
	medicince_listed_3month_10	= models.BooleanField(default=True)
	pnya				= models.BooleanField(default=False)

	PCOS 				= models.IntegerField(blank=True, null=True)
	Exclusion 			= models.IntegerField(blank=True, null=True)
	Grey 				= models.IntegerField(blank=True, null=True)
	Phenotype 			= models.CharField('Фенотип', max_length=1,blank=True)
	PCOS_text 			= models.TextField('Заключение', max_length=500,blank=True)
	Exclusion_text		= models.TextField('Причины исключения', max_length=500,blank=True)
	
	def __str__(self):
		return str(self.id)+' от '+str(self.date)


class Ultrasound(models.Model):
	Ovary = (
    ('1','Визуализируется'),
    ('2', 'Не визуализируется'),
    ('3','Отсутствует'),
)
	patient_key			= models.ForeignKey(Patient,  on_delete=models.CASCADE)
	visit_key			= models.ForeignKey(Visit,  on_delete=models.CASCADE)
	doctor_key			= models.ForeignKey(Doctor, on_delete=models.CASCADE)
	left_ovary_key 		= models.CharField(max_length=15, choices=Ovary, default='1')
	right_ovary_key 	= models.CharField(max_length=15, choices=Ovary, default='1')
	date 				= models.DateField()

	right_volume_total  = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	right_follicle_total= models.PositiveIntegerField(blank=True, null=True)
	diameter_right_total= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	left_volume_total	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	left_follicle_total	= models.PositiveIntegerField(blank=True, null=True)
	diameter_left_total	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])

	left_ovary_front	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	right_ovary_front	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	left_ovary_posterior	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])	
	right_ovary_posterior	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	left_ovary_side		= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	right_ovary_side	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])

	def __str__(self):
		return str(self.date)



class Appointment(models.Model):
	Periods = (
    ('1','Регулярный'),
    ('2','Нерегулярный'),
    ('3','Отсутствует'),
)
	Disorders = (
	('1','Аменорея отсутствует'),
    ('2','Первичная аменорея'),
    ('3','Вторичная аменорея'),
)

	Hirsutism = (
	('1','Нет'),
    ('2','Есть'),
)

	patient_key			= models.ForeignKey(Patient,  on_delete=models.CASCADE)
	visit_key			= models.ForeignKey(Visit,    on_delete=models.CASCADE)
	doctor_key			= models.ForeignKey(Doctor,   on_delete=models.CASCADE)
	date 				= models.DateField()
	periods				= models.CharField(max_length=15, choices=Periods, default='1')
	type_menstrual_disorders_1	=	models.CharField(max_length=25, choices=Disorders, default='1')
	type_menstrual_disorders_3	=	models.BooleanField(choices=BOOL_CHOICES,  default='No')
	type_menstrual_disorders_4	=	models.BooleanField(choices=BOOL_CHOICES,  default='No')
	min_menstrual		= models.PositiveIntegerField()
	max_menstrual		= models.PositiveIntegerField()
	sum_physician		= models.PositiveIntegerField()
	hirsutism   		= models.CharField(max_length=25, blank=True, null=True, choices=Hirsutism, default='1')

	def __str__(self):
		return str(self.date)





class Laboratory_test(models.Model):

	patient_key			= models.ForeignKey(Patient,  on_delete=models.CASCADE)
	visit_key 			= models.ForeignKey(Visit, on_delete=models.CASCADE)
	
	date 				= models.DateField()
	day_mens_prl		= models.PositiveIntegerField()
	value_testosteron	= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_shbg			= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_dheas			= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_tsh			= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_17hp			= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_prl			= models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True,
		validators=[MinValueValidator(Decimal('0.00'))])
	

	value_testosteron_max	= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_IFA_max			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_dheas_max			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_tsh_min			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_tsh_max			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_17hp_max_1		= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_prl_max_1			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	value_prl_max_2			= models.DecimalField(max_digits=5,decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))])
	def __str__(self):
		return str(self.date)


