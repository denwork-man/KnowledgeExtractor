import pandas

class KnowledgeExtractor:
    # конструктор
    def __init__(self, inputFilePath, fTableFilePath, kTableFilePath, bTableFilePath, chTableFilePath):
        # запись данных Excel таблиц в поля класса
        inputData = pandas.read_excel(inputFilePath, sheet_name="Первичный осмотр").to_dict()
        fTable = pandas.read_excel(fTableFilePath, sheet_name="Лист1").to_dict()
        kTable = pandas.read_excel(kTableFilePath, sheet_name="Лист1").to_dict()
        bTable = pandas.read_excel(bTableFilePath, sheet_name="Лист1").to_dict()
        chTable = pandas.read_excel(chTableFilePath, sheet_name="Лист1").to_dict()
        
        self.inputData = self.__trimDictKeys(inputData)
        self.fNameTable = self.__trimDictKeys(fTable)
        self.kNameAndNormTable = self.__trimDictKeys(kTable)
        self.bTimeCharacteristicTable = self.__trimDictKeys(bTable)
        self.chNameAndDigitNormTable = self.__trimDictKeys(chTable)


    def createRoughLikenessTable(self):
        """
        Шаг № 1 - получение таблицы ROUGH LIKENESS
        """
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

            kNamesAndNorms = self.kNameAndNormTable['Название'].values()
            chNameAndDigitNorms = self.chNameAndDigitNormTable['Название'].values()

            # если колонка есть в числовых характеристиках
            if validColumnName in chNameAndDigitNorms:
                for index, currentValue in self.inputData[validColumnName].items():
                    key = [k for k, v in self.chNameAndDigitNormTable['Название'].items() if v == validColumnName][0]
                    
                    minValue = self.chNameAndDigitNormTable['Ниж гр нормы'][key]
                    maxValue = self.chNameAndDigitNormTable['Верх гран нормы'][key]

                    if currentValue < minValue:
                        lowerItemsKeys.append(currentValue)
                    elif currentValue > minValue:
                        higherItemsKeys.append(currentValue)
                    else:
                        continue

            # если колонка есть в качественных характеристиках
            elif validColumnName in kNamesAndNorms:
                for index, currentValue in self.inputData[validColumnName].items():
                    key = [k for k, v in self.kNameAndNormTable['Название'].items() if v == validColumnName][0]
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

            if len(outItemsKeys) != 0 or len(higherItemsKeys) != 0 or len(lowerItemsKeys) != 0:
                roughLikenessRow['ObsNm'] = validColumnName
                roughLikenessRow['Out'] = ','.join(map(str, outItemsKeys)) or ''
                roughLikenessRow['Q-Out'] = len(outItemsKeys) or ''
                roughLikenessRow['Higher'] = ','.join(map(str, higherItemsKeys)) or ''
                roughLikenessRow['Q-Higher'] = len(higherItemsKeys) or ''
                roughLikenessRow['Lower'] = ','.join(map(str, lowerItemsKeys)) or ''
                roughLikenessRow['Q-Lower'] = len(lowerItemsKeys) or ''
                roughLikenessData.append(roughLikenessRow)

        print(roughLikenessData)
        self.roughLikenessTable = roughLikenessData
        self.__listOfDictToExcel('Output\\RoughLikenessTable.xlsx', roughLikenessData)
        
    
    def createSplittingUnNormTable(self):
        """
        Шаг № 2
        """
        pass


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