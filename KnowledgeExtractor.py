import pandas
from loguru import logger


class KnowledgeExtractor:
    # конструктор
    def __init__(self, inputFilePath, fTableFilePath, kTableFilePath, bTableFilePath, chTableFilePath):
        try:
            # запись данных Excel таблиц в поля класса
            self.inputData = self.__importData(inputFilePath)
            self.fNameTable = self.__importData(fTableFilePath)
            self.kNameAndNormTable = self.__importData(kTableFilePath)
            self.bTimeCharacteristicTable = self.__importData(bTableFilePath)
            self.chNameAndDigitNormTable = self.__importData(chTableFilePath)
            
            logger.info(f'Входные файлы успешно считаны')
        except BaseException as e:
            logger.exception(f'Во время чтения данных с файлов произошла ошибка')


    def createRoughLikenessTable(self):
        """ Шаг № 1 - получение таблицы ROUGH LIKENESS """
        try:
            worksheetRow = 0
            worksheetColumn = 0
            validColumns = []
            roughLikenessData = []
            aviableColumns = [
                "БольЖив.Локализ",
                "Боль.Интенсивн",
                "Рвота.Характеристики",
                "Температура тела",
                "ВлажностьЯзыка",
                "Налет на языке",
                "ПрочиеЖКТжалобы",
                "Чувствит-ть при пальп",
                "Чувствит-ть.Локализ",
                "УЗИ-СтенкиЖП, мм",
                "Лечен.Эфф",
                "Гематокрит, %",
                "Лейкоциты, 10^9/л",
                "Состояние",
                "Билирубин общ, мкмоль/л",
                "Тошнота.Время",
            ]

            # отбор тех колонок у которых значений заполнено более 40%
            for col in aviableColumns:
                if col not in self.inputData.keys():
                    logger.warning(f"Во входных данных не была найдена колонка: \"{col}\". Проверьте ее существование и корректность названия.")
                    continue

                columnData = self.inputData[col]
                isValid = self.__isFillInPercent(columnData.values(), 40)
                if(isValid == True):
                    validColumns.append(col)

            # обработка колонок
            for validColumnName in validColumns:
                roughLikenessRow = {}
                outItemsKeys = []
                higherItemsKeys = []
                lowerItemsKeys = []

                if 'Название' not in self.kNameAndNormTable.keys():
                    logger.warning(f"Завершение работы. В таблице \"Таблица_К_имен_и_норм\" не была найдена колонка: \"Название\". Проверьте ее существование и корректность написания.")
                    return

                if 'Название' not in self.chNameAndDigitNormTable.keys():
                    logger.warning(f"Завершение работы. В таблице \"Таблица_Ч_имен_и_числовых_норм\" не была найдена колонка: \"Название\". Проверьте ее существование и корректность написания.")
                    return

                kNamesAndNorms = self.kNameAndNormTable['Название'].values()
                chNameAndDigitNorms = self.chNameAndDigitNormTable['Название'].values()

                # если колонка есть в числовых характеристиках
                if validColumnName in chNameAndDigitNorms:
                    for index, currentValue in self.inputData[validColumnName].items():
                        key = [k for k, v in self.chNameAndDigitNormTable['Название'].items() if v == validColumnName][0]
                        
                        if 'Ниж гр нормы' not in self.chNameAndDigitNormTable.keys():
                            logger.warning(f"Завершение работы. В таблице \"Таблица_Ч_имен_и_числовых_норм\" не была найдена колонка: \"Ниж гр нормы\". Проверьте ее существование и корректность написания.")
                            return

                        if 'Верх гран нормы' not in self.chNameAndDigitNormTable.keys():
                            logger.warning(f"Завершение работы. В таблице \"Таблица_Ч_имен_и_числовых_норм\" не была найдена колонка: \"Верх гран нормы\". Проверьте ее существование и корректность написания.")
                            return

                        minValue = self.chNameAndDigitNormTable['Ниж гр нормы'][key]
                        maxValue = self.chNameAndDigitNormTable['Верх гран нормы'][key]

                        if not pandas.notna(normValue) or not pandas.notna(currentValue):
                            continue
                        
                        if isinstance(currentValue, str) and 'нет' in currentValue.lower():
                            continue
                        
                        currentValue = self.__validateDigitValue(currentValue)
                        minValue = self.__validateDigitValue(minValue)
                        maxValue = self.__validateDigitValue(maxValue)

                        if currentValue < minValue:
                            lowerItemsKeys.append(index + 2)
                        elif currentValue > maxValue:
                            higherItemsKeys.append(index + 2)
                        else:
                            continue

                # если колонка есть в качественных характеристиках
                elif validColumnName in kNamesAndNorms:
                    for index, currentValue in self.inputData[validColumnName].items():
                        key = [k for k, v in self.kNameAndNormTable['Название'].items() if v == validColumnName][0]
                       
                        if 'Норма (если есть)' not in self.kNameAndNormTable.keys():
                            logger.warning(f"Завершение работы. В таблице \"Таблица_К_имен_и_норм\" не была найдена колонка: \"Норма (если есть)\". Проверьте ее существование и корректность написания.")
                            return

                        normValue = self.kNameAndNormTable['Норма (если есть)'][key]
                       
                        if not pandas.notna(normValue) or not pandas.notna(currentValue):
                            continue

                        if currentValue not in normValue:
                            outItemsKeys.append(index + 2) # index == 0 это индекс в массиве, +2 что бы он стал как индекс в excel
                        else:
                            continue

                # если нет ни в качественных ни в числовых характеристиках
                else:
                    continue

                # если что-то собрали
                if len(outItemsKeys) != 0 or len(higherItemsKeys) != 0 or len(lowerItemsKeys) != 0:
                    roughLikenessRow['ObsNm'] = validColumnName
                    roughLikenessRow['Out'] = ','.join(map(str, outItemsKeys)) or ''
                    roughLikenessRow['Q-Out'] = len(outItemsKeys) or ''
                    roughLikenessRow['Higher'] = ','.join(map(str, higherItemsKeys)) or ''
                    roughLikenessRow['Q-Higher'] = len(higherItemsKeys) or ''
                    roughLikenessRow['Lower'] = ','.join(map(str, lowerItemsKeys)) or ''
                    roughLikenessRow['Q-Lower'] = len(lowerItemsKeys) or ''
                    roughLikenessData.append(roughLikenessRow)

            self.__printTable(roughLikenessData)

            self.roughLikenessTable = roughLikenessData

            self.__listOfDictToExcel('Output\\RoughLikenessTable.xlsx', roughLikenessData)
            
            logger.info(f'Таблица ROUGH LIKENESS успешно сформирована')
        except BaseException as e:
            logger.exception(f'Во время получение таблицы ROUGH LIKENESS произошла ошибка')
        
    
    def createSplittingUnNormTable(self):
        """ Шаг № 2 """
        # Находим наиболее рейтинговый признак  
        rowMaxQOut, rowMaxNumOut = self.__getRowMaxQOut()
        chNameAndDigitNorms = self.chNameAndDigitNormTable['Название'].values()
        kNamesAndNorms = self.kNameAndNormTable['Название'].values()

        if rowMaxQOut == {}:
            return

        if rowMaxQOut['ObsNm'] in kNamesAndNorms: # Если признак качественный
            """ Шаг № 2.1 """
            try:
                CategoriesClustersData = []
                for nRowQQut in rowMaxQOut['Out'].split(','):  # Для каждой строки
                    categories = self.inputData[rowMaxQOut['ObsNm']][int(nRowQQut)-2]
                    
                    for categorie in categories.split(';'): # Для каждого значения из перечня

                        if len(CategoriesClustersData) == 0: # Если таблица пуста
                            self.__addRowCategoriesClustersData(CategoriesClustersData,categorie,nRowQQut) # Добавь значение

                        else:   # Иначе ищи среди существующих значений
                            isFind = False
                            for nCategoriesRow in range(len(CategoriesClustersData)):
                                if CategoriesClustersData[nCategoriesRow]["Val"] == categorie: # Если нашел совпадение
                                    CategoriesClustersData[nCategoriesRow]["Out"] = CategoriesClustersData[nCategoriesRow]["Out"] + "," + nRowQQut # Допиши номер строки
                                    CategoriesClustersData[nCategoriesRow]["Count"] += 1 # Увеличь счетчик
                                    isFind = True 
                                    break
                            if not isFind: # Если не нашел
                                self.__addRowCategoriesClustersData(CategoriesClustersData, categorie, nRowQQut) # Добавь значение

                for CategoriesClustersRow in CategoriesClustersData: # Для каждого значения категории
                    CategoriesClustersRow["%"] = CategoriesClustersRow["Count"] / len(rowMaxQOut['Out'].split(',')) * 100 # Рассчитай % вхождения в выборку

                self.__printTable(CategoriesClustersData) # Выведи таблицу
                self.CategoriesClustersTable = CategoriesClustersData # Сохрани таблицу
                self.__listOfDictToExcel('Output\\SplittingUnNormCategories.xlsx', CategoriesClustersData) # Выгрузи таблицу

                logger.info(f'Таблица SplittingUnNormCategories успешно сформирована (2.1)')
            except BaseException as e:
                logger.exception(f'Во время получение таблицы SplittingUnNormCategories произошла ошибка (2.1)')

        if rowMaxNumOut == {}:
            return

        if rowMaxNumOut['ObsNm'] in chNameAndDigitNorms: # Если признак числовой
            """ Шаг № 2.2 """
            try:
                NumbersClustersData = []
                validArray = []
                twoPercArray = []
                halfPercArray = []
                plusHalfPercArray = []
                borderValue = 0
                higherArray = rowMaxNumOut['Higher'].split(',')
                lowerArray = rowMaxNumOut['Lower'].split(',')

                key = [k for k, v in self.chNameAndDigitNormTable['Название'].items() if v == rowMaxNumOut['ObsNm']][0]

                if len(lowerArray) > len(higherArray):
                    validArray = lowerArray
                    borderValue = self.chNameAndDigitNormTable['Ниж гр нормы'][key]
                else:
                    validArray = higherArray
                    borderValue = self.chNameAndDigitNormTable['Верх гран нормы'][key]
                
                for elem in validArray:
                    number = self.inputData[rowMaxNumOut['ObsNm']][int(elem) - 2]
                    if not pandas.notna(number):
                        continue

                    twoPercBorder = borderValue * 0.02
                    halfBorder = borderValue * 0.5

                    number = self.__validateDigitValue(number)
                    borderValue = self.__validateDigitValue(borderValue)

                    if number > borderValue and number <= borderValue + twoPercBorder:
                        twoPercArray.append(number)
                    elif number > borderValue + twoPercBorder and number <= borderValue + halfBorder:
                        halfPercArray.append(number)
                    elif number > borderValue + halfBorder:
                        plusHalfPercArray.append(number)

                val = rowMaxNumOut['Q-Higher'] + rowMaxNumOut['Q-Lower']

                self.__createNumbersClustersData(NumbersClustersData, '> Граница, но <= Граница + 2%', twoPercArray, val)
                self.__createNumbersClustersData(NumbersClustersData, '> Граница + 2%, но <= Граница + 50%', halfPercArray, val)
                self.__createNumbersClustersData(NumbersClustersData, '> Граница + 50%', plusHalfPercArray, val)

                self.__printTable(NumbersClustersData)

                self.numbersClusterTable = NumbersClustersData
                self.__listOfDictToExcel('Output\\SplittingUnNumbersClusters.xlsx', NumbersClustersData)

                logger.info(f'Таблица SplittingUnNumbersClusters успешно сформирована (2.2)')
            except BaseException as e:
                logger.exception(f'Во время получение таблицы SplittingUnNumbersClusters произошла ошибка (2.2)')
		

    def __validateDigitValue(self, digit) -> float:
        if isinstance(digit, (str)):
            # Если значение строковое типа '3-4', то возвращаю наибольшее значение
            if '-' in digit:
                splitted = digit.split('-')
                return float(self.__validateDigitValue(splitted[0])) if float(self.__validateDigitValue(splitted[0])) >= float(self.__validateDigitValue(splitted[1])) else float(self.__validateDigitValue(splitted[1]))
            
            # Если значение строковое типа '3,5'
            elif ',' in digit:
                return float(digit.replace(',', '.'))

            # Если значение строковое типа '3'
            else:
                return float(digit)
        elif isinstance(digit, (int, float)):
            return float(digit)
        else:
            return float(digit)


    def __isFillInPercent(self, data, precent):
        allCount = len(data)
        isNullCount = self.__getNanValuesCount(data)
        precentCount = round(precent * allCount / 100)
        # не меннее precent заполнено
        return (allCount - isNullCount) > precentCount
    
    
    def __getNanValuesCount(self, data):
        nanCount = 0
        for item in data:
            if not pandas.notnull(item):
                nanCount += 1
        return nanCount


    def __listOfDictToExcel(self, filePath, data):
        output = pandas.DataFrame(data)
        output.to_excel(filePath, index=False)


    def __trimDictKeys(self, dictData: dict) -> dict:
        newDict = {}
        for dictKey, dictValues in dictData.items():
            newDict[dictKey.strip()] = dictValues
        
        return newDict


    def __importData(self, filePath: str) -> dict:
        data = pandas.read_excel(filePath).to_dict()
        resultDict = self.__trimDictKeys(data)
        return resultDict


    def __getRowMaxQOut(self):
        maxQOut = 0
        rowMaxQOut = {}
        maxNumOut = 0
        rowMaxNumOut = {}
        for row in self.roughLikenessTable:

            # Для численных значений у которых Q-Out отсутствует
            if row['Q-Out'] == '':
               qLower = 0 if row['Q-Lower'] == '' else row['Q-Lower']
               qHigher = 0 if row['Q-Higher'] == '' else row['Q-Higher']
               qSum = qHigher + qLower
               if int(qSum) > int(maxNumOut):
                   maxNumOut = qSum
                   rowMaxNumOut = row

            # Для качественных значений у которых есть Q-Out
            elif row['Q-Out'] > maxQOut:
               maxQOut = row['Q-Out']
               rowMaxQOut = row

        return rowMaxQOut, rowMaxNumOut


    def __printTable(self,table):
        for nomRow in range(len(table)):
            print("{0}:{1}".format(nomRow,table[nomRow]))
			

    def __addRowCategoriesClustersData(self, CategoriesClustersData, categorie, nRowQQut):
        clustersRow = { "Val":categorie,
                        "Out":nRowQQut,
                        "Count":1,
                        "%":0,}
        CategoriesClustersData.append(clustersRow)


    def __createNumbersClustersData(self, NumbersClustersData, val, array, precentVal):
        NumbersClustersData.append({
            'Val': val, 
            'Out':','.join(map(str, array)) or '',
            'Count':len(array), 
            '%' : round(len(array) / (precentVal) * 100, 2)
        })