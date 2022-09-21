#!/usr/bin/python
import sys
import os
import argparse
from KnowledgeExtractor import KnowledgeExtractor as KExtractor
from loguru import logger

def initArguments():
    """
    Установка аргументов для путей к таблицам
    """
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-?',        help='Вывод справочной информации о доступных параметрах', action='help')
    argParser.add_argument('-DEBUG',    help='Указание для вывода отладочной информации во время выполнения', type=bool, default=False, required=False)
    argParser.add_argument('-v',
                           '--verbose', help='Уровень вывода сообщений (либо "DEBUG", либо не указывать)', type=str, default='INFO')
    argParser.add_argument('-f_table',  help='Путь до Excel таблицы Ф имен',                    type=str, required=False, default=".\\DataSets\\Таблица_Ф_имен.xlsx")
    argParser.add_argument('-k_table',  help='Путь до Excel таблицы К имен и норм',             type=str, required=False, default=".\\DataSets\\Таблица_К_имен_и_норм.xlsx")
    argParser.add_argument('-b_table',  help='Путь до Excel таблицы Б временных характеристик', type=str, required=False, default=".\\DataSets\\Таблица_В_временных_характеристик.xlsx")
    argParser.add_argument('-ch_table', help='Путь до Excel таблицы Ч имен и числовых норм',    type=str, required=False, default=".\\DataSets\\Таблица_Ч_имен_и_числовых_норм.xlsx")
    argParser.add_argument('-input',    help='Путь до Excel таблицы исходных данных',           type=str, required=True)
    argParser.add_argument('-outdir',   help='Путь до директории вывода',                       type=str, required=False, default="Output")
    args = argParser.parse_args()
    return args

# TODO не забыть поменять пути к файлам
def getFullPath(fileName):
    return f"{os.getcwd()}\\{fileName}"


def isValidResourcesPath(args):
    """
    Валидация существования файлов таблиц Excel
    """

    pathes = [args.f_table, args.k_table, args.b_table, args.ch_table, args.input]

    for filePath in pathes:
        exist = os.path.exists(f"{getFullPath(filePath)}")
        if(exist == False):
            logger.warning(f"Не найден Excel файл по переданному пути: {filePath}")
            return False

        _, ext = os.path.splitext(filePath)
        if(ext != '.xlsx' and  ext != '.xls'):
            logger.warning("Расширение файла должно быть .xlsx или .xls")
            return False
    
    return True


# Точка входа приложения
if __name__ == '__main__':
    try:
        args = initArguments()
        logger.info(f'KnowledgeExtractor запускается. Сейчас всё начнётся.')

        if isinstance(args.verbose, (str)) and args.verbose in "DEBUG":
            logger.remove()
            logger.add(sys.stdout, level="DEBUG")
        else:
            logger.remove()
            logger.add(sys.stdout, level=args.verbose)
            logger.info(f'Включен вывод {args.verbose} сообщений')

        logger.debug(f'Включен вывод сообщений отладки')
        isValidArgs = isValidResourcesPath(args)
        if isValidArgs == False:
            logger.warning("Args is not valid")
            exit()

        kExtractor = KExtractor(
            inputFilePath=getFullPath(args.input),
            fTableFilePath=getFullPath(args.f_table),
            kTableFilePath=getFullPath(args.k_table),
            bTableFilePath=getFullPath(args.b_table),
            chTableFilePath=getFullPath(args.ch_table),
        )
        # Шаг № 1
        logger.info(f"Шаг №1")
        kExtractor.createRoughLikenessTable()
        
        # Шаг № 2
        logger.info(f"Шаг №2")
        kExtractor.createSplittingUnNormTable()

        # Шаг № 3
        logger.info(f"Шаг №3")
        kExtractor.createVariantTables()
        logger.success(f"Успешно завершено")
    except SystemExit as e:
        # игнор исключения (игнор так как метод exit() выкидывает эту ошибку при завершении python скрипта)
        logger.debug(f'Выход')
        pass
    except BaseException as e:
        logger.exception(f'Во время работы приложения произошла непредвиденная ошибка')


# Строка запуска программы в консоли
# python App.py -f_table DataSets\Таблица_Ф_имен.xlsx -k_table DataSets\Таблица_К_имен_и_норм.xlsx -b_table DataSets\Таблица_В_временных_характеристик.xlsx -ch_table DataSets\Таблица_Ч_имен_и_числовых_норм.xlsx -input DataSets\Пример_исх_данных_для_ВГУ_v2.xls