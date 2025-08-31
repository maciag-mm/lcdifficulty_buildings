"""
Model exported as python.
Name : PAW g8 g9 KOMIWOJAŻER p1 1.4
Group : 
With QGIS : 34000
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFolderDestination
import processing


class PawG8G9KomiwojaerP114(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('budynki', 'Budynki', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('obszary_zabudowy', 'Obszary zabudowy', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFolderDestination('Test', 'test', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(8, model_feedback)
        results = {}
        outputs = {}

        # Indeksuj obszary
        alg_params = {
            'FIELD_LENGTH': 128,
            'FIELD_NAME': 'ZID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Tekst (string)
            'FORMULA': 'concat("layer",\'_\',$id)',
            'INPUT': parameters['obszary_zabudowy'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IndeksujObszary'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Przypisz ZID do budynków
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': parameters['budynki'],
            'JOIN': outputs['IndeksujObszary']['OUTPUT'],
            'JOIN_FIELDS': ['ZID'],
            'METHOD': 0,  # twórz oddzielny obiekt dla każdego pasującego obiektu (jeden do wielu)
            'PREDICATE': [1,2,4,5],  # zawierają się,są równe,nachodzą,znajdują się wewnątrz
            'PREFIX': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PrzypiszZidDoBudynkw'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Centroidy
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['PrzypiszZidDoBudynkw']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroidy'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Indeksuj budynki
        alg_params = {
            'FIELD_LENGTH': 6,
            'FIELD_NAME': 'BID',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Liczba dziesiętna (double)
            'FORMULA': '$id',
            'INPUT': outputs['Centroidy']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['IndeksujBudynki'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Dodaj atrybuty geometrii
        alg_params = {
            'CALC_METHOD': 0,  # układ warstwy
            'INPUT': outputs['IndeksujBudynki']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DodajAtrybutyGeometrii'] = processing.run('qgis:exportaddgeometrycolumns', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Czyść pola
        alg_params = {
            'FIELDS': ['BID','ZID','xcoord','ycoord'],
            'INPUT': outputs['DodajAtrybutyGeometrii']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CzyPola'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Usuń geometrie
        alg_params = {
            'INPUT': outputs['CzyPola']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['UsuGeometrie'] = processing.run('native:dropgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Podziel warstwę wektorową
        alg_params = {
            'FIELD': 'ZID',
            'FILE_TYPE': 5,  # csv
            'INPUT': outputs['UsuGeometrie']['OUTPUT'],
            'PREFIX_FIELD': False,
            'OUTPUT': parameters['Test']
        }
        outputs['PodzielWarstwWektorow'] = processing.run('native:splitvectorlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Test'] = outputs['PodzielWarstwWektorow']['OUTPUT']
        return results

    def name(self):
        return 'PAW g8 g9 KOMIWOJAŻER p1 1.4'

    def displayName(self):
        return 'PAW g8 g9 KOMIWOJAŻER p1 1.4'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PawG8G9KomiwojaerP114()
