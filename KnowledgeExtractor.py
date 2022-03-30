import pandas
import xlsxwriter

class KnowledgeExtractor:
    # конструктор
    def __init__(self, inputFilePath, fTableFilePath, kTableFilePath, bTableFilePath, chTableFilePath):
        # запись данных Excel таблиц в поля класса
        self.inputData = pandas.read_excel(inputFilePath, sheet_name="Первичный осмотр").to_dict()
        self.fNameTable = pandas.read_excel(fTableFilePath, sheet_name="Лист1").to_dict()
        self.kNameAndNormTable = pandas.read_excel(kTableFilePath, sheet_name="Лист1").to_dict()
        self.bTimeCharacteristicTable = pandas.read_excel(bTableFilePath, sheet_name="Лист1").to_dict()
        self.chNameAndDigitNormTable = pandas.read_excel(chTableFilePath, sheet_name="Лист1").to_dict()


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

        # ddd
        for validColumnName in validColumns:
            roughLikenessRow = {}
            outItemsKeys = []
            higherItemsKeys = []
            lowerItemsKeys = []
            for index, currentValue in self.inputData[validColumnName].items():
                kNamesAndNorms = self.kNameAndNormTable['название'].values()
                chNameAndDigitNorms = self.chNameAndDigitNormTable['название'].values()

                # если колонка есть в числовых характеристиках
                if validColumnName in chNameAndDigitNorms:
                    minValue = self.kNameAndNormTableDf.loc[self.kNameAndNormTableDf['название'] == validColumnName]['Ниж гр нормы']
                    maxValue = self.kNameAndNormTableDf.loc[self.kNameAndNormTableDf['название'] == validColumnName]['Верх гран нормы']
                    if currentValue < minValue:
                        roughLikenessRow['lower'] = currentValue
                    elif currentValue > minValue:
                        roughLikenessRow['higher'] = currentValue
                    else:
                        continue

                # если колонка есть в качественных характеристиках
                elif validColumnName in kNamesAndNorms:
                    key = [k for k, v in self.kNameAndNormTable['название'].items() if v == validColumnName][0]
                    normValue = self.kNameAndNormTable['Норма (если есть)'][key]
                    if not pandas.notnull(normValue):
                        continue

                    if currentValue not in normValue:
                        outItemsKeys.append(index + 2) # index == 0 это индекс в массиве, +2 что бы он стал как индекс в excel
                    else:
                        continue
                else:
                    break

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

        # workbook = xlsxwriter.Workbook('RoughLikenessTable.xlsx')
        # worksheet = workbook.add_worksheet()
        # worksheet.write(row, column, item)
        # row += 1
        # workbook.close()
    
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
    
    
    def __clearValues(self, data):
        return data.dropna().map(lambda item: item.rstrip()) # удаляет пустые и у оставшихся удаляет пробелы в конце
    
    def __getNanValuesCount(self, data):
        nanCount = 0
        for item in data:
            if not pandas.notnull(item):
                nanCount += 1
        return nanCount