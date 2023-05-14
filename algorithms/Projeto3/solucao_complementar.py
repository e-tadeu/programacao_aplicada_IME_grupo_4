# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo4
                                 A QGIS plugin
 Solução do Grupo 4
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-04
        copyright            : (C) 2023 by Grupo 4
        emails               : e.tadeu.eb@ime.eb.br
                               raulmagno@ime.eb.br
                               arthur.cavalcante@ime.eb.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Grupo 4'
__date__ = '2023-05-04'
__copyright__ = '(C) 2023 by Grupo 4'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsExpression)
import processing


class Projeto4SolucaoComplementar(QgsProcessingAlgorithm):
    """
    Este algoritmo realiza a generalização de edifícios próximos às rodovias.

    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def initAlgorithm(self, config=None):
        #Entradas
        self.addParameter(QgsProcessingParameterVectorLayer('drenagem', 'Drenagem', 
                                                            types=[QgsProcessing.TypeVectorLine], 
                                                            defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('massas_de_agua', 'Massas de Agua',
                                                            types=[QgsProcessing.TypeVectorPolygon],
                                                            defaultValue=None))
        #Saida
        self.addParameter(QgsProcessingParameterFeatureSink('Trecho_drenagens_ajust', 'Trecho_Drenagens_Ajust',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True,
                                                            supportsAppend=True,
                                                            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Indices Espaciais Massas de Agua
        alg_params = {
            'INPUT': parameters['massas_de_agua']
        }
        outputs['IndicesEspaciaisMassasDeAgua'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Indices Espaciais Drenagens
        alg_params = {
            'INPUT': parameters['drenagem']
        }
        outputs['IndicesEspaciaisDrenagens'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Intersecao 
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['IndicesEspaciaisDrenagens']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OVERLAY': outputs['IndicesEspaciaisMassasDeAgua']['OUTPUT'],
            'OVERLAY_FIELDS': ['null'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersec'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Diferenca simetrica
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['IndicesEspaciaisDrenagens']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OVERLAY': outputs['Intersec']['OUTPUT'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DiferencaSimetrica'] = processing.run('native:symmetricaldifference', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Coluna Temporaria Verdadeira
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Col_Temp_True',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 6,  # Booleano
            'FORMULA': 'true',
            'INPUT': outputs['Intersec']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ColunaTemporriaVerdadeira'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Uniao
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['DiferencaSimetrica']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OVERLAY': outputs['Intersec']['OUTPUT'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Uniao'] = processing.run('native:union', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Associar atributos por localizacao
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['Uniao']['OUTPUT'],
            'JOIN': outputs['ColunaTemporriaVerdadeira']['OUTPUT'],
            'JOIN_FIELDS': [''],
            'METHOD': 1,  # Tomar atributos apenas da primeira feicao coincidente (uma-por-uma)
            'NON_MATCHING': None,
            'PREDICATE': [2],  # igual
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AssociarAtributosPorLocalizao'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Criacao da Coluna Final
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'dentro_de_poligono',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 6,  # Booleano
            'FORMULA': 'if("Col_Temp_True" = true,true,false)',
            'INPUT': outputs['AssociarAtributosPorLocalizao']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CriacaoDaColunaFinal'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Descartar coluna temporaria
        alg_params = {
            'COLUMN': ['Col_Temp_True'],
            'INPUT': outputs['CriacaoDaColunaFinal']['OUTPUT'],
            'OUTPUT': parameters['Trecho_drenagens_ajust']
        }
        outputs['DelColTemp'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Trecho_drenagens_ajust'] = outputs['DelColTemp']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução Complementar do Projeto 2'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Projeto 2'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto2SolucaoComplementar()
    
  