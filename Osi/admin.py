from django.contrib import admin

from .models import FieldsMode, FieldsData, FieldsSelectionCol, FieldsSelectionColValue, FieldsDivisionCols,\
    FieldsPatientInfo, FieldsPatientNumParam, FieldsPatientDenParam, FieldsAgeIntervalBorders,\
    FieldsDivideByEthnicityDefault, FieldsPatientDefault, FieldsPatientResultExcelFile, FieldsPatientTable,\
    FieldsExcelFileDefault

from .models import FileData, FileIdCol, FileNumeratorParamCol, FileDenominatorParamCol, FileDivisionCols,\
    FileAgeIntervalsQuantity, FileAgeIntervalBorders, FileGenderValuesQuantity, FileGenderValue,\
    FileEthnicityValuesQuantity, FileEthnicityValue, FileSelectionCol, FileSelectionColValues, FileOsiResultsArchive,\
    FileOsiResultsFile


#fields
admin.site.register(FieldsMode)
admin.site.register(FieldsData)
admin.site.register(FieldsSelectionCol)
admin.site.register(FieldsSelectionColValue)
admin.site.register(FieldsDivisionCols)
admin.site.register(FieldsPatientInfo)
admin.site.register(FieldsPatientNumParam)
admin.site.register(FieldsPatientDenParam)
admin.site.register(FieldsAgeIntervalBorders)
admin.site.register(FieldsDivideByEthnicityDefault)
admin.site.register(FieldsPatientDefault)
admin.site.register(FieldsPatientResultExcelFile)
admin.site.register(FieldsPatientTable)
admin.site.register(FieldsExcelFileDefault)


#file
admin.site.register(FileData)
admin.site.register(FileIdCol)
admin.site.register(FileNumeratorParamCol)
admin.site.register(FileDenominatorParamCol)
admin.site.register(FileDivisionCols)
admin.site.register(FileAgeIntervalsQuantity)
admin.site.register(FileAgeIntervalBorders)
admin.site.register(FileGenderValuesQuantity)
admin.site.register(FileGenderValue)
admin.site.register(FileEthnicityValuesQuantity)
admin.site.register(FileEthnicityValue)
admin.site.register(FileSelectionCol)
admin.site.register(FileSelectionColValues)
admin.site.register(FileOsiResultsArchive)
admin.site.register(FileOsiResultsFile)



