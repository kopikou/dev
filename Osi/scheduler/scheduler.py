from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
import sys
from datetime import datetime
import os
import shutil

from ..models import FieldsMode, FieldsData, FieldsSelectionCol, FieldsSelectionColValue, FieldsDivisionCols,\
    FieldsPatientInfo, FieldsPatientNumParam, FieldsPatientDenParam, FieldsAgeIntervalBorders,\
    FieldsDivideByEthnicityDefault, FieldsPatientDefault, FieldsPatientResultExcelFile, FieldsPatientTable

from ..models import FileData, FileIdCol, FileNumeratorParamCol, FileDenominatorParamCol, FileDivisionCols,\
    FileAgeIntervalsQuantity, FileAgeIntervalBorders, FileGenderValuesQuantity, FileGenderValue,\
    FileEthnicityValuesQuantity, FileEthnicityValue, FileSelectionCol, FileSelectionColValues, FileOsiResultsArchive,\
    FileOsiResultsFile


def clear_database_and_filesystem():
    FieldsMode.objects.all().delete()
    FieldsData.objects.all().delete()
    FieldsSelectionCol.objects.all().delete()
    FieldsSelectionColValue.objects.all().delete()
    FieldsDivisionCols.objects.all().delete()
    FieldsPatientInfo.objects.all().delete()
    FieldsPatientNumParam.objects.all().delete()
    FieldsPatientDenParam.objects.all().delete()
    FieldsAgeIntervalBorders.objects.all().delete()
    FieldsDivideByEthnicityDefault.objects.all().delete()
    FieldsPatientDefault.objects.all().delete()
    FieldsPatientResultExcelFile.objects.all().delete()
    FieldsPatientTable.objects.all().delete()

    FileData.objects.all().delete()
    FileIdCol.objects.all().delete()
    FileNumeratorParamCol.objects.all().delete()
    FileDenominatorParamCol.objects.all().delete()
    FileDivisionCols.objects.all().delete()
    FileAgeIntervalsQuantity.objects.all().delete()
    FileAgeIntervalBorders.objects.all().delete()
    FileGenderValuesQuantity.objects.all().delete()
    FileGenderValue.objects.all().delete()
    FileEthnicityValuesQuantity.objects.all().delete()
    FileEthnicityValue.objects.all().delete()
    FileSelectionCol.objects.all().delete()
    FileSelectionColValues.objects.all().delete()
    FileOsiResultsArchive.objects.all().delete()
    FileOsiResultsFile.objects.all().delete()


    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Время: %s. База данных очищена." % (datetime_str))

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'generated_files')
    for dir_name in os.listdir(path_to_delete):
        dir = os.path.join(path_to_delete, dir_name)
        print('Deleting dir:', dir)
        shutil.rmtree(dir)

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'fields', 'uploaded')
    for dir_name in os.listdir(path_to_delete):
        dir = os.path.join(path_to_delete, dir_name)
        print('Deleting dir:', dir)
        os.remove(dir)


    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'generated_files')
    for dir_name in os.listdir(path_to_delete):
        dir = os.path.join(path_to_delete, dir_name)
        print('Deleting dir:', dir)
        shutil.rmtree(dir)

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'uploaded')
    for dir_name in os.listdir(path_to_delete):
        dir = os.path.join(path_to_delete, dir_name)
        print('Deleting dir:', dir)
        os.remove(dir)

    path_to_delete = os.path.join(settings.MEDIA_ROOT, 'Osi', 'file', 'zip_archives')
    for dir_name in os.listdir(path_to_delete):
        dir = os.path.join(path_to_delete, dir_name)
        print('Deleting dir:', dir)
        shutil.rmtree(dir)

    datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("Время: %s. Файловая система очищена." % (datetime_str))



def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(clear_database_and_filesystem, trigger='cron', hour='03', minute='00', name='clear_db_and_fs', jobstore='default')
    register_events(scheduler)
    scheduler.start()
    print("Scheduler started...", file=sys.stdout)