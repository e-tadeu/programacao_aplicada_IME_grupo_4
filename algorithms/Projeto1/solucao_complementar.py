
"""
/***************************************************************************
 ProgramacaoAplicadaGrupo4
                                 A QGIS plugin
 Solução Complementar do Grupo 4
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

import os
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsCoordinateReferenceSystem, 
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingMultiStepFeedback,
                       QgsRasterLayer,
                       QgsProcessingException,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsExpression)
import processing

class Projeto1SolucaoComplementar(QgsProcessingAlgorithm):

    """
    Calcular o EMQz entre os MDS adjacentes (pareados dois a dois,
    considerando a maior área de sobreposição entre rasters adjacentes), 
    criando uma malha de pontos com 200 metros de distância
    X e Y nas intersecçoes:

    • Determinar x min, x max, y min, y max de cada raster;

    • Realizar loop em x e y considerando a distância de 200 metros em x
    e y;

    • Somente considerar para o cálculo pontos que estejam em ambos os
    raster;

    • A entrada do processo devem ser todos os rasters a serem
    considerados;

    • A saída do processo deve ser no formato vetorial polígono. Cada
    polígono de saída é a intersecção dos rasters avaliados devem ter
    atributos raster1 (basename do arquivo 1), raster2 (basename do
    arquivo 2) e emqz.

    """

    def initAlgorithm(self, config=None):
        # Camada de Entrada.
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_1', 'Input raster 1', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_2', 'Input raster 2', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_3', 'Input raster 3', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_4', 'Input raster 4', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_5', 'Input raster 5', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('input_raster_6', 'Input raster 6', defaultValue=None))

        
        #self.addParameter(QgsProcessingParameterFile('mdes', 'Modelos Digitais de Superficie', fileFilter='Tif (*.TIF)'))


        # Camada de Saida.
        self.addParameter(QgsProcessingParameterFeatureSink('multi_polygon', 'Multiplos polígonos', 
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True,
                                                            supportsAppend=True,
                                                            defaultValue='TEMPORARY_OUTPUT'))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model

        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        outputs = {}

        # Defining crs
        crs = QgsCoordinateReferenceSystem(
        'EPSG:31982'
        )

        input_rasters = [parameters['input_raster_1'], parameters['input_raster_2'], parameters['input_raster_3'], 
                         parameters['input_raster_4'], parameters['input_raster_5'], parameters['input_raster_6']]

        intersection_features = []

        for i in range(len(input_rasters)):
            for j in range(i+1, len(input_rasters)):
                # Computar a intersecção entre cada um dos rasters
                alg_params = {
                    'INPUT': [input_rasters[i], input_rasters[j]],
                    'OVERLAY': None,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }
                intersection = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
                
                # add intersection features to the list
                intersection_features.append(intersection)

        # Combinar todas as intersecções em uma geometria de multiplos polígonos
        geom_collection = QgsGeometry().fromMultiPolygon([f.geometry().asPolygon() for f in intersection_features])

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Criar os pontos dentro de cada uma das intersecções

        inside_points = []
        for feat in geom_collection.getFeatures():
            extent = feat.geometry().boundingBox()
            grid = processing.run(
                'native:creategrid',
                {
                    'TYPE': 2,  # Points
                    'EXTENT': extent,
                    'HSPACING': 200,
                    'VSPACING': 200,
                    'CRS': crs,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }
            )['OUTPUT']
            for point in grid.getFeatures():
                if feat.geometry().contains(point.geometry()):
                    inside_points.append(point)

        final_points = QgsVectorLayer('Point?crs={}'.format(crs.authid()), 'final_points', 'memory')
        final_points_data = final_points.dataProvider()
        final_points_data.addFeatures(inside_points)
        final_points.updateExtents()
        outputs['Pontos do grid'] = final_points_data 

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}


        # Filtrando pontos
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['Pontos do grid'],
            'INPUT_FIELDS': [''],
            'OUTPUT': 'TEMPORARY_OUTPUT',
            'OVERLAY': geom_collection,
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FiltrandoPontos'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

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
            'INPUT': outputs['FiltrandoPontos'],
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
            'RASTERCOPY': parameters['mdes'],
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


        results['multi_polygon'] = outputs['Emqz']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Solução complementar do Projeto 1'

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
        return Projeto1SolucaoComplementar()