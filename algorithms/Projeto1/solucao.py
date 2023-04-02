# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ProgramacaoAplicadaGrupo4
                                 A QGIS plugin
 Solução do Grupo 4
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-04-04
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
__date__ = '2023-04-04'
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


class Projeto1Solucao(QgsProcessingAlgorithm):
    """
    This is an algorithm that takes a vector layer and
    creates a new identical one.

    """

    def initAlgorithm(self, config=None):
        # Camada de Entrada.
        self.addParameter(QgsProcessingParameterVectorLayer('pontos_de_controle', 'Pontos de Controle', 
                                                            types=[QgsProcessing.TypeVectorPoint], 
                                                            defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('mde', 'MDE',
                                                             defaultValue=None))
        
          # Camada de Saida.
        self.addParameter(QgsProcessingParameterFeatureSink('AcuraciaAltimetrica', 'Acuracia Altimetrica', 
                                                            type=QgsProcessing.TypeVectorAnyGeometry, 
                                                            createByDefault=True, 
                                                            supportsAppend=True, 
                                                            defaultValue='TEMPORARY_OUTPUT'))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Delimitando limites
        alg_params = {
            'LAYERS': parameters['mde'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DelimitandoLimites'] = processing.run('native:exportlayersinformation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Descartando campos
        alg_params = {
            'COLUMN': QgsExpression("'source;crs;provider;file_path;layer_name;subset;abstract;attribution'").evaluate(),
            'INPUT': outputs['DelimitandoLimites']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DescartandoCampos'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Filtrando pontos
        alg_params = {
            'INPUT': parameters['pontos_de_controle'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OVERLAYS': outputs['DescartandoCampos']['OUTPUT'],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FiltrandoPontos'] = processing.run('native:multiintersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Extraindo o Z da geometria
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ZRef',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '$z',
            'INPUT': outputs['FiltrandoPontos']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraindoOZDaGeometria'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Extraindo valores do raster
        alg_params = {
            'COLUMN_PREFIX': 'ZRast',
            'INPUT': outputs['ExtraindoOZDaGeometria']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'RASTERCOPY': parameters['mde'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtraindoValoresDoRaster'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Calculando o Erro
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Erro',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '"ZRef"-"ZRast1"',
            'INPUT': outputs['ExtraindoValoresDoRaster']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CalculandoOErro'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # EMQz
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'EMQz',
            'FIELD_PRECISION': 2,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '(mean("Erro","name"))^2',
            'INPUT': outputs['CalculandoOErro']['OUTPUT'],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Emqz'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Analise do PEC
        alg_params = {
            'FIELD_LENGTH': 50,
            'FIELD_NAME': 'PEC',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Texto (string)
            'FORMULA': 'if("EMQz"<=1.67,\'A\',if("EMQz">1.67 AND "EMQz"<=3.33,\'B\',if("EMQz">3.33 AND "EMQz"<=4.00,\'C\',if("EMQz">4.00 AND "EMQz"<=5.00,\'D\',\'Sem Classifica��o\'))))\r\n\r\n',
            'INPUT': outputs['Emqz']['OUTPUT'],
            'OUTPUT': parameters['AcuraciaAltimetrica']
        }
        outputs['AnaliseDoPec'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['AcuraciaAltimetrica'] = outputs['AnaliseDoPec']['OUTPUT']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Configurando o estilo da camada
        alg_params = {
            'INPUT': outputs['AnaliseDoPec']['OUTPUT'],
            'STYLE': 'estilo-erro-altimetrico.qml'
        }
        outputs['ConfigurandoOEstiloDaCamada'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução do Projeto 1'

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
        return 'Projeto 1'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return Projeto1Solucao()
