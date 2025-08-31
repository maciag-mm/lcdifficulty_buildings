"""
Model exported as python.
Name : PAW g1 DŁUGOŚĆ 1.1
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG1Dugo11(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G1', 'g1', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
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

        # Najmniejsze zorientowane prostokąty ograniczające
        alg_params = {
            'INPUT': outputs['LiczPowierzchniObszarw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NajmniejszeZorientowaneProstoktyOgraniczajce'] = processing.run('native:orientedminimumboundingbox', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Numeruj prostokąty
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'IDP',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Liczba całkowita (32-bitowa)
            'FORMULA': '$id',
            'INPUT': outputs['NajmniejszeZorientowaneProstoktyOgraniczajce']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NumerujProstokty'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Wyodrębnij krawędzie
        alg_params = {
            'INPUT': outputs['NumerujProstokty']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WyodrbnijKrawdzie'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Rozdziel linie
        alg_params = {
            'INPUT': outputs['WyodrbnijKrawdzie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RozdzielLinie'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Podaj długości dla obszarów
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'OBZ_g1',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'maximum($length,group_by:="IDP")',
            'INPUT': outputs['RozdzielLinie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PodajDugociDlaObszarw'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie
        alg_params = {
            'INPUT': outputs['PodajDugociDlaObszarw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrie'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Agreguj do poligonów
        alg_params = {
            'FIELDS': ['IDP'],
            'INPUT': outputs['PorzuGeometrie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujDoPoligonw'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Oblicz długości dla wsi
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'g1',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'sum("OBZ_g1"*"AREA",group_by:="layer")/sum("AREA",group_by:="layer")',
            'INPUT': outputs['AgregujDoPoligonw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ObliczDugociDlaWsi'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Agreguj do wsi
        alg_params = {
            'FIELDS': ['layer'],
            'INPUT': outputs['ObliczDugociDlaWsi']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujDoWsi'] = processing.run('native:removeduplicatesbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Czyść pola
        alg_params = {
            'FIELDS': ['layer','g1'],
            'INPUT': outputs['AgregujDoWsi']['OUTPUT'],
            'OUTPUT': parameters['G1']
        }
        outputs['CzyPola'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G1'] = outputs['CzyPola']['OUTPUT']
        return results

    def name(self):
        return 'PAW g1 DŁUGOŚĆ 1.1'

    def displayName(self):
        return 'PAW g1 DŁUGOŚĆ 1.1'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG1Dugo11()
