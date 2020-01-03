""" NOTE: The code in this file was taken from this repo under the MIT license:  https://github.com/econpy/google-ngrams"""

from ast import literal_eval
from pandas import DataFrame
import re
import requests
import subprocess
import sys

corpora = dict(eng_us_2012=17, eng_us_2009=5, eng_gb_2012=18, eng_gb_2009=6,
               chi_sim_2012=23, chi_sim_2009=11, eng_2012=15, eng_2009=0,
               eng_fiction_2012=16, eng_fiction_2009=4, eng_1m_2009=1,
               fre_2012=19, fre_2009=7, ger_2012=20, ger_2009=8, heb_2012=24,
               heb_2009=9, spa_2012=21, spa_2009=10, rus_2012=25, rus_2009=12,
               ita_2012=22)


def get_ngram_freqs(query, corpus, start_year=1990, end_year=2020, smoothing=3, case_insensitive=False):
    params = dict(content=query, year_start=start_year, year_end=end_year,
                  corpus=corpora[corpus], smoothing=smoothing,
                  case_insensitive=case_insensitive)
    if params['case_insensitive'] is False:
        params.pop('case_insensitive')
    if '?' in params['content']:
        params['content'] = params['content'].replace('?', '*')
    if '@' in params['content']:
        params['content'] = params['content'].replace('@', '=>')
    req = requests.get('http://books.google.com/ngrams/graph', params=params)
    res = re.findall('var data = (.*?);\\n', req.text)
    if res:
        data = {qry['ngram']: qry['timeseries']
                for qry in literal_eval(res[0])}
        df = DataFrame(data)
        df.insert(0, 'year', list(range(start_year, end_year + 1)))
    else:
        df = DataFrame()
    return req.url, params['content'], df


def run_query(arg_string):
    """
    Run command line query
    Parameters
    ----------
    arg_string: str
    """
    arguments = arg_string.split()
    query = ' '.join([arg for arg in arguments if not arg.startswith('-')])
    if '?' in query:
        query = query.replace('?', '*')
    if '@' in query:
        query = query.replace('@', '=>')
    params = [arg for arg in arguments if arg.startswith('-')]
    corpus, start_year, end_year, smoothing = 'eng_2012', 1990, 2000, 3
    printHelp, case_insensitive, allData = False, False, False
    save, to_print, to_plot = False, True, False

    # parsing the query parameters
    for param in params:
        if '-save' in param:
            save = True
        elif '-print' in param:
            to_print = True
        elif '-plot' in param:
            to_plot = True
        elif '-corpus' in param:
            corpus = param.split('=')[1].strip()
        elif '-start_year' in param:
            start_year = int(param.split('=')[1])
        elif '-end_year' in param:
            end_year = int(param.split('=')[1])
        elif '-smoothing' in param:
            smoothing = int(param.split('=')[1])
        elif '-case_insensitive' in param:
            case_insensitive = True
        elif '-alldata' in param:
            allData = True
        elif '-help' in param:
            printHelp = True
        else:
            print(('Did not recognize the following argument: %s' % param))
    if printHelp:
        print('See README file.')
    else:
        if '*' in query and case_insensitive is True:
            case_insensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Wildcard and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        elif '_INF' in query and case_insensitive is True:
            case_insensitive = False
            notifyUser = True
            warningMessage = "*NOTE: Inflected form and case-insensitive " + \
                             "searches can't be combined, so the " + \
                             "case-insensitive option was ignored."
        else:
            notifyUser = False
        url, urlquery, df = get_ngram_freqs(query, corpus, start_year, end_year,
                                            smoothing, case_insensitive)
        if not allData:
            if case_insensitive is True:
                for col in df.columns:
                    if col.count('(All)') == 1:
                        df[col.replace(' (All)', '')] = df.pop(col)
                    elif col.count(':chi_') == 1 or corpus.startswith('chi_'):
                        pass
                    elif col.count(':ger_') == 1 or corpus.startswith('ger_'):
                        pass
                    elif col.count(':heb_') == 1 or corpus.startswith('heb_'):
                        pass
                    elif col.count('(All)') == 0 and col != 'year':
                        if col not in urlquery.split(','):
                            df.pop(col)
            if '_INF' in query:
                for col in df.columns:
                    if '_INF' in col:
                        df.pop(col)
            if '*' in query:
                for col in df.columns:
                    if '*' in col:
                        df.pop(col)
        if to_print:
            print((','.join(df.columns.tolist())))
            for row in df.iterrows():
                try:
                    print(('%d,' % int(row[1].values[0]) +
                           ','.join(['%.12f' % s for s in row[1].values[1:]])))
                except:
                    print((','.join([str(s) for s in row[1].values])))
        queries = ''.join(urlquery.replace(',', '_').split())
        if '*' in queries:
            queries = queries.replace('*', 'WILDCARD')
        if case_insensitive is True:
            word_case = 'case_insensitive'
        else:
            word_case = 'caseSensitive'
        filename = '%s-%s-%d-%d-%d-%s.csv' % (queries, corpus, start_year,
                                              end_year, smoothing, word_case)
        if save:
            for col in df.columns:
                if '&gt;' in col:
                    df[col.replace('&gt;', '>')] = df.pop(col)
            df.to_csv(filename, index=False)
            print(('Data to_saved to %s' % filename))
        if to_plot:
            try:
                subprocess.call(['python', 'xkcd.py', filename])
            except:
                if not save:
                    print(('Currently, if you want to create a plot you ' +
                           'must also to_save the data. Rerun your query, ' +
                           'removing the -save option.'))
                else:
                    print(('Plotting Failed: %s' % filename))
        if notifyUser:
            print(warningMessage)


if __name__ == '__main__':
    argumentString = ' '.join(sys.argv[1:])
    if argumentString == '':
        argumentString = eval(input('Enter query (or -help):'))
    else:
        try:
            run_query(argumentString)
        except:
            print('An error occurred.')
