import pandas
import xlsxwriter

class KnowledgeExtractor:
    # конструктор
    def __init__(self, inputFilePath, fTableFilePath, kTableFilePath, bTableFilePath, chTableFilePath):
        # запись данных Excel таблиц в поля класса
        self.inputDataDf = pandas.read_excel(inputFilePath, sheet_name="Первичный осмотр")
        self.fNameTableDf = pandas.read_excel(fTableFilePath, sheet_name="Лист1")
        self.kNameAndNormTableDf = pandas.read_excel(kTableFilePath, sheet_name="Лист1")
        self.bTimeCharacteristicTableDf = pandas.read_excel(bTableFilePath, sheet_name="Лист1")
        self.chNameAndDigitNormTableDf = pandas.read_excel(chTableFilePath, sheet_name="Лист1")


    def createRoughLikenessTable(self):
        """
        Шаг № 1 - получение таблицы ROUGH LIKENESS
        """
        worksheetRow = 0
        worksheetColumn = 0
        roughLikenessRow = {}
        validColumns = []
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
            columnData = self.inputDataDf[col]
            isValid = self.__isFillInPercent(columnData, 40)
            if(isValid == True):
                validColumns.append(col)

        dataRowCount = self.inputDataDf.shape[0]

        for dataRow in range(dataRowCount):
            for dataColName in validColumns:
                currentValue = self.inputDataDf[dataColName][dataRow]
                kNamesAndNorms = self.__clearValues(self.kNameAndNormTableDf['название'])
                chNameAndDigitNorms = self.__clearValues(self.chNameAndDigitNormTableDf['название'])

                # если колонка есть в числовых характеристиках
                if dataColName in chNameAndDigitNorms.values:
                    minValue = self.kNameAndNormTableDf.loc[self.kNameAndNormTableDf['название'] == dataColName]['Ниж гр нормы']
                    maxValue = self.kNameAndNormTableDf.loc[self.kNameAndNormTableDf['название'] == dataColName]['Верх гран нормы']
                    if currentValue < minValue:
                        roughLikenessRow['lower'] = currentValue
                    elif currentValue > minValue:
                        roughLikenessRow['higher'] = currentValue
                    else:
                        continue

                # если колонка есть в качественных характеристиках
                elif dataColName in kNamesAndNorms.values:
                    normValue = self.kNameAndNormTableDf.loc[self.kNameAndNormTableDf['название'] == dataColName]['Норма (если есть)']
                    if currentValue in normValue:
                        roughLikenessRow['Out'] = col
                    else:
                        continue

                roughLikenessRow['obsNm'] = col
                roughLikenessRow['Q-вне'] = len(roughLikenessRow['Out'])
                roughLikenessRow['Q-high'] = len(roughLikenessRow['higher'])
                roughLikenessRow['Q-low'] = len(roughLikenessRow['lower'])
        
        print(roughLikenessRow)
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
        isNullCount = data.isna().sum()
        precentCount = round(precent * allCount / 100)
        # не меннее precent заполнено
        return (allCount - isNullCount) > precentCount
    
    
    def __clearValues(self, data):
        return data.dropna().map(lambda item: item.rstrip()) # удаляет пустые и у оставшихся удаляет пробелы в конце