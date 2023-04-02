
# **************************************************
# ********* 1. CARREGAMENTO DOS ARQUIVOS ***********
# **************************************************

mds_1 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-NE.tif","MDS_MI_2953-3-NE","gdal")
mds_2 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-NO.tif","MDS_MI_2953-3-NO","gdal")
#mds_3 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-SE.tif","MDS_MI_2953-3-SE","gdal")
#mds_4 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-SO.tif","MDS_MI_2953-3-SO","gdal")
#mds_5 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-4-NO.tif","MDS_MI_2953-4-NO","gdal")
#mds_6 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-4-SO.tif","MDS_MI_2953-4-SO","gdal")

# **************************************************
# ***** 2. OBTENÇÃO DOS LIMITES DOS RASTERS ********
# **************************************************

xmin_1 = mds_1.extent().xMinimum()
xmax_1 = mds_1.extent().xMaximum()
ymin_1 = mds_1.extent().yMinimum()
ymax_1 = mds_1.extent().yMaximum()

xmin_2 = mds_2.extent().xMinimum()
xmax_2 = mds_2.extent().xMaximum()
ymin_2 = mds_2.extent().yMinimum()
ymax_2 = mds_2.extent().yMaximum()

# **************************************************
# ***** 3. CRIAÇÃO DOS PONTOS DE SOBREPOSIÇÃO ******
# **************************************************

memoryLayer = QgsVectorLayer("Point?crs=EPSG:31982", "pontos de sobreposição", "memory")  
dp = memoryLayer.dataProvider() 
dp.addAttributes([QgsField("erro", QVariant.Double)])
memoryLayer.updateFields()
QgsProject.instance().addMapLayer(memoryLayer)

p_erro = list()
if xmin_1 <= xmin_2:
    if ymin_1 <= ymin_2:
        erro = list()
        aux = 0
        x = xmin_2
        while x <= xmax_1:
            y = ymin_2
            while y <= ymax_1:
                dif = 0
                value1, result1 = mds_1.dataProvider().sample(QgsPointXY(x,y), 1)
                value2, result2 = mds_2.dataProvider().sample(QgsPointXY(x,y), 1)
                if result1 == True and result2 == True:
                    dif = value1 - value2
                    erro.append(dif)
                    p_erro.append(dif)
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
                    feat.setAttributes([erro[aux]])
                    dp.addFeatures([feat])
                    memoryLayer.updateExtents()
                    aux += 1
                y += 200
            x += 200
            
    if ymin_2 <= ymin_1:
        erro = list()
        aux = 0
        x = xmin_2
        while x <= xmax_1:
            y = ymin_1
            while y <= ymax_2:
                dif = 0
                value1, result1 = mds_1.dataProvider().sample(QgsPointXY(x,y), 1)
                value2, result2 = mds_2.dataProvider().sample(QgsPointXY(x,y), 1)
                if result1 == True and result2 == True:
                    dif = value1 - value2
                    erro.append(dif)
                    p_erro.append(dif)
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
                    feat.setAttributes([erro[aux]])
                    dp.addFeatures([feat])
                    memoryLayer.updateExtents()
                    aux += 1
                y += 200
            x += 200

if xmin_2 <= xmin_1:
    if ymin_1 <= ymin_2:
        erro = list()
        aux = 0
        x = xmin_1
        while x <= xmax_2:
            y = ymin_2
            while y <= ymax_1:
                dif = 0
                value1, result1 = mds_1.dataProvider().sample(QgsPointXY(x,y), 1)
                value2, result2 = mds_2.dataProvider().sample(QgsPointXY(x,y), 1)
                if result1 == True and result2 == True:
                    dif = value1 - value2
                    erro.append(dif)
                    p_erro.append(dif)
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
                    feat.setAttributes([erro[aux]])
                    dp.addFeatures([feat])
                    memoryLayer.updateExtents()
                    aux += 1
                y += 200
            x += 200

    if ymin_2 <= ymin_1:
        erro = list()
        aux = 0
        x = xmin_1
        while x <= xmax_2:
            y = ymin_1
            while y <= ymax_2:
                dif = 0
                value1, result1 = mds_1.dataProvider().sample(QgsPointXY(x,y), 1)
                value2, result2 = mds_2.dataProvider().sample(QgsPointXY(x,y), 1)
                if result1 == True and result2 == True:
                    dif = value1 - value2
                    erro.append(dif)
                    p_erro.append(dif)
                    feat = QgsFeature()
                    feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
                    feat.setAttributes([erro[aux]])
                    dp.addFeatures([feat])
                    memoryLayer.updateExtents()
                    aux += 1
                y += 200
            x += 200

#Alteração de simbologia para o peso de erro de cada ponto
err = QgsProperty()
err.setField('erro')
memoryLayer.renderer().symbol().setDataDefinedSize(err)
memoryLayer.triggerRepaint() 
iface.layerTreeView().refreshLayerSymbology(memoryLayer.id())

# ***************************************************
# *** 4. FUNÇÃO QUE CALCULA A ACURÁCIA RELATIVA *****
# ***************************************************

# Cálculo do EMQz
emqz = 0
for i in p_erro:
    emqz = emqz + i**2
emqz = sqrt(emqz/len(p_erro))

if emqz <= 1.67:
    print(f'O Padrão de Exatidão Cartográfica é A com Erro Médio Quadrático de {emqz:.3f}')
elif 1.67 < emqz <= 3.33:
    print(f'O Padrão de Exatidão Cartográfica é B com Erro Médio Quadrático de {emqz:.3f}')
elif 3.33 < emqz <= 4.00:
    print(f'O Padrão de Exatidão Cartográfica é C com Erro Médio Quadrático de {emqz:.3f}')
elif 4.00 < emqz <= 5.00:
    print(f'O Padrão de Exatidão Cartográfica é D com Erro Médio Quadrático de {emqz:.3f}')