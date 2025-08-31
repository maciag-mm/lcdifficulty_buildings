"""
Model exported as python.
Name : PAW g2 WYDŁUŻENIE 1.1
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG2Wyduenie11(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G2', 'g2', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Licz powierzchnię obszarów
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'AREA',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': '$area',
            'INPUT': parameters['obszary_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LiczPowierzchniObszarw'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Licz wydłużenie W
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'W',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'IF(sqrt($perimeter^2-16*$area),\r\n($perimeter+sqrt($perimeter^2-16*$area))/($perimeter-sqrt($perimeter^2-16*$area)),0)',
            'INPUT': outputs['LiczPowierzchniObszarw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LiczWyduenieW'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Agreguj W dla wsi
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'g2',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'sum("W"*$area,group_by:="layer")/sum($area,group_by:="layer")',
            'INPUT': outputs['LiczWyduenieW']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujWDlaWsi'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie
        alg_params = {
            'INPUT': outputs['AgregujWDlaWsi']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrie'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Czyść pola
        alg_params = {
            'FIELDS': ['layer','g2'],
            'INPUT': outputs['PorzuGeometrie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CzyPola'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Agreguj wyniki
        alg_params = {
            'FIELDS': ['layer'],
            'INPUT': outputs['CzyPola']['OUTPUT'],
            'OUTPUT': parameters['G2']
        }
        outputs['AgregujWyniki'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G2'] = outputs['AgregujWyniki']['OUTPUT']
        return results

    def name(self):
        return 'PAW g2 WYDŁUŻENIE 1.1'

    def displayName(self):
        return 'PAW g2 WYDŁUŻENIE 1.1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG2Wyduenie11()
