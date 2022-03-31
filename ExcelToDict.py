import pandas as pd
import numpy as np
import json as jn

from functools import singledispatch

@singledispatch
def GetStructuredData(inputDF: pd.DataFrame) -> dict:
    validColumns = list(filter(lambda item: 'Unnamed' not in item, inputDF.columns.to_list()))
    objects = {}
    counter = 0

    for row in inputDF.index:
        attributes = {}

        for item in validColumns:
            attr_name = item.strip()
            value = int(0)

            elem = inputDF[item][row]

            # пропускаем пустые значения
            if pd.isna(elem):
                continue

            # если значение числовое
            if isinstance(elem, np.float64) or isinstance(elem, np.int64):
                value = elem.item()

            # если значение строковое
            elif isinstance(elem, str):
                listt = list(map(lambda item: item.strip(), elem.split(';')))
                if len(listt) > 1:
                    value = listt
                elif len(listt) == 1:
                    value = listt[0]
            
            # если значение другого типа
            else:
                value = elem

            attributes[attr_name] = value

        objects[str(row + 1)] = attributes
    print(objects)
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
    validColumns = {}
    for item in inputDF.count().index:
        if 'Unnamed' in item:
            continue

        attr_name = item.strip()
        validColumns[attr_name] = int(inputDF.count()[item])
    
    return validColumns


def testFunctionsAbove(inpFileName : str = "DataSets\\Пример_исх_данных_для_ВГУ.xlsx"):
    inpDataFrame = pd.read_excel(inpFileName, sheet_name="Первичный осмотр")
    array = GetStructuredData(inpDataFrame)

    json_str = jn.dumps(array)
    print(json_str)

    array_cnt = GetStructureCount(inpDataFrame)
    json_str = jn.dumps(array_cnt)
    print(json_str)
