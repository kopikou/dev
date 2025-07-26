from django import forms
from .models import FieldsMode, FieldsData, FieldsSelectionCol, FieldsSelectionColValue, FieldsDivisionCols,\
    FieldsPatientInfo, FieldsPatientNumParam, FieldsPatientDenParam, FieldsAgeIntervalBorders,\
    FieldsDivideByEthnicityDefault, FieldsPatientDefault
from .models import FileData, FileIdCol, FileNumeratorParamCol, FileDenominatorParamCol, FileDivisionCols,\
    FileAgeIntervalsQuantity, FileAgeIntervalBorders, FileGenderValuesQuantity, FileGenderValue,\
    FileEthnicityValuesQuantity, FileEthnicityValue, FileSelectionCol, FileSelectionColValues
import pickle
from math import isnan


#fields forms
class FieldsModeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsModeForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = [[1, "Стандартный вариант (с указанием данных контрольной выборки"],
                       [2, "Вариант по умолчанию (используются данные из нашей контрольной выборки [Женщины от 18 до 45 лет])"]]
        self.fields['mode'].widget = forms.RadioSelect(choices=col_choices,
                                                                    attrs={'class': "form-control"})

    class Meta:
        model = FieldsMode
        fields = [
            'mode',
            'user_session_key',
        ]


class FieldsDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsDataForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()

    class Meta:
        model = FieldsData
        fields = [
            'data_file',
            'numerator_params_quantity',
            'denominator_params_quantity',
            'divide_by_age',
            'divide_by_gender',
            'divide_by_ethnicity',
            'user_session_key',
        ]


class FieldsSelectionColForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsSelectionColForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['selection_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FieldsSelectionCol
        fields = [
            'selection_col',
            'data_columns',
            'user_session_key',
        ]


class FieldsSelectionColValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        selection_col_values_serialized = kwargs.pop('selection_col_values')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsSelectionColValueForm, self).__init__(*args, **kwargs)
        self.fields['selection_col_values'].initial = selection_col_values_serialized
        self.fields['selection_col_values'].widget.attrs['disabled'] = True
        self.fields['selection_col_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        selection_col_values = pickle.loads(selection_col_values_serialized)
        col_choices = []
        for value in selection_col_values:
            if not isnan(value):
                col_choices.append([value, value])
        self.fields['control_selection_value'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FieldsSelectionColValue
        fields = [
            'control_selection_value',
            'user_session_key',
            'selection_col_values'
        ]


class FieldsDivisionColsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsDivisionColsForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        data = FieldsData.objects.filter(user_session_key=user_session_key).order_by("-id")[:1][0]
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['age_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['gender_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['ethnicity_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        if not data.divide_by_age:
            self.fields['age_col'].widget.attrs['disabled'] = True
            self.fields['age_col'].required = False
        if not data.divide_by_gender:
            self.fields['gender_col'].widget.attrs['disabled'] = True
            self.fields['gender_col'].required = False
        if not data.divide_by_ethnicity:
            self.fields['ethnicity_col'].widget.attrs['disabled'] = True
            self.fields['ethnicity_col'].required = False

    class Meta:
        model = FieldsDivisionCols
        fields = [
            'age_col',
            'gender_col',
            'ethnicity_col',
            'data_columns',
            'user_session_key',
        ]


class FieldsPatientInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        ethnicity_values_serialized = kwargs.pop('ethnicity_values')
        gender_values_serialized = kwargs.pop('gender_values')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsPatientInfoForm, self).__init__(*args, **kwargs)
        self.fields['ethnicity_values'].initial = ethnicity_values_serialized
        self.fields['ethnicity_values'].widget.attrs['disabled'] = True
        self.fields['ethnicity_values'].widget = forms.HiddenInput()
        self.fields['gender_values'].initial = ethnicity_values_serialized
        self.fields['gender_values'].widget.attrs['disabled'] = True
        self.fields['gender_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        gender_values = pickle.loads(gender_values_serialized)
        ethnicity_values = pickle.loads(ethnicity_values_serialized)
        division_cols = FieldsDivisionCols.objects.filter(user_session_key=user_session_key).order_by("-id")[:1][0]
        gender_col = division_cols.gender_col
        ethnicity_col = division_cols.ethnicity_col
        #age_col = division_cols.age_col
        #if age_col == "":
        #    self.fields['age'].required = False
        if gender_col != "":
            gender_col_choices = []
            for value in gender_values:
                if not isnan(value):
                    gender_col_choices.append([value, value])
            self.fields['gender'].widget = forms.Select(choices=gender_col_choices, attrs={'class': "form-control"})
        else:
            self.fields['gender'].widget = forms.TextInput()
            self.fields['gender'].required = False
        if ethnicity_col != "":
            ethnicity_col_choices = []
            for value in ethnicity_values:
                if not isnan(value):
                    ethnicity_col_choices.append([value, value])
            self.fields['ethnicity'].widget = forms.Select(choices=ethnicity_col_choices, attrs={'class': "form-control"})
        else:
            self.fields['ethnicity'].widget = forms.TextInput()
            self.fields['ethnicity'].required = False

    class Meta:
        model = FieldsPatientInfo
        fields = [
            'patient_id',
            'age',
            'gender',
            'ethnicity',
            'user_session_key',
            'gender_values',
            'ethnicity_values'
        ]


class FieldsPatientNumParamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsPatientNumParamForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['name'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['value'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['norm'].required = False

    class Meta:
        model = FieldsPatientNumParam
        fields = [
            'name',
            'value',
            'norm',
            'data_columns',
            'user_session_key'
        ]


class FieldsPatientDenParamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsPatientDenParamForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['name'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['value'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['norm'].required = False

    class Meta:
        model = FieldsPatientDenParam
        fields = [
            'name',
            'value',
            'norm',
            'data_columns',
            'user_session_key'
        ]


class FieldsAgeIntervalBordersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsAgeIntervalBordersForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()

    class Meta:
        model = FieldsAgeIntervalBorders
        fields = [
            'lower_border_value',
            'upper_border_value',
            'user_session_key'
        ]


class FieldsDivideByEthnicityDefaultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FieldsDivideByEthnicityDefaultForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = [[1, "Да"],
                       [2, "Нет"]]
        self.fields['divide_by_ethnicity'].widget = forms.RadioSelect(choices=col_choices,
                                                                    attrs={'class': "form-control"})

    class Meta:
        model = FieldsDivideByEthnicityDefault
        fields = [
            'divide_by_ethnicity',
            'user_session_key',
        ]


class FieldsPatientDefaultForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):

        ethnicity_values_serialized = kwargs.pop('ethnicity_values')

        user_session_key = kwargs.pop('user_session_key')
        super(FieldsPatientDefaultForm, self).__init__(*args, **kwargs)
        self.fields['ethnicity_values'].initial = ethnicity_values_serialized
        self.fields['ethnicity_values'].widget.attrs['disabled'] = True
        self.fields['ethnicity_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        ethnicity_values = pickle.loads(ethnicity_values_serialized)
        divide_by_ethnicity = FieldsDivideByEthnicityDefault.objects.filter(user_session_key=user_session_key).order_by("-id")[:1][0].divide_by_ethnicity

        if divide_by_ethnicity == 1:
            ethnicity_col_choices = []
            for value in ethnicity_values:
                if not isnan(value):
                    ethnicity_col_choices.append([value, value])
            self.fields['ethnicity'].widget = forms.Select(choices=ethnicity_col_choices, attrs={'class': "form-control"})
        elif divide_by_ethnicity == 2:
            self.fields['ethnicity'].widget = forms.TextInput()
            self.fields['ethnicity'].required = False

        self.fields['dk'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['kd_st'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['mda'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['cod'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['gsh'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['e'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})
        self.fields['a'].widget = forms.NumberInput(attrs={'step': 0.01, 'min': 0, 'max': 30})

    class Meta:
        model = FieldsPatientDefault
        fields = [
            'patient_id',
            'age',
            'ethnicity',
            'dk',
            'kd_st',
            'mda',
            'cod',
            'gsh',
            'e',
            'a',
            'user_session_key',
            'ethnicity_values'
        ]

#file forms
class FileDataForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FileDataForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()

    class Meta:
        model = FileData
        fields = [
            'data_file',
            'numerator_params_quantity',
            'denominator_params_quantity',
            'divide_by_age',
            'divide_by_gender',
            'divide_by_ethnicity',
            'user_session_key',
        ]


class FileIdColForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FileIdColForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['id_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})


    class Meta:
        model = FileIdCol
        fields = [
            'id_col',
            'data_columns',
            'user_session_key',
        ]


class FileNumeratorParamColForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FileNumeratorParamColForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['num_param_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileNumeratorParamCol
        fields = [
            'num_param_col',
            'data_columns',
            'user_session_key',
        ]


class FileDenominatorParamColForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FileDenominatorParamColForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['den_param_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileDenominatorParamCol
        fields = [
            'den_param_col',
            'data_columns',
            'user_session_key',
        ]


class FileDivisionColsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FileDivisionColsForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        data = FileData.objects.filter(user_session_key=user_session_key).order_by("-id")[:1][0]
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['age_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['gender_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['ethnicity_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        if not data.divide_by_age:
            self.fields['age_col'].widget.attrs['disabled'] = True
            #self.fields['age_col'].widget = forms.HiddenInput()
            self.fields['age_col'].required = False
        if not data.divide_by_gender:
            self.fields['gender_col'].widget.attrs['disabled'] = True
            #self.fields['gender_col'].widget = forms.HiddenInput()
            self.fields['gender_col'].required = False
        if not data.divide_by_ethnicity:
            self.fields['ethnicity_col'].widget.attrs['disabled'] = True
            #self.fields['ethnicity_col'].widget = forms.HiddenInput()
            self.fields['ethnicity_col'].required = False


    class Meta:
        model = FileDivisionCols
        fields = [
            'age_col',
            'gender_col',
            'ethnicity_col',
            'data_columns',
            'user_session_key',
        ]


class FileGenderValuesQuantityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FileGenderValuesQuantityForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = [[1, 1], [2, 2]]
        self.fields['gender_values_quantity'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
    class Meta:
        model = FileGenderValuesQuantity
        fields = [
            'gender_values_quantity',
            'user_session_key',
        ]


class FileGenderValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        gender_values_serialized = kwargs.pop('gender_values')
        user_session_key = kwargs.pop('user_session_key')
        super(FileGenderValueForm, self).__init__(*args, **kwargs)
        self.fields['gender_values'].initial = gender_values_serialized
        self.fields['gender_values'].widget.attrs['disabled'] = True
        self.fields['gender_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        gender_values = pickle.loads(gender_values_serialized)
        col_choices = []
        for value in gender_values:
            if not isnan(value):
                col_choices.append([value, value])
        self.fields['gender_value'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})


    class Meta:
        model = FileGenderValue
        fields = [
            'gender_value',
            'user_session_key',
            'gender_values'
        ]


class FileEthnicityValuesQuantityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        unique_values_quantity = kwargs.pop('unique_values_quantity')
        user_session_key = kwargs.pop('user_session_key')
        super(FileEthnicityValuesQuantityForm, self).__init__(*args, **kwargs)
        self.fields['unique_values_quantity'].initial = unique_values_quantity
        self.fields['unique_values_quantity'].widget.attrs['disabled'] = True
        self.fields['unique_values_quantity'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        for value in range(1, unique_values_quantity + 1):
            col_choices.append([value, value])
        self.fields['ethnicity_values_quantity'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileEthnicityValuesQuantity
        fields = [
            'ethnicity_values_quantity',
            'user_session_key',
            'unique_values_quantity'
        ]


class FileEthnicityValueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        ethnicity_values_serialized = kwargs.pop('ethnicity_values')
        user_session_key = kwargs.pop('user_session_key')
        super(FileEthnicityValueForm, self).__init__(*args, **kwargs)
        self.fields['ethnicity_values'].initial = ethnicity_values_serialized
        self.fields['ethnicity_values'].widget.attrs['disabled'] = True
        self.fields['ethnicity_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        ethnicity_values = pickle.loads(ethnicity_values_serialized)
        col_choices = []
        for value in ethnicity_values:
            if not isnan(value):
                col_choices.append([value, value])
        self.fields['ethnicity_value'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileEthnicityValue
        fields = [
            'ethnicity_value',
            'user_session_key',
            'ethnicity_values'
        ]


class FileAgeIntervalsQuantityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FileAgeIntervalsQuantityForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()

        self.fields['intervals_quantity'].widget = forms.NumberInput(attrs={'min': 0, 'max': 5})

    class Meta:
        model = FileAgeIntervalsQuantity
        fields = [
            'intervals_quantity',
            'user_session_key',
        ]


class FileAgeIntervalBordersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_session_key = kwargs.pop('user_session_key')
        super(FileAgeIntervalBordersForm, self).__init__(*args, **kwargs)
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()

    class Meta:
        model = FileAgeIntervalBorders
        fields = [
            'lower_border_value',
            'upper_border_value',
            'user_session_key',
        ]


class FileSelectionColForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        data_columns = kwargs.pop('data_columns')
        user_session_key = kwargs.pop('user_session_key')
        super(FileSelectionColForm, self).__init__(*args, **kwargs)
        self.fields['data_columns'].initial = data_columns
        self.fields['data_columns'].widget.attrs['disabled'] = True
        self.fields['data_columns'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        col_choices = []
        columns = pickle.loads(data_columns)
        for col in columns:
            col_choices.append([col, col])
        self.fields['selection_col'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileSelectionCol
        fields = [
            'selection_col',
            'data_columns',
            'user_session_key',
        ]


class FileSelectionColValuesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        selection_col_values_serialized = kwargs.pop('selection_col_values')
        user_session_key = kwargs.pop('user_session_key')
        super(FileSelectionColValuesForm, self).__init__(*args, **kwargs)
        self.fields['selection_col_values'].initial = selection_col_values_serialized
        self.fields['selection_col_values'].widget.attrs['disabled'] = True
        self.fields['selection_col_values'].widget = forms.HiddenInput()
        self.fields['user_session_key'].initial = user_session_key
        self.fields['user_session_key'].widget.attrs['disabled'] = True
        self.fields['user_session_key'].widget = forms.HiddenInput()
        selection_col_values = pickle.loads(selection_col_values_serialized)
        col_choices = []
        for value in selection_col_values:
            if not isnan(value):
                col_choices.append([value, value])
        self.fields['control_selection_value'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})
        self.fields['case_selection_value'].widget = forms.Select(choices=col_choices, attrs={'class': "form-control"})

    class Meta:
        model = FileSelectionColValues
        fields = [
            'control_selection_value',
            'case_selection_value',
            'user_session_key',
            'selection_col_values'
        ]