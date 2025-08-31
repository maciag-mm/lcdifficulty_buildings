"""
Model exported as python.
Name : PAW g3 POWIERZCHNIA 1.1
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG3Powierzchnia11(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G3', 'g3', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # g3
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'g3',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'sum($area/10000,group_by:="layer")/count($id,group_by:="layer")',
            'INPUT': parameters['obszary_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['G3'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie
        alg_params = {
            'INPUT': outputs['G3']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrie'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Agreguj
        alg_params = {
            'FIELD': ['layer'],
            'INPUT': outputs['PorzuGeometrie']['OUTPUT'],
            'SEPARATE_DISJOINT': False,
            'OUTPUT': parameters['G3']
        }
        outputs['Agreguj'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G3'] = outputs['Agreguj']['OUTPUT']
        return results

    def name(self):
        return 'PAW g3 POWIERZCHNIA 1.1'

    def displayName(self):
        return 'PAW g3 POWIERZCHNIA 1.1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG3Powierzchnia11()
