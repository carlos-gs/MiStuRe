#!/usr/bin/env python
# encoding: utf-8
'''
GitLogAnaly -- Analysis of str with content of "git log" command over a repository

GitLogAnaly is a description

It defines classes_and_methods

@author:     Carlos González Sesmero.

@copyright:  2014.

@license:    license

@contact:    gcarlosonza@gmail.com
@deffield    updated: Updated
'''

import datetime
import os
import re

import entities.student as Mstud

# ATRIBUTOS DEL MODULO.
# NUMCOMMITS = 0
# PARAMETROS PROPIOS P2 PTAVI
NMINCOMMITS = 4
NEXPECTEDCOMMITS = 5
MINLENGTH = 20  # MIN CHARACTERS IN A COMMIT'S DESCRIPTION

DMONTH = {}
MONTH = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dic')
numonths = tuple(range(1, len(MONTH) + 1))
for i in range(len(MONTH)):
    DMONTH[MONTH[i]] = numonths[i]


# PATTERNS.
GITLOG_PATTERN = ''.join([
    r"^commit\s+(?P<shacode>\S+)$\s",  # patrones ideados para flag re.M puesto
    r"^Author:\s+(?P<Author>.+)$\s",
    r"^Date:\s+(?P<Datetime>.+)$\s",
    r"^\s+(?P<Description>.+)$\s+"
])
DATETIME_PATTERN = r"^\w{3} (?P<month>\w{3}) (?P<day>\d{1,2}) (?P<hour>\d{2}):" + \
                   r"(?P<min>\d{2}):(?P<sec>\d{2}) (?P<year>\d{4})"
DESC_PATTERN = '|'.join([
    r"(calc)",
    r"(sum)|(rest)|(mult)|(div)",
    r"(commit)|(primer)|(DEFINITIVA)",
    r"(objeto)|(orientado)|(object)|(\s+o.o.\s+)",
    r"(herenc)|(herit)|(hij)",
    r"(csv)|(fich)|(comma.+sepparated.+value.+)"
])  # encouraged flags re.I Ignored Case


def mainGLA(gitlogstr):
    """
        With string s given that contains git log stdour, analize it.
    """
    outputstr = ''
    # Extract data from info into list of tuples, if commit pattern find commit with correct format
    commitsdata = re.findall(GITLOG_PATTERN, gitlogstr,
                             re.M)  # importante re.M para patrones multiline
    # Commitsdata list of (shacode, author, datetime, description)
    outputstr += ncommitsAnaly(commitsdata)
    outputstr += datesAnaly(commitsdata)
    outputstr += commentsAnaly(commitsdata)

    return outputstr


def ncommitsAnaly(commitslist):
    """
        Evaluate commit's account as function of specify account
        of commits of PTAVI code..
    """
    outputstr = ''
    numcommits = len(commitslist)
    outputstr += 'Cantidad de commits: ' + str(numcommits) + '\n'
    if (numcommits >= NMINCOMMITS):
        notacom = min((5 * numcommits / NMINCOMMITS), 10)
    else:
        notacom = 0
    outputstr += 'Evaluacion: ' + str(notacom) + '/10'
    outputstr += '\n'
    return outputstr


def commentsAnaly(commitslist):
    """
        Evaluate commits' description as function of RELEVANT WORDS used
        on commits of PTAVI code..
        Also evaluates use of DISENCOURAGED WORDS.
    """
    outputstr = ''
    nmatch = 0
    nbadlen = 0
    commitstr = ''
    for com in commitslist:
        nm = re.findall(DESC_PATTERN, com[3],
                        re.I)  # 3 is descripcion of commit
        nmatch += len(nm)
        if len(com[3]) < MINLENGTH:
            nbadlen += 1
            commitstr += ('\t\"' + com[3] + '\"\n')
    outputstr += 'Localizadas ' + str(
        nmatch) + ' cadenas relevantes en las descripciones\n'
    outputstr += 'Hay ' + str(nbadlen) + ' descripciones cortas:\n' + commitstr

    return outputstr


def datesAnaly(commitslist):
    """
        Statistics about commits datetime.
        Datetime format: Tue Jul 16 23:59:59 2013 +0200
    """
    outputstr = ''
    datmlist = _extractCommitsTimes(commitslist)
    # print(datmlist)
    com_steps = _countHours(datmlist)
    outputstr += "Horas entre commits: " + "{:.2f}".format(
        sum(com_steps)) + '\n'
    counts = [0, 0, 0, 0]
    for x in com_steps:
        if x < 0.08:  # Very Short, pro-alumn or cheater.
            counts[0] += 1
        elif x < 0.5:  # Usual for this exercises
            counts[1] += 1
        elif x < 2.0:  # Large
            counts[2] += 1
        else:  # Discontinuous work, probably.
            counts[3] += 1
    outputstr += ('Intervalos entre commits: ' +
                  'Corto(< 5m, WARNING): {0[0]}. Aconsejable(< 30m): {0[1]}. ' +
                  'Largo(< 2h): {0[2]}. Discontinuos: {0[3]}.\n').format(counts)
    return outputstr


def _extractCommitsTimes(commits):
    """
        In: list of tuples each one cotains string data with info.
        Out: list of datetime objects with recent down to older date of commits.
    """
    datelist = []  # Ordered list it's needed.
    for commit in commits:
        el = re.findall(DATETIME_PATTERN,
                        commit[2])  # 2 is date of commit tuple
        if not (
            len(el) == 1):  # Don't be date format valid, it doesn't anything.
            continue  # next it for
        # If there was match, tuple has (word-month, day, hour, min, sec, year)
        els = list(el[0])
        els = [DMONTH[els[0]]] + [int(x) for x in
                                  els[1:]]  # Number as str to int
        dt = datetime.datetime(els[5], els[0], els[1], els[2], els[3], els[4])
        datelist.append(dt)
    return datelist


def _countHours(dateslist):
    """
        Obtain a list of float with steps of time (at hours) among consecutive
        datetimes of dateslist. First recent commits and last older is assumed.
    """
    if (len(dateslist) > 1):
        hourslist = []
        dtrecent = dateslist[0]
        for dtelem in dateslist[1:]:
            try:
                tmdt = (dtrecent - dtelem)  # timedelta is result
                hours = (tmdt.days * 24 + tmdt.seconds / 3600)  # ms floored
                hourslist.append(hours)
            except Exception:  # as excep: # OverflowError or anyelse
                print("GitLogAnaly.py:countHours: Error in datetimes op")
                pass  # sys.exc_info()[0]
            dtrecent = dtelem
    return hourslist


def analy_gitlog(studentObj):
    """
        Redirige el comando "git log" del repositorio de alumno
        a un directorio, lo lee y extrae estadísticas del git log.
    """
    repositorypath = studentObj.gitPath
    logfilepath = studentObj.gitlogPath
    resultsfilepath = studentObj.resultPath
    errorfilepath = studentObj.errorPath

    Mstud.writeResultStud("########## ANALISIS GIT LOG ##########")
    com1 = " git log " + repositorypath + " > " + logfilepath + \
           " 2>> " + errorfilepath
    if not os.system(com1) == 0:  # Status
        Mstud.writeErrLogs('Error ejecutando git log', com1)
        Mstud.writeResultStud('Error ejecutando git log', com1)
        return None
    # Extraemos el contenido del fichero, de la salida del git log, a un string.
    s = utils.readFileFull(logfilepath)
    # ANALISIS COMENTARIOS. String out del análisis, volcado a resultados.
    Mstud.writeResultsStud(mainGLA(s))
    return 1
