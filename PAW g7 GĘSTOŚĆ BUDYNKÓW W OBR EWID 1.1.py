"""
Model exported as python.
Name : PAW g7 GĘSTOŚĆ BUDYNKÓW W OBR EWID 1.1
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG7GstoBudynkwWObrEwid11(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('budynki', 'Budynki', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('obrby_ewidencyjne', 'Obręby ewidencyjne', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G7', 'g7', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Licz powierzchnię obrębów ewidenycjnych
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'P_OBR',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': '$area/10000',
            'INPUT': parameters['obrby_ewidencyjne'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LiczPowierzchniObrbwEwidenycjnych'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Centroidy
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': parameters['budynki'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroidy'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Policz budynki w obrębach
        alg_params = {
            'CLASSFIELD': None,
            'FIELD': 'L_BUD',
            'POINTS': outputs['Centroidy']['OUTPUT'],
            'POLYGONS': outputs['LiczPowierzchniObrbwEwidenycjnych']['OUTPUT'],
            'WEIGHT': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoliczBudynkiWObrbach'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie
        alg_params = {
            'INPUT': outputs['PoliczBudynkiWObrbach']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrie'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # g7
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'g7',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': '"L_BUD"/"P_OBR"',
            'INPUT': outputs['PorzuGeometrie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['G7'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Czyść pola
        alg_params = {
            'FIELDS': ['JPT_NAZWA_','g7'],
            'INPUT': outputs['G7']['OUTPUT'],
            'OUTPUT': parameters['G7']
        }
        outputs['CzyPola'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G7'] = outputs['CzyPola']['OUTPUT']
        return results

    def name(self):
        return 'PAW g7 GĘSTOŚĆ BUDYNKÓW W OBR EWID 1.1'

    def displayName(self):
        return 'PAW g7 GĘSTOŚĆ BUDYNKÓW W OBR EWID 1.1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG7GstoBudynkwWObrEwid11()
