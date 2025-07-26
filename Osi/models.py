from django.db import models
#from django.forms import NumberInput
from Osi.validators import validate_file_size
from django.core.validators import MaxValueValidator, MinValueValidator
import os


def fields_file_path(instance, filename):
    path = 'Osi/fields/uploaded/'
    #if not os.path.exists(path):
    #    os.makedirs(path)
    return os.path.join(path, filename)

def file_file_path(instance, filename):
    path = 'Osi/file/uploaded/'
    return os.path.join(path, filename)

def fields_default_file_path(instance, filename):
    path = 'Osi/fields/default/'
    return os.path.join(path, filename)


#fields models
class FieldsMode(models.Model):
    mode = models.IntegerField(default=0)
    user_session_key = models.CharField(max_length=100, default='')


class FieldsData(models.Model):
    data_file = models.FileField(upload_to=fields_file_path, validators=[validate_file_size])
    numerator_params_quantity = models.IntegerField(default='', validators=[MinValueValidator(3), MaxValueValidator(15)])
    denominator_params_quantity = models.IntegerField(default='', validators=[MinValueValidator(4), MaxValueValidator(15)])
    divide_by_age = models.BooleanField(default=False)
    divide_by_gender = models.BooleanField(default=False)
    divide_by_ethnicity = models.BooleanField(default=False)
    user_session_key = models.CharField(max_length=100, default='')

class FieldsSelectionCol(models.Model):
    selection_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FieldsSelectionColValue(models.Model):
    control_selection_value = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    selection_col_values = models.CharField(max_length=10000, default='')


class FieldsDivisionCols(models.Model):
    age_col = models.CharField(max_length=30, default='')
    gender_col = models.CharField(max_length=30, default='')
    ethnicity_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FieldsPatientInfo(models.Model):
    patient_id = models.IntegerField(default='')
    age = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    gender = models.CharField(max_length=20, default='')
    ethnicity = models.CharField(max_length=40, default='')
    user_session_key = models.CharField(max_length=100, default='')
    gender_values = models.CharField(max_length=10000, default='')
    ethnicity_values = models.CharField(max_length=10000, default='')


class FieldsPatientNumParam(models.Model):
    name = models.CharField(max_length=40, default='')
    value = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    norm = models.CharField(max_length=60, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FieldsPatientDenParam(models.Model):
    name = models.CharField(max_length=40, default='')
    value = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    norm = models.CharField(max_length=60, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FieldsAgeIntervalBorders(models.Model):
    lower_border_value = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    upper_border_value = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    user_session_key = models.CharField(max_length=100, default='')


class FieldsPatientTable(models.Model):
    patient_table = models.CharField(max_length=3000, default='')
    user_session_key = models.CharField(max_length=100, default='')


class FieldsPatientResultExcelFile(models.Model):
    result_excel_file = models.FileField()
    user_session_key = models.CharField(max_length=100, default='')


class FieldsExcelFileDefault(models.Model):
    excel_file_default = models.FileField(upload_to=fields_default_file_path)


class FieldsDivideByEthnicityDefault(models.Model):
    divide_by_ethnicity = models.IntegerField(default=0)
    user_session_key = models.CharField(max_length=100, default='')


class FieldsPatientDefault(models.Model):
    patient_id = models.IntegerField(default='')
    age = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    ethnicity = models.CharField(max_length=40, default='')
    dk = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    kd_st = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    mda = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    cod = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    gsh = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    e = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    a = models.FloatField(default='', validators=[MinValueValidator(0.0), MaxValueValidator(30.0)])
    ethnicity_values = models.CharField(max_length=10000, default='')
    user_session_key = models.CharField(max_length=100, default='')


#file models
class FileData(models.Model):
    data_file = models.FileField(upload_to=file_file_path, validators=[validate_file_size])
    numerator_params_quantity = models.IntegerField(default='', validators=[MinValueValidator(3), MaxValueValidator(15)])
    denominator_params_quantity = models.IntegerField(default='', validators=[MinValueValidator(4), MaxValueValidator(15)])
    divide_by_age = models.BooleanField(default=False)
    divide_by_gender = models.BooleanField(default=False)
    divide_by_ethnicity = models.BooleanField(default=False)
    user_session_key = models.CharField(max_length=100, default='')


class FileIdCol(models.Model):
    id_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FileNumeratorParamCol(models.Model):
    num_param_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FileDenominatorParamCol(models.Model):
    den_param_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FileDivisionCols(models.Model):
    age_col = models.CharField(max_length=30, default='')
    gender_col = models.CharField(max_length=30, default='')
    ethnicity_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FileGenderValuesQuantity(models.Model):
    gender_values_quantity = models.IntegerField(default='')
    user_session_key = models.CharField(max_length=100, default='')


class FileGenderValue(models.Model):
    gender_value = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    gender_values = models.CharField(max_length=10000, default='')


class FileEthnicityValuesQuantity(models.Model):
    ethnicity_values_quantity = models.IntegerField(default='')
    user_session_key = models.CharField(max_length=100, default='')
    unique_values_quantity = models.IntegerField(default='')


class FileEthnicityValue(models.Model):
    ethnicity_value = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    ethnicity_values = models.CharField(max_length=10000, default='')


class FileAgeIntervalsQuantity(models.Model):
    intervals_quantity = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(15)])
    user_session_key = models.CharField(max_length=100, default='')


class FileAgeIntervalBorders(models.Model):
    lower_border_value = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    upper_border_value = models.IntegerField(default='', validators=[MinValueValidator(0), MaxValueValidator(150)])
    user_session_key = models.CharField(max_length=100, default='')


class FileSelectionCol(models.Model):
    selection_col = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    data_columns = models.CharField(max_length=3000, default='')


class FileSelectionColValues(models.Model):
    control_selection_value = models.CharField(max_length=30, default='')
    case_selection_value = models.CharField(max_length=30, default='')
    user_session_key = models.CharField(max_length=100, default='')
    selection_col_values = models.CharField(max_length=10000, default='')


class FileOsiResultsArchive(models.Model):
    osi_results_archive = models.FileField()
    user_session_key = models.CharField(max_length=100, default='')


class FileOsiResultsFile(models.Model):
    osi_results_file = models.FileField()
    user_session_key = models.CharField(max_length=100, default='')


