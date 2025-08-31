"""
Model exported as python.
Name : SALATA 1.3
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Salata13(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('budynki', 'Budynki', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('ObszaryZabudowy', 'Obszary zabudowy', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

        # Napraw geometrie budynków
        alg_params = {
            'INPUT': parameters['budynki'],
            'METHOD': 1,  # strukturalna
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NaprawGeometrieBudynkw'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Wyodrębnij wierzchołki
        alg_params = {
            'INPUT': outputs['NaprawGeometrieBudynkw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WyodrbnijWierzchoki'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Triangulacja Delone
        alg_params = {
            'ADD_ATTRIBUTES': True,
            'INPUT': outputs['WyodrbnijWierzchoki']['OUTPUT'],
            'TOLERANCE': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TriangulacjaDelone'] = processing.run('native:delaunaytriangulation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Dodaj ID trójkąta
        alg_params = {
            'FIELD_LENGTH': 16,
            'FIELD_NAME': 'IDT',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Liczba całkowita (32-bitowa)
            'FORMULA': '$id',
            'INPUT': outputs['TriangulacjaDelone']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DodajIdTrjkta'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Poligony na linie
        alg_params = {
            'INPUT': outputs['DodajIdTrjkta']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonyNaLinie'] = processing.run('native:polygonstolines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Rozdziel linie
        alg_params = {
            'INPUT': outputs['PoligonyNaLinie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RozdzielLinie'] = processing.run('native:explodelines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Testuj krawędzie
        alg_params = {
            'FIELD_LENGTH': 1,
            'FIELD_NAME': 'TEST_KR',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Liczba całkowita (32-bitowa)
            'FORMULA': 'CASE\r\nWHEN length($geometry) > 160 THEN 1\r\nELSE 0\r\nEND',
            'INPUT': outputs['RozdzielLinie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TestujKrawdzie'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Testuj trójkąty
        alg_params = {
            'FIELD_LENGTH': 1,
            'FIELD_NAME': 'TEST_TR',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Liczba całkowita (32-bitowa)
            'FORMULA': 'CASE\r\nWHEN sum("TEST_KR",group_by:="IDT")=0 THEN 1\r\nELSE 0\r\nEND',
            'INPUT': outputs['TestujKrawdzie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['TestujTrjkty'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Przypisz wynik testu
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': 'IDT',
            'FIELDS_TO_COPY': ['TEST_TR'],
            'FIELD_2': 'IDT',
            'INPUT': outputs['DodajIdTrjkta']['OUTPUT'],
            'INPUT_2': outputs['TestujTrjkty']['OUTPUT'],
            'METHOD': 1,  # przyjmuj atrybuty tylko z pierwszego pasującego obiektu (jeden do jednego)
            'PREFIX': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PrzypiszWynikTestu'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Selekcja trójkątów
        alg_params = {
            'EXPRESSION': '"TEST_TR"=1',
            'INPUT': outputs['PrzypiszWynikTestu']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['SelekcjaTrjktw'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Agregacja obszarów zabudowy
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['SelekcjaTrjktw']['OUTPUT'],
            'SEPARATE_DISJOINT': True,
            'OUTPUT': parameters['ObszaryZabudowy']
        }
        outputs['AgregacjaObszarwZabudowy'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ObszaryZabudowy'] = outputs['AgregacjaObszarwZabudowy']['OUTPUT']
        return results

    def name(self):
        return 'SALATA 1.3'

    def displayName(self):
        return 'SALATA 1.3'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Salata13()
