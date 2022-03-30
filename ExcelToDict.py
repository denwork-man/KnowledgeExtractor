import pandas as pd
import numpy as np
import json as jn

from functools import singledispatch

@singledispatch
def GetStructuredData(inputDF: pd.DataFrame) -> dict:
    validColumns = []

    objects = {}
    counter = 0
    for item in inputDF.columns:
        attr_name = item.strip()
        # print(type(item), " : ", attr_name)
        validColumns.append(item)
        # print(inputDF[item][0])

    for row in inputDF.index:

        atributes: dict
        atributes = {}
        for item in validColumns:
            attr_name = item.strip()
            # if isinstance(inputDF[item][row], float):
            print("\t\t", type(inputDF[item][row]), " : ", inputDF[item][row], pd.isna(inputDF[item][row]))

            value = int(0)
            if not pd.isna(inputDF[item][row]):

                if isinstance(inputDF[item][row], np.float64):
                    # print(type(inputDF[item][row]), ': ', inputDF[item][row])
                    value = inputDF[item][row].item()
                    print(type(value), ': ', value)
                else:
                    if isinstance(inputDF[item][row], np.int64):
                        value = inputDF[item][row].item()
                        print(type(value), ': ', value)
                        # print(type(inputDF[item][row]), ': ', inputDF[item][row])
                    else:
                        value = inputDF[item][row]
                if isinstance(value, str):
                    value = value.strip()
                    listt = value.split('; ')
                    if len(listt) > 1:
                        value = listt
                    if isinstance(value, list):
                        # print('\t\tLIST ', type(value))
                        for i in range(0, len(value)):
                            # print('\t\t\t\t ', i, ') "', value[i],'"')
                            value[i] = value[i].strip()
                            # print('\t\t\tAfterStrip\n\t\t\t\t_', i, ') "', value[i],'"')

                # print('__\t',type(value), ': ', value)
                atributes[attr_name] = value

        objects[str(row + 1)] = atributes
    return objects

@GetStructuredData.register
def _(inputFile: str) -> dict:
    inputDF = pd.read_excel(inputFile, sheet_name="Первичный осмотр")
    return GetStructuredData(inputDF)

"""
GetStructureCount возвращает dict подобный по виду и структуре, тому, который возвращает GetStructuredData.
Возвращаемый dict содержит в себе элементы 'ключ':'значение', где 'ключ' -- название столбца, 
'значение' -- количество значений в нём 
"""
def GetStructureCount(inputDF: pd.DataFrame) -> dict:
    validColumns ={}
    for item in inputDF.count().index:
        attr_name = item.strip()
        # print(type(item), " : ", attr_name)
        validColumns[attr_name] = int(inputDF.count()[item])
    return validColumns


def testFunctionsAbove(inpFileName : str = "C:\\Users\\DinDin\\Downloads\\Telegram Desktop\\Шалфеева_файлы\\примерИсхДан (для ВГу).xls"):
    inpDataFrame = pd.read_excel(inpFileName, sheet_name="Первичный осмотр")
    array = GetStructuredData(inpDataFrame)

    json_str = jn.dumps(array)
    print(json_str)

    array_cnt = GetStructureCount(inpDataFrame)
    json_str = jn.dumps(array_cnt)
    print(json_str)
