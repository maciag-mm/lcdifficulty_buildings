"""
Model exported as python.
Name : PAW g6 GĘSTOŚĆ BUDYNKÓW W OBSZ ZAB 1.2
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PawG6GstoBudynkwWObszZab12(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('budynki', 'Budynki', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('G6', 'g6', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # Licz budynki
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'L_BUD',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Liczba całkowita (32-bitowa)
            'FORMULA': 'count($id,group_by:="layer")',
            'INPUT': parameters['budynki'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LiczBudynki'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Licz powierzchnię obszarów zabudowy
        alg_params = {
            'FIELD_LENGTH': 12,
            'FIELD_NAME': 'P_OBS',
            'FIELD_PRECISION': 4,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'sum($area,group_by:="layer")',
            'INPUT': parameters['obszary_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['LiczPowierzchniObszarwZabudowy'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie obszarów
        alg_params = {
            'INPUT': outputs['LiczPowierzchniObszarwZabudowy']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrieObszarw'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Porzuć geometrie budynków
        alg_params = {
            'INPUT': outputs['LiczBudynki']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PorzuGeometrieBudynkw'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Agreguj budynki
        alg_params = {
            'FIELD': ['layer'],
            'INPUT': outputs['PorzuGeometrieBudynkw']['OUTPUT'],
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujBudynki'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Dostosuj pola
        alg_params = {
            'FIELD_LENGTH': 64,
            'FIELD_NAME': 'layer2',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': 'replace("layer",\'BUD\',\'OBSZ_ZABUD\')',
            'INPUT': outputs['AgregujBudynki']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DostosujPola'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Agreguj obszary
        alg_params = {
            'FIELD': ['layer'],
            'INPUT': outputs['PorzuGeometrieObszarw']['OUTPUT'],
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AgregujObszary'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # g6
        alg_params = {
            'FIELD_LENGTH': 18,
            'FIELD_NAME': 'g6',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': 'attribute(get_feature( @Agreguj_budynki_OUTPUT,\'layer\',replace("layer",\'OBSZ_ZABUD\',\'BUD\')),\'L_BUD\')/("P_OBS"/10000)',
            'INPUT': outputs['AgregujObszary']['OUTPUT'],
            'OUTPUT': parameters['G6']
        }
        outputs['G6'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['G6'] = outputs['G6']['OUTPUT']
        return results

    def name(self):
        return 'PAW g6 GĘSTOŚĆ BUDYNKÓW W OBSZ ZAB 1.2'

    def displayName(self):
        return 'PAW g6 GĘSTOŚĆ BUDYNKÓW W OBSZ ZAB 1.2'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG6GstoBudynkwWObszZab12()
