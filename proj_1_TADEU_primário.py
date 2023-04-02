import pandas as pd
from math import sqrt

# ***************************************************
# *********** 1. CARREGAMENTO DOS DADOS *************
# ***************************************************

mds_1 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-NE.tif","MDS_MI_2953-3-NE","gdal")
mds_2 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-NO.tif","MDS_MI_2953-3-NO","gdal")
mds_3 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-SE.tif","MDS_MI_2953-3-SE","gdal")
mds_4 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-3-SO.tif","MDS_MI_2953-3-SO","gdal")
mds_5 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-4-NO.tif","MDS_MI_2953-4-NO","gdal")
mds_6 = iface.addRasterLayer("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - MDS_MI_2953-4-SO.tif","MDS_MI_2953-4-SO","gdal")

pontos_controle = pd.read_csv("C:/Users/etade/OneDrive/Documents/IME/2023.1 4º Ano - Engenharia Cartográfica/Programação Aplicada a Eng Cartográfica/Projeto_1/Edson Tadeu da Silva Pinto - pontos_controle.csv")
pc = list()
for i in range (0, len(pontos_controle)):
    x = pontos_controle['x'][i]
    y = pontos_controle['y'][i]
    z = pontos_controle['z'][i]
    ponto = [x, y, z]
    pc.append(ponto)

camadas = [mds_1, mds_2, mds_3, mds_4, mds_5, mds_6]
nomes = ['MDS_MI_2953-3-NE', 'MDS_MI_2953-3-NO', 'MDS_MI_2953-3-SE', 'MDS_MI_2953-3-SO', 'MDS_MI_2953-4-NO', 'MDS_MI_2953-4-SO']

# ***************************************************
# *** 2. FUNÇÃO QUE CALCULA A ACURÁCIA POSICIONAL ***
# ***************************************************
def acuracia (modelo, pontos, name):
    #Os parâmetros desta função são (modelo digital de superfície, pontos de controle, nome)
    mds = modelo
    pc = pontos
    nome = str(name)

    xmin = mds.extent().xMinimum()
    xmax = mds.extent().xMaximum()
    ymin = mds.extent().yMinimum()
    ymax = mds.extent().yMaximum()
    
    # Erro
    erro = list()
    cont = 0
    for p in range(len(pc[0:])-1):
        if xmin <= float(pc[p+1][0]) <= xmax and ymin <= float(pc[p+1][1]) <= ymax:
            error = 0
            value, result = mds.dataProvider().sample(QgsPointXY(float(pc[p+1][0]),float(pc[p+1][1])), 1)
            error = value - float(pc[p+1][2])
            erro.append(error)
            cont += 1

    # Cálculo do EMQz
    emqz = 0
    for i in erro:
        emqz = emqz + i**2
    emqz = sqrt(emqz/cont)

    if emqz <= 1.67:
        print(f'O Padrão de Exatidão Cartográfica do {nome} é A com Erro Médio Quadrático de {emqz:.3f}')
    elif 1.67 < emqz <= 3.33:
        print(f'O Padrão de Exatidão Cartográfica do {nome} é B com Erro Médio Quadrático de {emqz:.3f}')
    elif 3.33 < emqz <= 4.00:
        print(f'O Padrão de Exatidão Cartográfica do {nome} é C com Erro Médio Quadrático de {emqz:.3f}')
    elif 4.00 < emqz <= 5.00:
        print(f'O Padrão de Exatidão Cartográfica do {nome} é D com Erro Médio Quadrático de {emqz:.3f}')

    # Camada temporária de pontos de controle com o erro
    points = f'Pontos de controle {nome}'
    memoryLayer = QgsVectorLayer("Point?crs=EPSG:31982", points, "memory")  
    dp = memoryLayer.dataProvider() 
    dp.addAttributes([QgsField('erro', QVariant.Double)])
    memoryLayer.updateFields()
    QgsProject.instance().addMapLayer(memoryLayer)

    aux = 0
    for p in range(len(pc[0:])-1):
        if xmin <= float(pc[p+1][0]) <= xmax and ymin <= float(pc[p+1][1]) <= ymax:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(float(pc[p+1][0]),float(pc[p+1][1]))))
            feat.setAttributes([erro[aux]])
            dp.addFeatures([feat])
            memoryLayer.updateExtents()
            aux += 1
            
    #Alteração de simbologia para o peso de erro de cada ponto
    err = QgsProperty()
    err.setField('erro')
    memoryLayer.renderer().symbol().setDataDefinedSize(err)
    memoryLayer.triggerRepaint() 
    iface.layerTreeView().refreshLayerSymbology(memoryLayer.id())

# ***************************************************
# ************ 3. APLICAÇÃO DA FUNÇÃO ***************
# ***************************************************

#Aplicada uma estrutura de repetição que aplica a função criada para todas as camadas carregadas
for i in range (0, len(camadas)):
    acuracia(camadas[i], pc, nomes[i])