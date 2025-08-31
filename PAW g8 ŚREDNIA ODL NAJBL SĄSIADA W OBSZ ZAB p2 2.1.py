"""
Model exported as python.
Name : PAW g8 ŚREDNIA ODL NAJBL SASIADA W OBSZ ZAB p2 2.1
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG8RedniaOdlNajblSasiadaWObszZabP221(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('plik_hamiltonowski_out_dla_obszarw_zabudowy', 'Plik hamiltonowski "OUT" dla obszarów zabudowy', types=[QgsProcessing.TypeVector], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G8_lok', 'g8_lok', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G8', 'g8', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        outputs = {}

        # Znajdź UID w pliku
        alg_params = {
            'FIELD_LENGTH': 255,
            'FIELD_NAME': 'UID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': 'replace(replace("field_1",concat(\'C:\',char(92),\'KomIn\',char(47)),\'\'),\'.csv\',\'\')',
            'INPUT': parameters['plik_hamiltonowski_out_dla_obszarw_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZnajdUidWPliku'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Nadaj UID obszarom
        alg_params = {
            'FIELD_LENGTH': 255,
            'FIELD_NAME': 'UID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': 'concat("layer",\'_\',$id)',
            'INPUT': parameters['obszary_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NadajUidObszarom'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # g8_lokalny
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'g8_lok',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'attribute(get_feature( @Znajdź_UID_w_pliku_OUTPUT ,\'UID\',"UID"),\'field_2\')',
            'INPUT': outputs['NadajUidObszarom']['OUTPUT'],
            'OUTPUT': parameters['G8_lok']
        }
        outputs['G8_lokalny'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G8_lok'] = outputs['G8_lokalny']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Napraw g8
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'g8_kor',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'CASE\r\nWHEN "g8_lok">100000 THEN 0\r\nELSE "g8_lok"\r\nEND',
            'INPUT': outputs['G8_lokalny']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NaprawG8'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # g8
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'g8',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': ' sum("g8_kor"*$area,group_by:="layer")/sum($area,group_by:="layer")',
            'INPUT': outputs['NaprawG8']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['G8'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Agreguj dla wsi
        alg_params = {
            'FIELDS': ['layer'],
            'INPUT': outputs['G8']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujDlaWsi'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Zachowaj pola
        alg_params = {
            'FIELDS': ['layer','g8'],
            'INPUT': outputs['AgregujDlaWsi']['OUTPUT'],
            'OUTPUT': parameters['G8']
        }
        outputs['ZachowajPola'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G8'] = outputs['ZachowajPola']['OUTPUT']
        return results

    def name(self):
        return 'PAW g8 ŚREDNIA ODL NAJBL SASIADA W OBSZ ZAB p2 2.1'

    def displayName(self):
        return 'PAW g8 ŚREDNIA ODL NAJBL SASIADA W OBSZ ZAB p2 2.1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG8RedniaOdlNajblSasiadaWObszZabP221()
