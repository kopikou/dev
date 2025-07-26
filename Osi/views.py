import shutil
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import formset_factory
from django.conf import settings
from shutil import make_archive, rmtree
from functools import wraps, partial
import os
import pathlib
import re
import pickle
from math import isnan
from .forms import FieldsModeForm, FieldsDataForm, FieldsSelectionColForm, FieldsSelectionColValueForm, \
    FieldsDivisionColsForm, FieldsPatientInfoForm, FieldsPatientNumParamForm, FieldsPatientDenParamForm, \
    FieldsAgeIntervalBordersForm, FieldsDivideByEthnicityDefaultForm, FieldsPatientDefaultForm

from .models import FieldsMode, FieldsData, FieldsSelectionCol, FieldsSelectionColValue, FieldsDivisionCols,\
    FieldsPatientInfo, FieldsPatientNumParam, FieldsPatientDenParam, FieldsAgeIntervalBorders,\
    FieldsDivideByEthnicityDefault, FieldsPatientDefault, FieldsPatientResultExcelFile, FieldsPatientTable,\
    FieldsExcelFileDefault

from .forms import FileDataForm, FileIdColForm, FileNumeratorParamColForm, FileDenominatorParamColForm,\
    FileDivisionColsForm, FileAgeIntervalsQuantityForm, FileAgeIntervalBordersForm, FileGenderValueForm,\
    FileGenderValuesQuantityForm, FileEthnicityValuesQuantityForm, FileEthnicityValueForm, FileSelectionColForm,\
    FileSelectionColValuesForm

from .models import FileData, FileIdCol, FileNumeratorParamCol, FileDenominatorParamCol, FileDivisionCols,\
    FileAgeIntervalsQuantity, FileAgeIntervalBorders, FileGenderValuesQuantity, FileGenderValue,\
    FileEthnicityValuesQuantity, FileEthnicityValue, FileSelectionCol, FileSelectionColValues, FileOsiResultsArchive,\
    FileOsiResultsFile

import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.tree import DecisionTreeRegressor
import datetime
from django.template import RequestContext
from functools import wraps, partial
from django.template.loader import render_to_string, get_template
#from weasyprint import HTML
import tempfile
try:
    from weasyprint import HTML
except:
    HTML = None
    print("WeasyPrint не загружен, PDF функции недоступны")

#instruction view
def instruction_view(request):
    context = {'123':'123'}

    return render(request, "Osi/instruction_osi/instruction.html", context)


#fields views
def fields_error_view(request):
    context = {}

    return render(request, "Osi/fields_osi/error.html", context)


def fields_mode_view(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_key = request.session.session_key
    if request.method == 'POST':
        form = FieldsModeForm(request.POST, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_mode"}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_redirect')
    else:
        form = FieldsModeForm(user_session_key=session_key)
    context = {'form': form}

    return render(request, "Osi/fields_osi/mode.html", context)


def fields_redirect_view(request):
    session_key = request.session.session_key
    mode = FieldsMode.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].mode
    if mode == 1:
        return HttpResponseRedirect('fields_data')
    elif mode == 2:
        return HttpResponseRedirect('fields_divide_by_ethnicity_default')
    return render(request, "Osi/fields_osi/redirect.html", context={})


def fields_data_view(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        form = FieldsDataForm(request.POST, request.FILES, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_data"}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_selection_col')
    else:
        form = FieldsDataForm(user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/fields_osi/data.html", context)


def fields_selection_col_view(request):
    session_key = request.session.session_key
    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    print(columns)
    columns_serialized = pickle.dumps(columns)
    if request.method == 'POST':
        form = FieldsSelectionColForm(request.POST, data_columns=columns_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_selection_col"}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_selection_col_value')
    else:
        form = FieldsSelectionColForm(data_columns=columns_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/fields_osi/selection_col.html", context)

def fields_selection_col_value_view(request):
    session_key = request.session.session_key

    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    selection_col = FieldsSelectionCol.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].selection_col
    selection_col_values = get_column_unique_values(request, data.data_file, selection_col)
    if not len(selection_col_values) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    selection_col_values_serialized = pickle.dumps(selection_col_values)

    if request.method == 'POST':
        form = FieldsSelectionColValueForm(request.POST, selection_col_values=selection_col_values_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_selection_col_value"}
            return render(request, "Osi/fields_osi/error.html", context)
        if data.divide_by_age or data.divide_by_gender or data.divide_by_ethnicity:
            return HttpResponseRedirect('fields_division_cols')
        else:
            return HttpResponseRedirect('fields_patient_info')
    else:
        form = FieldsSelectionColValueForm(selection_col_values=selection_col_values_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/fields_osi/selection_col_value.html", context)

def fields_division_cols_view(request):
    session_key = request.session.session_key

    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    columns_serialized = pickle.dumps(columns)

    if request.method == 'POST':
        form = FieldsDivisionColsForm(request.POST, data_columns=columns_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_division_cols"}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_patient_info')
    else:
        form = FieldsDivisionColsForm(data_columns=columns_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/fields_osi/division_cols.html", context)


def fields_patient_info_view(request):

    session_key = request.session.session_key

    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    gender_col = FieldsDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].gender_col
    if gender_col != '':
        gender_values = get_column_unique_values(request, data.data_file, gender_col)
        if not len(gender_values) > 0:
            return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                          "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                                 "href": "fields_data"})
    else:
        gender_values = []
    gender_values_serialized = pickle.dumps(gender_values)

    ethnicity_col = FieldsDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_col
    if ethnicity_col != '':
        ethnicity_values = get_column_unique_values(request, data.data_file, ethnicity_col)
        if not len(ethnicity_values) > 0:
            return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                          "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                                 "href": "fields_data"})

    else:
        ethnicity_values = []
    ethnicity_values_serialized = pickle.dumps(ethnicity_values)
    if request.method == 'POST':
        info_form = FieldsPatientInfoForm(request.POST, gender_values=gender_values_serialized,
                               ethnicity_values=ethnicity_values_serialized, user_session_key=session_key)

        if info_form.is_valid():
            info_form.save()
        else:
            print(info_form.errors)
            context = {
                'error': info_form.errors,
                'href': 'fields_patient_info'}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_patient_num_params')
    else:
        info_form = FieldsPatientInfoForm(gender_values=gender_values_serialized,
                               ethnicity_values=ethnicity_values_serialized, user_session_key=session_key)
    context = {
        'info_form': info_form,
    }
    return render(request, "Osi/fields_osi/patient_info.html", context)

def fields_patient_num_params_view(request):
    session_key = request.session.session_key

    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    columns_serialized = pickle.dumps(columns)

    num_params_quantity = data.numerator_params_quantity

    PatientNumParamFormSet = formset_factory(wraps(FieldsPatientNumParamForm)(partial(FieldsPatientNumParamForm,
                                                                                data_columns=columns_serialized,
                                                                                user_session_key=session_key)),
                                                                                extra=num_params_quantity)

    if request.method == 'POST':
        num_param_formset = PatientNumParamFormSet(request.POST)

        if num_param_formset.is_valid():
            for num_param_form in num_param_formset:
                num_param_form.save()
        else:
            print(num_param_formset.errors)
            context = {
                'error': num_param_formset.errors,
                'href': 'fields_patient_num_params'}
            return render(request, "Osi/fields_osi/error.html", context)

        return HttpResponseRedirect('fields_patient_den_params')
    else:
        num_param_formset = PatientNumParamFormSet()
    context = {
        'num_param_formset': num_param_formset,
    }
    return render(request, "Osi/fields_osi/patient_num_params.html", context)


def fields_patient_den_params_view(request):
    session_key = request.session.session_key

    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    columns_serialized = pickle.dumps(columns)

    den_params_quantity = data.denominator_params_quantity

    PatientDenParamFormSet = formset_factory(wraps(FieldsPatientDenParamForm)(partial(FieldsPatientDenParamForm,
                                                                                data_columns=columns_serialized,
                                                                                user_session_key=session_key)),
                                                                                extra=den_params_quantity)

    if request.method == 'POST':
        den_param_formset = PatientDenParamFormSet(request.POST)

        if den_param_formset.is_valid():
            for den_param_form in den_param_formset:
                den_param_form.save()
        else:
            print(den_param_formset.errors)
            context = {
                'error': den_param_formset.errors,
                'href': 'fields_patient_den_params'}
            return render(request, "Osi/fields_osi/error.html", context)
        if data.divide_by_age:
            return HttpResponseRedirect('fields_age_interval_borders')
        else:
            return fields_get_results(request, session_key)
    else:
        den_param_formset = PatientDenParamFormSet()
    context = {
        'den_param_formset': den_param_formset,
    }
    return render(request, "Osi/fields_osi/patient_den_params.html", context)


def fields_age_interval_borders_view(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        form = FieldsAgeIntervalBordersForm(request.POST, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_age_interval_borders"}
            return render(request, "Osi/fields_osi/error.html", context)
        return fields_get_results(request, session_key)
    else:
        form = FieldsAgeIntervalBordersForm(user_session_key=session_key)
    context = {'form': form}

    return render(request, "Osi/fields_osi/age_interval_borders.html", context)


def fields_results_view(request):
    session_key = request.session.session_key
    patient_html_table = FieldsPatientTable.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].patient_table
    result_excel_file = FieldsPatientResultExcelFile.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].result_excel_file

    context = {
        'patient_html_table':  patient_html_table,
        'result_excel_file': result_excel_file
    }
    return render(request, "Osi/fields_osi/results.html", context)


#fields views (режим по умолчанию)

def fields_divide_by_ethnicity_default_view(request):
    session_key = request.session.session_key
    if request.method == 'POST':
        form = FieldsDivideByEthnicityDefaultForm(request.POST, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "fields_divide_by_ethnicity_default"}
            return render(request, "Osi/fields_osi/error.html", context)
        return HttpResponseRedirect('fields_patient_default')
    else:
        form = FieldsDivideByEthnicityDefaultForm(user_session_key=session_key)
    context = {'form': form}

    return render(request, "Osi/fields_osi/divide_by_ethnicity_default.html", context)


def fields_patient_default_view(request):

    session_key = request.session.session_key

    excel_file_default = FieldsExcelFileDefault.objects.all().order_by("-id")[:1][0].excel_file_default

    ethnicity_values = get_column_unique_values(request, excel_file_default, ETHNICITY_COL_NAME_DEFAULT)
    if not len(ethnicity_values) > 0:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "fields_data"})
    ethnicity_values_serialized = pickle.dumps(ethnicity_values)

    if request.method == 'POST':
        form = FieldsPatientDefaultForm(request.POST, ethnicity_values=ethnicity_values_serialized,
                                  user_session_key=session_key)

        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {
                'error': form.errors,
                'href': 'fields_patient_default'}
            return render(request, "Osi/fields_osi/error.html", context)
        return fields_get_results_default(request, session_key)
    else:
        form = FieldsPatientDefaultForm(ethnicity_values=ethnicity_values_serialized, user_session_key=session_key)
    context = {
        'form': form,
    }
    return render(request, "Osi/fields_osi/patient_default.html", context)


def fields_get_results(request, session_key):

    # определение данных
    data = FieldsData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    data_file = data.data_file
    num_params_quantity = data.numerator_params_quantity
    den_params_quantity = data.denominator_params_quantity

    num_params_data = FieldsPatientNumParam.objects.filter(user_session_key=session_key).order_by("-id")[
                              :num_params_quantity]
    num_params_data = num_params_data[::-1]
    den_params_data = FieldsPatientDenParam.objects.filter(user_session_key=session_key).order_by("-id")[
                      :den_params_quantity]
    den_params_data = den_params_data[::-1]

    divide_by_age = data.divide_by_age
    divide_by_gender = data.divide_by_gender
    divide_by_ethnicity = data.divide_by_ethnicity

    patient = FieldsPatientInfo.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    patient_num_params_dict = {}
    patient_num_params_norms_dict = {}
    for num_param in num_params_data:
        patient_num_params_dict[num_param.name] = num_param.value
        patient_num_params_norms_dict[num_param.name] = num_param.norm

    patient_den_params_dict = {}
    patient_den_params_norms_dict = {}
    for den_param in den_params_data:
        patient_den_params_dict[den_param.name] = den_param.value
        patient_den_params_norms_dict[den_param.name] = den_param.norm

    try:
        data_file_suffix = pathlib.Path(data_file.name).suffix
        if data_file_suffix == '.csv':
            data = pd.read_csv(data_file, sep=';', on_bad_lines='skip')
        elif data_file_suffix == '.xls':
            data = pd.read_excel(data_file, sheet_name=0, index_col=None)
    except BaseException:
        return render(request, "Osi/fields_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                       "href": "fields_data"})

    params_cols = []
    params_cols += patient_num_params_dict.keys()
    params_cols += patient_den_params_dict.keys()

    cols = []
    cols += patient_num_params_dict.keys()
    cols += patient_den_params_dict.keys()


    if divide_by_age:
        age_col = FieldsDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].age_col
        cols.append(age_col)
    if divide_by_gender:
        gender_col = FieldsDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].gender_col
        cols.append(gender_col)
    if divide_by_ethnicity:
        ethnicity_col = FieldsDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_col
        cols.append(ethnicity_col)
    print(cols)


    selection_col = FieldsSelectionCol.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].selection_col
    control_selection_value = FieldsSelectionColValue.objects.filter(user_session_key=session_key).order_by("-id")[:1][
        0].control_selection_value

    # проверка уникальности выбранных столбцов
    cols_check = cols + [selection_col]
    print(cols_check)
    if len(set(cols_check)) != len(cols_check):
        return render(request, "Osi/fields_osi/error.html", {"error": "При выборе столбцов не должно быть повторений.",
                                                       "href": "fields_data"})


    control_data = data[data[selection_col].astype(str) == control_selection_value]
    control_df = control_data[cols]

    # преобразование строковых значений с запятой (полученных из Excel) в числа типа float
    for col in cols:
        if isinstance(control_df.dropna()[col].iloc[0], str) and re.fullmatch(r'\d+,\d+',
                                                                              control_df.dropna()[col].iloc[0]):
            control_df[col] = control_df[col].str.replace(',', '.').apply(float)

    # обработка данных
    print(cols)
    print(control_df.describe())
    print("--------------")
    imp = IterativeImputer(estimator=DecisionTreeRegressor())
    control_df = imp.fit_transform(control_df)
    control_df = pd.DataFrame(control_df, columns=cols)
    control_df = round(control_df, 2)
    print(control_df.describe())
    print("--------------")

    if divide_by_age:
        lower_age_interval_border = FieldsAgeIntervalBorders.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].lower_border_value
        upper_age_interval_border = FieldsAgeIntervalBorders.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].upper_border_value

        if upper_age_interval_border < lower_age_interval_border:
            return render(request, "Osi/fields_osi/error.html",
                          {"error": "Заполняйте граничные значения возрастных промежутков в порядке возрастания.",
                           "href": "fields_age_interval_borders"})

        if patient.age < lower_age_interval_border or patient.age >= upper_age_interval_border:
            return render(request, "Osi/fields_osi/error.html",
                          {"error": "Заданный промежуток должен включать возраст пациента.",
                           "href": "fields_age_interval_borders"})



    print(control_df)

    def indicators_check(params, params_cols_names):
        indicators = ""
        for i in range(len(params)):
            if params[i] > np.percentile(control_df[params_cols_names[i]], 97.5) or params[i] < np.percentile(control_df[params_cols_names[i]], 2.5):
                indicators = "del"
        return indicators

    indicators = control_df.apply(lambda row: indicators_check(row[params_cols], params_cols), axis=1)
    if not indicators.empty:
        control_df['indicators'] = indicators
        control_df = control_df[control_df['indicators'] == ""]
        control_df.drop(['indicators'], axis=1, inplace=True)

    print(control_df.describe())

    if divide_by_age:
        control_df = control_df[(control_df[age_col] >= lower_age_interval_border)
                                & (control_df[age_col] < upper_age_interval_border)]

    if divide_by_gender:
        control_df = control_df[control_df[gender_col].astype(str) == patient.gender]

    if divide_by_ethnicity:
        control_df = control_df[control_df[ethnicity_col].astype(str) == patient.ethnicity]


    MIN_CONTROL_DF_ROWS_NUM = 20  # 120
    if len(control_df.index) < MIN_CONTROL_DF_ROWS_NUM:
        control_df_message = "Контрольная выборка должна содержать не менее %d записей. Сформированная контрольная" \
                              " выборка содержит %d записей." % (MIN_CONTROL_DF_ROWS_NUM, len(control_df.index))
        return render(request, "Osi/fields_osi/error.html",
                      {"error": control_df_message,
                       "href": "fields_data"})

    numerator = 1
    denominator = 1
    for param in patient_num_params_dict:
        numerator *= patient_num_params_dict[param] / control_df[param].median()
    for param in patient_den_params_dict:
        denominator *= patient_den_params_dict[param] / control_df[param].median()
    osi = round(numerator / denominator, 2)
    print(osi)


    patient_html_table = '<table class="results_table">'
    patient_html_table += '<tr><td>Уникальный идентификатор</td><td colspan="2">%d</td></tr>' \
                         '<tr><td>Возраст</td><td colspan="2">%d</td></tr>' \
                         '<tr><td>Пол</td><td colspan="2">%s</td></tr>' \
                         '<tr><td>Раса</td><td colspan="2">%s</td></tr>' \
                         '<tr><th>Показатель</th><th>Результат</th><th>Норма</th></tr>' %\
                         (patient.patient_id, patient.age, patient.gender, patient.ethnicity)
    for param in patient_num_params_dict:
        patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>%s</td></tr>' % (param, patient_num_params_dict[param],
                                                                     patient_num_params_norms_dict[param])
    for param in patient_den_params_dict:
        patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>%s</td></tr>' % (param, patient_den_params_dict[param],
                                                                     patient_den_params_norms_dict[param])
    patient_html_table += '<tr><td><b>Коэффициент окислительного стресса</b></td><td colspan="2"><b>%.2f</b></td></tr>' % (osi)

    patient_html_table += '</table>'


    FieldsPatientTable.objects.create(
        patient_table=patient_html_table,
        user_session_key=session_key
    )

    patient_df = pd.DataFrame(columns=['param', 'val'])
    patient_df.loc[len(patient_df.index)] = ['Уникальный идентификатор', patient.patient_id]
    patient_df.loc[len(patient_df.index)] = ['Возраст', patient.age]
    patient_df.loc[len(patient_df.index)] = ['Пол', patient.gender]
    patient_df.loc[len(patient_df.index)] = ['Раса', patient.ethnicity]
    for param in patient_num_params_dict:
        patient_df.loc[len(patient_df.index)] = [param, patient_num_params_dict[param]]
    for param in patient_den_params_dict:
        patient_df.loc[len(patient_df.index)] = [param, patient_den_params_dict[param]]
    patient_df.loc[len(patient_df.index)] = ['Коэффициент окислительного стресса', osi]
    print(patient_df)

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key)
    if os.path.exists(path_to_delete):
        rmtree(path_to_delete)
    FieldsPatientResultExcelFile.objects.all().filter(user_session_key=session_key).delete()
    path = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key)
    if not os.path.exists(path):
        os.makedirs(path)
    output_file = os.path.join(path, 'patient.xls')
    patient_df.to_excel(output_file, header=False, index=False)

    FieldsPatientResultExcelFile.objects.create(
        result_excel_file=os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key, 'patient.xls'),
        user_session_key=session_key
    )

    return HttpResponseRedirect('fields_results')


ETHNICITY_COL_NAME_DEFAULT = 'ethnicity'
DK_COL_NAME_DEFAULT = 'value_test2_bioch_DK'
KD_ST_COL_NAME_DEFAULT = 'value_kd_ct'
MDA_COL_NAME_DEFAULT = 'value_test3_bioch_MDA'
COD_COL_NAME_DEFAULT = 'value_test6_bioch_COD'
GSH_COL_NAME_DEFAULT = 'value_test8_bioch_GSH'
E_COL_NAME_DEFAULT = 'value_test11_bioch_vitE'
A_COL_NAME_DEFAULT = 'value_test10_bioch_vitA'
SELECTION_COL_NAME_DEFAULT = 'supercontrol'
SELECTION_COL_CONTROL_VALUE_DEFAULT = 1


def fields_get_results_default(request, session_key):
    excel_file_default = FieldsExcelFileDefault.objects.all().order_by("-id")[:1][0].excel_file_default

    patient_default = FieldsPatientDefault.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    divide_by_ethnicity = FieldsDivideByEthnicityDefault.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].divide_by_ethnicity

    data = pd.read_excel(excel_file_default, sheet_name=0, index_col=None)

    cols = []

    if divide_by_ethnicity == 1:
        cols.append(ETHNICITY_COL_NAME_DEFAULT)

    num_params_cols = [DK_COL_NAME_DEFAULT, KD_ST_COL_NAME_DEFAULT, MDA_COL_NAME_DEFAULT]
    den_params_cols = [COD_COL_NAME_DEFAULT, GSH_COL_NAME_DEFAULT, E_COL_NAME_DEFAULT, A_COL_NAME_DEFAULT]

    params_cols = num_params_cols + den_params_cols

    cols += params_cols

    control_data = data[data[SELECTION_COL_NAME_DEFAULT] == float(SELECTION_COL_CONTROL_VALUE_DEFAULT)]
    control_df = control_data[cols]

    # преобразование строковых значений с запятой (полученных из Excel) в числа типа float
    for col in cols:
        if isinstance(control_df.dropna()[col].iloc[0], str) and re.fullmatch(r'\d+,\d+',
                                                                              control_df.dropna()[col].iloc[0]):
            control_df[col] = control_df[col].str.replace(',', '.').apply(float)

    # обработка данных
    print(cols)
    print(control_df.describe())
    print("--------------")
    imp = IterativeImputer(estimator=DecisionTreeRegressor())
    control_df = imp.fit_transform(control_df)
    control_df = pd.DataFrame(control_df, columns=cols)
    control_df = round(control_df, 2)
    print(control_df.describe())
    print("--------------")

    print(control_df)

    def indicators_check(params, params_cols_names):
        indicators = ""
        for i in range(len(params)):
            if params[i] > np.percentile(control_df[params_cols_names[i]], 97.5) or params[i] < np.percentile(
                    control_df[params_cols_names[i]], 2.5):
                indicators = "del"
        return indicators

    indicators = control_df.apply(lambda row: indicators_check(row[params_cols], params_cols), axis=1)
    if not indicators.empty:
        control_df['indicators'] = indicators
        control_df = control_df[control_df['indicators'] == ""]
        control_df.drop(['indicators'], axis=1, inplace=True)

    print(control_df.describe())

    if divide_by_ethnicity == 1:
        control_df = control_df[control_df[ETHNICITY_COL_NAME_DEFAULT].astype(str) == patient_default.ethnicity]

    MIN_CONTROL_DF_ROWS_NUM = 20  # 120
    if len(control_df.index) < MIN_CONTROL_DF_ROWS_NUM:
        control_df_message = "Контрольная выборка должна содержать не менее %d записей. Сформированная контрольная" \
                             " выборка содержит %d записей." % (MIN_CONTROL_DF_ROWS_NUM, len(control_df.index))
        return render(request, "Osi/fields_osi/error.html",
                      {"error": control_df_message,
                       "href": "fields_data"})

    numerator = 1
    denominator = 1
    numerator *= patient_default.dk / control_df[DK_COL_NAME_DEFAULT].median()
    numerator *= patient_default.kd_st / control_df[KD_ST_COL_NAME_DEFAULT].median()
    numerator *= patient_default.mda / control_df[MDA_COL_NAME_DEFAULT].median()

    denominator *= patient_default.cod / control_df[COD_COL_NAME_DEFAULT].median()
    denominator *= patient_default.gsh / control_df[GSH_COL_NAME_DEFAULT].median()
    denominator *= patient_default.e / control_df[E_COL_NAME_DEFAULT].median()
    denominator *= patient_default.a / control_df[A_COL_NAME_DEFAULT].median()

    osi = round(numerator / denominator, 2)
    print(osi)

    patient_html_table = '<table class="results_table">'
    patient_html_table += '<tr><td>Уникальный идентификатор</td><td colspan="2">%d</td></tr>' \
                          '<tr><td>Возраст</td><td colspan="2">%d</td></tr>' \
                          '<tr><td>Пол</td><td colspan="2">%s</td></tr>' \
                          '<tr><td>Раса</td><td colspan="2">%s</td></tr>' \
                          '<tr><th>Показатель</th><th>Результат</th><th>Норма</th></tr>' % \
                          (patient_default.patient_id, patient_default.age, 'Женский', patient_default.ethnicity)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>0.99-1.53 мкМ/л</td></tr>' % (
    'Диеновые конъюгаты', patient_default.dk)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td> </td></tr>' % (
    'Кетодиены и сопряженные триены', patient_default.kd_st)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>1.94-2.50 мкМ/л</td></tr>' % (
    'Малоновый диальдегид', patient_default.mda)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>1.52-1.80 усл.ед.</td></tr>' % (
    'Супероксиддисмутаза', patient_default.cod)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>2.50-3.20 мМ/л</td></tr>' % (
    'Глутатион восстановленный', patient_default.gsh)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>6.66-14.80 мкМ/л</td></tr>' % (
    'α токоферол vitE', patient_default.e)
    patient_html_table += '<tr><td>%s</td><td>%.2f</td><td>0.50-2.27 мкМ/л</td></tr>' % (
    'Ретинол vitA', patient_default.a)

    patient_html_table += '<tr><td><b>Коэффициент окислительного стресса</b></td><td colspan="2"><b>%.2f</b></td></tr>' % (
        osi)

    patient_html_table += '</table>'

    FieldsPatientTable.objects.create(
        patient_table=patient_html_table,
        user_session_key=session_key
    )

    patient_df = pd.DataFrame(columns=['param', 'val'])
    patient_df.loc[len(patient_df.index)] = ['Уникальный идентификатор', patient_default.patient_id]
    patient_df.loc[len(patient_df.index)] = ['Возраст', patient_default.age]
    patient_df.loc[len(patient_df.index)] = ['Пол', 'Женский']
    patient_df.loc[len(patient_df.index)] = ['Раса', patient_default.ethnicity]
    patient_df.loc[len(patient_df.index)] = ['ДК', patient_default.dk]
    patient_df.loc[len(patient_df.index)] = ['КД-СТ', patient_default.kd_st]
    patient_df.loc[len(patient_df.index)] = ['МДА', patient_default.mda]
    patient_df.loc[len(patient_df.index)] = ['СОД', patient_default.cod]
    patient_df.loc[len(patient_df.index)] = ['GSH', patient_default.gsh]
    patient_df.loc[len(patient_df.index)] = ['E', patient_default.e]
    patient_df.loc[len(patient_df.index)] = ['A', patient_default.a]
    patient_df.loc[len(patient_df.index)] = ['Коэффициент окислительного стресса', osi]
    print(patient_df)

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key)
    if os.path.exists(path_to_delete):
        rmtree(path_to_delete)
    FieldsPatientResultExcelFile.objects.all().filter(user_session_key=session_key).delete()
    path = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key)
    if not os.path.exists(path):
        os.makedirs(path)
    output_file = os.path.join(path, 'patient.xls')
    patient_df.to_excel(output_file, header=False, index=False)

    FieldsPatientResultExcelFile.objects.create(
        result_excel_file=os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files', session_key, 'patient.xls'),
        user_session_key=session_key
    )

    return HttpResponseRedirect('fields_results')


def fields_export_pdf(request):
    session_key = request.session.session_key

    patient_html_table = FieldsPatientTable.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].patient_table

    template = get_template('Osi/fields_osi/pdf_output.html')
    html = template.render({'patient_html_table': patient_html_table})
    response = HttpResponse(content_type='application/pdf')
    HTML(string=html).write_pdf(response)
    return response


#file views

def file_error_view(request):
    context = {}

    return render(request, "Osi/file_osi/error.html", context)


def file_data_view(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_key = request.session.session_key
    #ControlData.objects.all().filter(user_session_key=session_key).delete()
    if request.method == 'POST':
        form = FileDataForm(request.POST, request.FILES, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_data"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_id_col')
    else:
        form = FileDataForm(user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/data.html", context)


def file_id_col_view(request):
    session_key = request.session.session_key
    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    columns_serialized = pickle.dumps(columns)
    if request.method == 'POST':
        form = FileIdColForm(request.POST, data_columns=columns_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_id_col"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_numerator_params_cols')
    else:
        form = FileIdColForm(data_columns=columns_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/id_col.html", context)


def file_numerator_params_cols_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    columns_serialized = pickle.dumps(columns)
    quantity = data.numerator_params_quantity
    NumeratorParamColsFormSet = formset_factory(wraps(FileNumeratorParamColForm)(partial(
        FileNumeratorParamColForm, data_columns=columns_serialized, user_session_key=session_key)), extra=quantity)
    if request.method == 'POST':
        formset = NumeratorParamColsFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
        else:
            print(formset.errors)
            context = {"error": formset.errors, "href": "file_numerator_params_cols"}
            return render(request, "Osi/file_osi/error.html", context)

        return HttpResponseRedirect('file_denominator_params_cols')
    else:
        formset = NumeratorParamColsFormSet()
    context = {'formset': formset}
    return render(request, "Osi/file_osi/numerator_params_cols.html", context)


def file_denominator_params_cols_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    columns_serialized = pickle.dumps(columns)
    quantity = data.denominator_params_quantity
    DenominatorParamColsFormSet = formset_factory(wraps(FileDenominatorParamColForm)(partial(
        FileDenominatorParamColForm, data_columns=columns_serialized, user_session_key=session_key)), extra=quantity)
    if request.method == 'POST':
        formset = DenominatorParamColsFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
        else:
            print(formset.errors)
            context = {"error": formset.errors, "href": "file_denominator_params_cols"}
            return render(request, "Osi/file_osi/error.html", context)
        if data.divide_by_age or data.divide_by_gender or data.divide_by_ethnicity:
            return HttpResponseRedirect('file_division_cols')
        else:
            return HttpResponseRedirect('file_selection_col')
    else:
        formset = DenominatorParamColsFormSet()
    context = {'formset': formset}
    return render(request, "Osi/file_osi/denominator_params_cols.html", context)


def file_division_cols_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    columns_serialized = pickle.dumps(columns)

    if request.method == 'POST':
        form = FileDivisionColsForm(request.POST, data_columns=columns_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_division_cols"}
            return render(request, "Osi/file_osi/error.html", context)
        if data.divide_by_gender:
            return HttpResponseRedirect('file_gender_values_quantity')
        elif data.divide_by_ethnicity:
            return HttpResponseRedirect('file_ethnicity_values_quantity')
        elif data.divide_by_age:
            return HttpResponseRedirect('file_age_intervals_quantity')
        else:
            return HttpResponseRedirect('file_selection_col')
    else:
        form = FileDivisionColsForm(data_columns=columns_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/division_cols.html", context)


def file_gender_values_quantity_view(request):
    session_key = request.session.session_key

    if request.method == 'POST':
        form = FileGenderValuesQuantityForm(request.POST, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_gender_values_quantity"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_gender_values')
    else:
        form = FileGenderValuesQuantityForm(user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/gender_values_quantity.html", context)


def file_gender_values_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    gender_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].gender_col
    gender_values = get_column_unique_values(request, data.data_file, gender_col)
    if not len(gender_values) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    gender_values_serialized = pickle.dumps(gender_values)
    quantity = FileGenderValuesQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].gender_values_quantity

    GenderValuesFormSet = formset_factory(wraps(FileGenderValueForm)(partial(
        FileGenderValueForm, gender_values=gender_values_serialized, user_session_key=session_key)), extra=quantity)

    if request.method == 'POST':
        formset = GenderValuesFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
        else:
            print(formset.errors)
            context = {"error": formset.errors, "href": "file_gender_values"}
            return render(request, "Osi/file_osi/error.html", context)
        if data.divide_by_ethnicity:
            return HttpResponseRedirect('file_ethnicity_values_quantity')
        elif data.divide_by_age:
            return HttpResponseRedirect('file_age_intervals_quantity')
        else:
            return HttpResponseRedirect('file_selection_col')
    else:
        formset = GenderValuesFormSet()
    context = {'formset': formset}
    return render(request, "Osi/file_osi/gender_values.html", context)


def file_ethnicity_values_quantity_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    ethnicity_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_col
    unique_values = get_column_unique_values(request, data.data_file, ethnicity_col)
    if not len(unique_values) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    unique_values = [x for x in unique_values if not isnan(x)]
    unique_values_quantity = np.array(unique_values).size
    if request.method == 'POST':
        form = FileEthnicityValuesQuantityForm(request.POST, unique_values_quantity=unique_values_quantity, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_ethnicity_values_quantity"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_ethnicity_values')
    else:
        form = FileEthnicityValuesQuantityForm(unique_values_quantity=unique_values_quantity, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/ethnicity_values_quantity.html", context)


def file_ethnicity_values_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    ethnicity_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_col
    ethnicity_values = get_column_unique_values(request, data.data_file, ethnicity_col)
    if not len(ethnicity_values) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    ethnicity_values_serialized = pickle.dumps(ethnicity_values)
    quantity = FileEthnicityValuesQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_values_quantity

    EthnicityValuesFormSet = formset_factory(wraps(FileEthnicityValueForm)(partial(
        FileEthnicityValueForm, ethnicity_values=ethnicity_values_serialized, user_session_key=session_key)), extra=quantity)

    if request.method == 'POST':
        formset = EthnicityValuesFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
        else:
            print(formset.errors)
            context = {"error": formset.errors, "href": "file_ethnicity_values"}
            return render(request, "Osi/file_osi/error.html", context)
        if data.divide_by_age:
            return HttpResponseRedirect('file_age_intervals_quantity')
        else:
            return HttpResponseRedirect('file_selection_col')
    else:
        formset = EthnicityValuesFormSet()
    context = {'formset': formset}
    return render(request, "Osi/file_osi/ethnicity_values.html", context)


def file_age_intervals_quantity_view(request):

    session_key = request.session.session_key

    if request.method == 'POST':
        form = FileAgeIntervalsQuantityForm(request.POST, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_age_intervals_quantity"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_age_intervals_borders')
    else:
        form = FileAgeIntervalsQuantityForm(user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/age_intervals_quantity.html", context)


def file_age_intervals_borders_view(request):
    session_key = request.session.session_key

    quantity = FileAgeIntervalsQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].intervals_quantity
    FileAgeIntervalsBordersFormSet = formset_factory(wraps(FileAgeIntervalBordersForm)(partial(
        FileAgeIntervalBordersForm, user_session_key=session_key)), extra=quantity)
    if request.method == 'POST':
        formset = FileAgeIntervalsBordersFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                form.save()
        else:
            print(formset.errors)
            context = {"error": formset.errors, "href": "file_age_intervals_borders"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_selection_col')
    else:
        formset = FileAgeIntervalsBordersFormSet()
    context = {'formset': formset}
    return render(request, "Osi/file_osi/age_intervals_borders.html", context)


def file_selection_col_view(request):
    session_key = request.session.session_key
    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    columns = get_file_columns(request, data.data_file)
    if not len(columns) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    columns_serialized = pickle.dumps(columns)
    if request.method == 'POST':
        form = FileSelectionColForm(request.POST, data_columns=columns_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_selection_col"}
            return render(request, "Osi/file_osi/error.html", context)
        return HttpResponseRedirect('file_selection_col_values')
    else:
        form = FileSelectionColForm(data_columns=columns_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/selection_col.html", context)


def file_selection_col_values_view(request):
    session_key = request.session.session_key

    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    selection_col = FileSelectionCol.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].selection_col
    selection_col_values = get_column_unique_values(request, data.data_file, selection_col)
    if not len(selection_col_values) > 0:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                      "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                             "href": "file_data"})
    selection_col_values_serialized = pickle.dumps(selection_col_values)

    if request.method == 'POST':
        form = FileSelectionColValuesForm(request.POST, selection_col_values=selection_col_values_serialized, user_session_key=session_key)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
            context = {"error": form.errors, "href": "file_selection_col_values"}
            return render(request, "Osi/file_osi/error.html", context)
        return file_get_results(request, session_key)

    else:
        form = FileSelectionColValuesForm(selection_col_values=selection_col_values_serialized, user_session_key=session_key)
    context = {'form': form}
    return render(request, "Osi/file_osi/selection_col_values.html", context)


def file_results_view(request):
    session_key = request.session.session_key
    osi_results_archive = FileOsiResultsArchive.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]
    osi_results_files = FileOsiResultsFile.objects.filter(user_session_key=session_key).all()
    urls = []
    dfs = []
    for osi_results_file in osi_results_files:
        urls.append(osi_results_file.osi_results_file.url)
        data_file_suffix = pathlib.Path(osi_results_file.osi_results_file.name).suffix
        if data_file_suffix == '.csv':
            data = pd.read_csv(osi_results_file.osi_results_file, sep=';', on_bad_lines='skip')
            dfs.append(data)
        elif data_file_suffix == '.xls' or data_file_suffix == '.xlsx':
            data = pd.read_excel(osi_results_file.osi_results_file, sheet_name=0, index_col=None)
            dfs.append(data)
    urls_dfs = zip(urls, dfs)
    context = {'osi_results_archive': osi_results_archive, "urls_dfs": urls_dfs}
    return render(request, "Osi/file_osi/results.html", context)


def file_get_results(request, session_key):

    #определение данных
    data = FileData.objects.filter(user_session_key=session_key).order_by("-id")[:1][0]

    data_file = data.data_file
    num_params_quantity = data.numerator_params_quantity
    den_params_quantity = data.denominator_params_quantity
    num_params_cols_data = FileNumeratorParamCol.objects.filter(user_session_key=session_key).order_by("-id")[
                              :num_params_quantity]
    num_params_cols = []
    for col in num_params_cols_data:
        num_params_cols.append(col.num_param_col)
    num_params_cols.reverse()
    den_params_cols_data = FileDenominatorParamCol.objects.filter(user_session_key=session_key).order_by("-id")[
                              :den_params_quantity]
    den_params_cols = []
    for col in den_params_cols_data:
        den_params_cols.append(col.den_param_col)
    den_params_cols.reverse()
    params_cols = num_params_cols + den_params_cols

    divide_by_age = data.divide_by_age
    divide_by_gender = data.divide_by_gender
    divide_by_ethnicity = data.divide_by_ethnicity

    id_col = FileIdCol.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].id_col

    try:
        data_file_suffix = pathlib.Path(data_file.name).suffix
        if data_file_suffix == '.csv':
            data = pd.read_csv(data_file, sep=';', on_bad_lines='skip')
        elif data_file_suffix == '.xls' or data_file_suffix == '.xlsx':
            data = pd.read_excel(data_file, sheet_name=0, index_col=None)
    except BaseException:
        return render(request, "Osi/file_osi/error.html", {"error": "Проблема с загруженным файлом."
                                                                "Внимание! Доступные расширения файлов: .xls, .xlsx, .csv.",
                                                       "href": "file_data"})

    cols = []
    cols.append(id_col)
    cols += num_params_cols
    cols += den_params_cols
    if divide_by_age:
        age_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].age_col
        cols.append(age_col)
    if divide_by_gender:
        gender_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].gender_col
        cols.append(gender_col)
    if divide_by_ethnicity:
        ethnicity_col = FileDivisionCols.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].ethnicity_col
        cols.append(ethnicity_col)



    selection_col = FileSelectionCol.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].selection_col
    control_selection_value = FileSelectionColValues.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].control_selection_value
    case_selection_value = FileSelectionColValues.objects.filter(user_session_key=session_key).order_by("-id")[:1][0].case_selection_value

    # проверка уникальности выбранных столбцов
    cols_check = cols + [selection_col]
    print(cols_check)
    if (len(set(cols_check)) != len(cols_check)):
        return render(request, "Osi/file_osi/error.html", {"error": "При выборе столбцов не должно быть повторений.",
                                                       "href": "file_data"})

    control_data = data[data[selection_col] == float(control_selection_value)]
    control_df = control_data[cols]

    case_data = data[data[selection_col] == float(case_selection_value)]
    case_df = case_data[cols]

    #преобразование строковых значений с запятой (полученных из Excel) в числа типа float
    for col in cols:
        if isinstance(control_df.dropna()[col].iloc[0], str) and re.fullmatch(r'\d+,\d+', control_df.dropna()[col].iloc[0]):
            control_df[col] = control_df[col].str.replace(',', '.').apply(float)
        if isinstance(case_df.dropna()[col].iloc[0], str) and re.fullmatch(r'\d+,\d+', case_df.dropna()[col].iloc[0]):
            case_df[col] = case_df[col].str.replace(',', '.').apply(float)


    #обработка данных
    print(cols)
    print(control_df.describe())
    print("--------------")
    imp = IterativeImputer(estimator=DecisionTreeRegressor())
    control_df[cols[1:]] = imp.fit_transform(control_df[cols[1:]])
    control_df = pd.DataFrame(control_df, columns=cols)
    control_df = round(control_df, 2)
    control_df.set_index(id_col)
    print(control_df.describe())
    print("--------------")
    print(case_df.describe())
    print("--------------")
    case_df[cols[1:]] = imp.fit_transform(case_df[cols[1:]])
    case_df = pd.DataFrame(case_df, columns=cols)
    case_df = round(case_df, 2)
    case_df.set_index(id_col)
    print(case_df.describe())
    print("--------------")
    print("CONTROL")
    print(control_df)
    print("CASE")
    print(case_df)

    if divide_by_age:
        age_intervals_quantity = FileAgeIntervalsQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][
            0].intervals_quantity
        age_intervals_borders_data = FileAgeIntervalBorders.objects.filter(user_session_key=session_key).order_by("-id")[
                                     :age_intervals_quantity]
        age_intervals_borders = []
        for borders in age_intervals_borders_data:
            age_intervals_borders.append([borders.lower_border_value, borders.upper_border_value])

        #проверка возрастных промежутков на непересекаемость
        age_intervals_borders_sorted = sorted(age_intervals_borders, key = lambda x: int(x[0]))
        for borders in age_intervals_borders_sorted:
            if borders != sorted(borders):
                return render(request, "Osi/file_osi/error.html",
                              {"error": "Заполняйте граничные значения возрастных промежутков в порядке возрастания.",
                               "href": "file_age_intervals_quantity"})
        for i in range(len(age_intervals_borders_sorted) - 1):
            if age_intervals_borders_sorted[i][1] > age_intervals_borders_sorted[i + 1][0]:
                return render(request, "Osi/file_osi/error.html",
                              {"error": "Возрастные промежутки не могут пересекаться.",
                               "href": "file_age_intervals_quantity"})

        def get_age_intervals(age):
            age_interval = -1
            for i in range(len(age_intervals_borders)):
                if (age >= age_intervals_borders[i][0]) & (age < age_intervals_borders[i][1]):
                    age_interval = i + 1
            return age_interval

        control_df['age_intervals'] = control_df.apply(lambda row: get_age_intervals(row[age_col]), axis=1)
        case_df['age_intervals'] = case_df.apply(lambda row: get_age_intervals(row[age_col]), axis=1)

        control_df = control_df[control_df['age_intervals'] != -1]
        case_df = case_df[case_df['age_intervals'] != -1]



    def indicators_check(params, params_cols_names):
        indicators = ""
        for i in range(len(params)):
            if params[i] > np.percentile(control_df[params_cols_names[i]], 97.5) or params[i] < np.percentile(control_df[params_cols_names[i]], 2.5):
                indicators = "del"
        return indicators

    def find_osi(control_df, case_df):
        indicators = control_df.apply(lambda row: indicators_check(row[params_cols], params_cols), axis=1)
        if not indicators.empty:
            control_df['indicators'] = indicators
            control_df = control_df[control_df['indicators'] == ""]
            control_df.drop(['indicators'], axis=1, inplace=True)
        numerator = 1
        denominator = 1
        for x in num_params_cols:
            numerator *= case_df[x] / control_df[x].median()
        for x in den_params_cols:
            denominator *= case_df[x] / control_df[x].median()
        case_df['osi'] = round(numerator / denominator, 2)
        return control_df, case_df

    def generate_file_with_osi(case_df, name):
        path = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'generated_files', session_key)
        osi_df_cols = [id_col]
        if divide_by_age:
            osi_df_cols.append(age_col)
        if divide_by_gender:
            osi_df_cols.append(gender_col)
        if divide_by_ethnicity:
            osi_df_cols.append(ethnicity_col)
        osi_df_cols.append("osi")
        osi_df = case_df[osi_df_cols]
        if not os.path.exists(path):
            os.makedirs(path)
        output_file = os.path.join(path, name + '.xls')
        osi_df.to_excel(output_file, index=False)

        return osi_df

    control_datasets = []
    case_datasets = []
    multiple_files = True

    if divide_by_gender:
        gender_values_quantity = FileGenderValuesQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][
            0].gender_values_quantity
        gender_values_data = FileGenderValue.objects.filter(user_session_key=session_key).order_by("-id")[
                                     :gender_values_quantity]
        gender_values = []
        for value in gender_values_data:
            gender_values.append(float(value.gender_value))
        gender_values.reverse()

    if divide_by_ethnicity:
        ethnicity_values_quantity = FileEthnicityValuesQuantity.objects.filter(user_session_key=session_key).order_by("-id")[:1][
            0].ethnicity_values_quantity
        ethnicity_values_data = FileEthnicityValue.objects.filter(user_session_key=session_key).order_by("-id")[
                                     :ethnicity_values_quantity]
        ethnicity_values = []
        for value in ethnicity_values_data:
            ethnicity_values.append(float(value.ethnicity_value))
        ethnicity_values.reverse()

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'generated_files', session_key)
    if os.path.exists(path_to_delete):
        rmtree(path_to_delete)
    FileOsiResultsFile.objects.all().filter(user_session_key=session_key).delete()

    MIN_CONTROL_DF_ROWS_NUM = 20 #120
    MIN_CASE_DF_ROWS_NUM = 10 #20
    control_df_message = "Контрольная выборка должна содержать не менее %d записей. Недостаточно записей содержат" \
                         " сформированные контрольные выборки со следующими параметрами: " % (MIN_CONTROL_DF_ROWS_NUM)
    control_df_message_check = False
    case_df_message = "Выборка пациентов с патологиями должна содержать не менее %d записей. Недостаточно записей содержат" \
                         " сформированные выборки пациентов с патологиями со следующими параметрами: " % (MIN_CASE_DF_ROWS_NUM)
    case_df_message_check = False
    if divide_by_age and divide_by_gender and divide_by_ethnicity:
        for i in ethnicity_values:
            for j in gender_values:
                for k in control_df['age_intervals'].unique():
                    df = control_df[(control_df[ethnicity_col] == i) & (control_df[gender_col] == j)
                                     & (control_df['age_intervals'] == k)]
                    if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                        control_df_message += "Этника: %s, Пол: %s, Возрастной промежуток: %d - %d записей. "\
                                              % (i, j, k, len(df.index))
                        control_df_message_check = True
                    control_datasets.append(df)
        for i in ethnicity_values:
            for j in gender_values:
                for k in case_df['age_intervals'].unique():
                    df = case_df[(case_df[ethnicity_col] == i) & (case_df[gender_col] == j)
                                  & (case_df['age_intervals'] == k)]
                    if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                        case_df_message += "Этника: %s, Пол: %s, Возрастной промежуток: %d - %d записей. "\
                                              % (i, j, k, len(df.index))
                        case_df_message_check = True
                    case_datasets.append(df)
    elif divide_by_gender and divide_by_ethnicity:
        for i in ethnicity_values:
            for j in gender_values:
                df = control_df[(control_df[ethnicity_col] == i) & (control_df[gender_col] == j)]
                if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                    control_df_message += "Этника: %s, Пол: %s - %d записей. " \
                                          % (i, j, len(df.index))
                    control_df_message_check = True
                control_datasets.append(df)
        for i in ethnicity_values:
            for j in gender_values:
                df = case_df[(case_df[ethnicity_col] == i) & (case_df[gender_col] == j)]
                if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                    case_df_message += "Этника: %s, Пол: %s - %d записей. " \
                                       % (i, j, len(df.index))
                    case_df_message_check = True
                case_datasets.append(df)
    elif divide_by_age and divide_by_ethnicity:
        for i in ethnicity_values:
            for j in control_df['age_intervals'].unique():
                df = control_df[(control_df[ethnicity_col] == i) & (control_df['age_intervals'] == j)]
                if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                    control_df_message += "Этника: %s, Возрастной промежуток: %d - %d записей. " \
                                          % (i, j, len(df.index))
                    control_df_message_check = True
                control_datasets.append(df)
        for i in ethnicity_values:
            for j in case_df['age_intervals'].unique():
                df = case_df[(case_df[ethnicity_col] == i) & (case_df['age_intervals'] == j)]
                if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                    case_df_message += "Этника: %s, Возрастной промежуток: %d - %d записей. " \
                                       % (i, j, len(df.index))
                    case_df_message_check = True
                case_datasets.append(df)
    elif divide_by_age and divide_by_gender:
        for i in control_df['age_intervals'].unique():
            for j in gender_values:
                df = control_df[(control_df['age_intervals'] == i) & (control_df[gender_col] == j)]
                if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                    control_df_message += "Пол: %s, Возрастной промежуток: %d - %d записей. " \
                                          % (j, i, len(df.index))
                    control_df_message_check = True
                control_datasets.append(df)
        for i in case_df['age_intervals'].unique():
            for j in gender_values:
                df = case_df[(case_df['age_intervals'] == i) & (case_df[gender_col] == j)]
                if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                    case_df_message += "Пол: %s, Возрастной промежуток: %d - %d записей. " \
                                       % (j, i, len(df.index))
                    case_df_message_check = True
                case_datasets.append(df)
    elif divide_by_ethnicity:
        for i in ethnicity_values:
            df = control_df[control_df[ethnicity_col] == i]
            if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                control_df_message += "Этника: %s - %d записей. " \
                                      % (i, len(df.index))
                control_df_message_check = True
            control_datasets.append(df)
        for i in ethnicity_values:
            df = case_df[case_df[ethnicity_col] == i]
            if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                case_df_message += "Этника: %s - %d записей. " \
                                   % (i, len(df.index))
                case_df_message_check = True
            case_datasets.append(df)
    elif divide_by_gender:
        for i in gender_values:
            df = control_df[control_df[gender_col] == i]
            if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                control_df_message += "Пол: %s - %d записей. " \
                                      % (i, len(df.index))
                control_df_message_check = True
            control_datasets.append(df)
        for i in gender_values:
            df = case_df[case_df[gender_col] == i]
            if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                case_df_message += "Пол: %s - %d записей. " \
                                   % (i, len(df.index))
                case_df_message_check = True
            case_datasets.append(df)
    elif divide_by_age:
        for i in control_df['age_intervals'].unique():
            df = control_df[control_df['age_intervals'] == i]
            if len(df.index) < MIN_CONTROL_DF_ROWS_NUM:
                control_df_message += "Возрастной промежуток: %d - %d записей. " \
                                      % (i, len(df.index))
                control_df_message_check = True
            control_datasets.append(df)
        for i in case_df['age_intervals'].unique():
            df = case_df[case_df['age_intervals'] == i]
            if len(df.index) < MIN_CASE_DF_ROWS_NUM:
                case_df_message += "Возрастной промежуток: %d - %d записей. " \
                                   % (i, len(df.index))
                case_df_message_check = True
            case_datasets.append(df)
    else:
        if len(control_df.index) < MIN_CONTROL_DF_ROWS_NUM:
            control_df_message += "Контрольная выборка - %d записей. " % (len(control_df.index))
            control_df_message_check = True
        if len(case_df.index) < MIN_CASE_DF_ROWS_NUM:
            case_df_message += "Выборка пациентов с патологиями - %d записей. " % (len(case_df.index))
            case_df_message_check = True
        if control_df_message_check and case_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": control_df_message + case_df_message,
                           "href": "file_data"})
        elif control_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": control_df_message,
                           "href": "file_data"})
        elif case_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": case_df_message,
                           "href": "file_data"})
        control_df, case_df = find_osi(control_df, case_df)
        generate_file_with_osi(case_df, 'osi_data')
        multiple_files = False

    if multiple_files:

        if control_df_message_check and case_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": control_df_message + case_df_message,
                           "href": "file_data"})
        elif control_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": control_df_message,
                           "href": "file_data"})
        elif case_df_message_check:
            return render(request, "Osi/file_osi/error.html",
                          {"error": case_df_message,
                           "href": "file_data"})

        osi_datasets = []

        for i in range(len(control_datasets)):
            control_datasets[i], case_datasets[i] = find_osi(control_datasets[i], case_datasets[i])
            osi_datasets.append(
                generate_file_with_osi(case_datasets[i], 'osi_data_' + str(i + 1)))

    def create_zipfile(session_key):
        path = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'generated_files', session_key)
        archives_path = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'zip_archives', session_key)
        if not os.path.exists(archives_path):
            os.makedirs(archives_path)
        make_archive(os.path.join(archives_path, 'osi_results'), 'zip', path)

    create_zipfile(session_key)

    FileOsiResultsArchive.objects.create(
        osi_results_archive=os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'zip_archives', session_key, 'osi_results.zip'),
        user_session_key=session_key
    )


    path_to_save = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'generated_files', session_key)
    for file_name in os.listdir(path_to_save):
        file = os.path.join(path_to_save, file_name)
        FileOsiResultsFile.objects.create(
            osi_results_file=file,
            user_session_key=session_key
        )




    return HttpResponseRedirect('file_results')


def get_file_columns(request, data_file):
    data_file_suffix = pathlib.Path(data_file.name).suffix
    if data_file_suffix == '.csv':
        columns = pd.read_csv(data_file, on_bad_lines='skip').columns[0].split(';')
    elif data_file_suffix == '.xls' or data_file_suffix == '.xlsx':
        columns = pd.read_excel(data_file, sheet_name=0, index_col=None).columns.values
    else:
        print("Wrong extension")
        columns = []
    return columns


def get_column_unique_values(request, data_file, column):
    data_file_suffix = pathlib.Path(data_file.name).suffix
    if data_file_suffix == '.csv':
        values = pd.read_csv(data_file, sep=';', on_bad_lines='skip')[column].unique()
    elif data_file_suffix == '.xls' or data_file_suffix == '.xlsx':
        values = pd.read_excel(data_file, sheet_name=0, index_col=None)[column].unique()
    else:
        print("Wrong extension")
        values = []

    return values
