import json,os
import tkinter as tk
import wordcloud
from tkinter import ttk as ttk
from abc import ABC, abstractmethod
from dateutil.parser import parse
import matplotlib.pyplot as plt
import pandas as pd
import dask.dataframe as dd
import dask.array as da
import dask.bag as db
import numpy as np
import re
import unidecode
from icecream import ic
#from genderbr import get_gender

# All new modules have to inherit from this class
TEXT_WIDGET_WIDTH = 160
class ComponentModel():
    @abstractmethod
    def get_name():
        '''
        This method returns the name of the model

        Outputs:
        - Model name (Type: str)
        '''
        raise NotImplementedError

    @abstractmethod
    def requires_extra_input():
        '''
        This method tell wheter this model requires an extra input or not

        Outputs:
        - Model's requirement of extra input (Type: bool)
        '''
        raise NotImplementedError

    @abstractmethod
    def get_description():
        '''
        Returns a description of the model to be shown when the user clicks the help button

        Outputs:
        - String describing the model
        '''
        raise NotImplementedError

    @abstractmethod
    def execute(data, extra_input = None):
        '''
        This method executes it's algorithm on the given data

        Inputs:
        - Input data (Type: List of dictionaries)
        Outputs:
        - Model's output list(Type: string, path to png or jpeg image or a pandas DataFrame)
        '''
        raise NotImplementedError

def myfunc(x):
    #print(f'x antes:\n{x}')

    #print(f'x antes é {x} type = ', type(x))
    x = x.replace('\n','')
    x = x.strip()
    x = x.replace('[','')
    x = x.replace(']','')
    x = x.replace('},','}')
    #print(f'x depois:\n{x}')
    # Caso de problema no jsondecoder
    # if (len(x) < 100):
    #     print(f'x é {x} type = ', type(x))
    try:
        return json.loads(x)
    except json.JSONDecodeError as err:
        # grab a reasonable section, say 40 characters.
        # start, stop = max(0, err.pos - 20), err.pos + 20
        # snippet = err.doc[start:stop]
        print(err)
        print(err.doc)
        # print('... ' if start else '', snippet, ' ...' if stop < len(err.doc) else '', sep="")
        # print('^'.rjust(21 if not start else 25))
    return

class LoadFilesModel():

    def __init__(self):
        #document's path
        self.files_path = tk.StringVar()

        #JSON files in the current directory
        self.json_files = []

        #data that will be analyzed, its a list of list of dictionaries
        self.data_list = []

        #the possible values for each metadata, its a dictionary where each item is a set
        self.key_to_possible_values_dic = {}

        #all the available metadata, aka keys
        self.all_keys = []

    def set_path_variable(self, path_variable):
        self.files_path = path_variable

    def m_process_json(self):
        try:
            self.json_files = [json_file for json_file in os.listdir(self.files_path.get()) if json_file.endswith('.json')]
        except FileNotFoundError:
            Print("Arquivos JSON não encontrados, o diretório indicado pode estar incorreto")

        #I'M APPENDING TWO DIFFERENT TYPES OF JSON FILES HERE, 1 AND 2 DEGREE CASES, MAY CAUSE ERRORS
        df_list = []
        self.data_list.clear()
        if len(self.json_files) > 0:
            self.data = db.read_text(self.files_path.get()+'/*.json',linedelimiter="},\n", blocksize=2**28).map(myfunc).to_dataframe()
            print(self.data)
        self.all_keys = list(self.data.columns)

        #remove useless keys for filtering
        UNIQUE_KEYS = ['ementa', 'processo', 'cdacordao', 'julgado', 'pagina', 'duplicado', 'cd_doc']

        #Get available metadata and it's possible values by iterating over the columns
        self.key_to_possible_values_dic.clear()
        for column in self.data.columns:
            if column not in UNIQUE_KEYS:
                print(column)
                self.key_to_possible_values_dic[column] = np.sort(list(self.data[column].unique()))

        return self.all_keys, self.key_to_possible_values_dic

    def is_date(self,string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    #
    def filter_is_empty(self, filter_list):
        flag = True
        for filter in filter_list:
            if filter != '':
                flag = False
        return flag

    def apply_filters(self,filters_dict, view_filters_list):
        df = self.data.copy()

        # Apply visualization filter
        for column in df.columns:
            if column not in view_filters_list:
                df = df.drop(column, axis=1)
                if column.capitalize() in filters_dict.keys():
                    del filters_dict[column.capitalize()]

        # Apply selection filter
        for key,values in filters_dict.items():
            if not self.filter_is_empty(values):
                filter = (df[key.lower()].isin(values))
                df = df.loc[filter]

        # Drop duplicated documents
        df = df.drop_duplicates(subset = ['processo'])
        if 'duplicado' in df.columns:
            df = df.drop(columns=['duplicado'])

        return df

    def save_csv(self, data):
        #df = pd.DataFrame.from_records(data)
        file_name = 'veritas_consulta'
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".csv", initialfile=file_name, title='Salvar como')
        if not f.name == '':
            print(f'name: {f.name}')
            data.to_csv(f.name, single_file=True)
        else:
            return

    def save_json(self, data):
        file_name = 'veritas_consulta'
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".json", initialfile=file_name, title='Salvar como')
        if not f.name == '':
            # One json file is going to be created for each partition of the data
            name_without_extension = f.name.split('.')[0]
            file_name = name_without_extension.split('/')[-1]
            data.to_json(name_without_extension+'-*.json', orient='records', lines=False, force_ascii=False)
            # Remove the annoying empty json file that is generated
            os.remove(name_without_extension+'.json')
        else:
            return

class TestModel(ComponentModel):
    def __init__(self):
        print('Starting test model')

    def get_name(self):
        return 'Test Model'

    def requires_extra_input(self):
        return False

    def get_description(self):
        return 'teste'

    def execute(self, data, extra_input = None):
        fig,ax = plt.subplots()
        ax.plot([1,2,3],[1,2,3])
        cwd = os.getcwd()
        fig.savefig(cwd+'/images/fig1.png')
        img_path = cwd+'/images/fig1.png'
        return ['test_output', img_path, 'eaiii']

class CountDocuments(ComponentModel):
    def __init__(self):
        return
    def get_name(self):
        return 'Count Documents'

    def requires_extra_input(self):
        return True

    def get_description(self):
        string =  'Realiza a contagem dos documentos em relação às categorias escolhidas, os resultados incluem contagem absoluta e contagem relativa. '
        string += 'Para gerar gráficos selecione alguns dos checkboxes disponíveis.'
        return string

    def insert_linebreak(self,string, lengLabel=20):
        string = str(string)
        return '\n'.join(string[i:i+lengLabel] for i in range(0, len(string), lengLabel))

    def execute(self, data, extra_input):
        '''
        This module's required extra input is a list containing the categories on where the count in going to be made
        '''
        output = []
        df = data
        total_documents = len(df)
        output.append('Número total de documentos: ' + str(total_documents))

        for column in extra_input['selected_categories']:
            if column in df.columns:
                output.append('\nNúmero de documentos por: ' + str(column))
                absolute_count = df[column].value_counts().compute()
                relative_count = df[column].value_counts(normalize = True).compute()
                tmp_df = pd.DataFrame({'Absoluto': absolute_count, 'Relativo' : relative_count})
                output.append(tmp_df)
                if extra_input['bar_selected'] == 1:
                    # add a line break so the names can be read
                    bar_df = tmp_df.copy()
                    bar_df.index = bar_df.index.map(self.insert_linebreak)

                    output.append('\nGráfico de barras das '+ str(extra_input['bar_n'])+' aparições mais frequentes:')

                    bar_fig, bar_ax = plt.subplots()
                    bar_fig.set_size_inches((12,6))
                    plt.rcParams['font.size'] = 12.0
                    bar_df['Absoluto'].sort_index().head(extra_input['bar_n']).plot(kind='bar', ax=bar_ax)
                    bar_ax.set_xlabel(column.capitalize())
                    bar_ax.set_ylabel('N° de documentos')
                    bar_ax.set_title(str(column.capitalize()+ 's mais frequentes'))
                    plt.tight_layout()
                    cwd = os.getcwd()
                    bar_fig.savefig(cwd+'/images/'+column+'_bar'+'.png')
                    output.append(cwd+'/images/'+column+'_bar'+'.png')
                if extra_input['pie_selected'] == 1:
                    output.append('\nGráfico de pizza:')
                    pie_fig, pie_ax = plt.subplots()
                    pie_fig.set_size_inches((12,6))
                    plt.rcParams['font.size'] = 12.0

                    # Uses the relative count because its a pie chart
                    tmp_df['Relativo'].plot(kind='pie', ax=pie_ax, autopct='%1.1f%%', textprops={'fontsize': 8}, normalize = True)
                    pie_ax.set_title(str(column.capitalize()+ 's'))
                    pie_ax.set_ylabel('')
                    plt.tight_layout()
                    cwd = os.getcwd()
                    pie_fig.savefig(cwd+'/images/'+column+'_pie'+'.png')
                    output.append(cwd+'/images/'+column+'_pie'+'.png')
            output.append('-'*TEXT_WIDGET_WIDTH)

        return output

class MatchNames(ComponentModel):
    def get_name(self):
        return 'Agrupar pares'

    def requires_extra_input(self):
        return False

    def get_description(self):
        return 'Encontra pares de pessoas que estão juntamente envolvidas em mais de um processo'

    def isNaN(self, string):
        return string != string

    def extract_people(self, data):
        #author_pattern = re.compile(r'\n')
        #author_pattern = re.compile('(.+?)(?=\n)')

        authors = []
        defendants = []
        victims = []
        main_pattern_string = r'(Autor|Autora|Autor e Parte|Requerente|Requerente (s)|Impetrante|Exequente|Exeqüente|Embargante|Demandante|MAGISTRADO|Herdeiro|Inventariante|Inventariante (Ativo)|Inventariante (Ativo)):\s(.+?)(?=(Justiça Gratuita|Juiz|Juíza|Promotor de Justiça|Prioridade Idoso|Aos|Em \d\d|Autos n|ATA D|Ata d|Data da|Artigo da|Conclusão|CONCLUSÃO|C O N C L U S Ã O|SENTENÇA|Réu Preso|Descrição|Data da identificação|Vistos|VISTOS|Controle|Processo))'
        general_pattern = re.compile(main_pattern_string)
        i = 0
        print_index = 99999
        processo = '0'
        for i,text in enumerate(data['julgado']):
            author = np.NaN
            defendant = np.NaN
            victim = np.NaN
            # if i == print_index or data.iloc[i]['processo'] == processo:
            #     print(text)
            sentence = general_pattern.search(text)
            if sentence:
                # Check if there is a victim
                check_victim_pattern = re.compile(r'(Vítima|Vitima)')
                check_victim_search = check_victim_pattern.search(sentence.group())
                if check_victim_search:
                    # There is the name of the victim in the text
                    victim_pattern = re.compile(r'(?<=(Vítima|Vitima)).*')
                    victim_search = victim_pattern.search(sentence.group())
                    if victim_search:
                        victim = victim_search.group()
                        # if i == print_index or data.iloc[i]['processo'] == processo:
                        #     print(f'\n\vítima: ', victim_search.group())
                        #     print('vitima real=', victim)
                    # get the remaining text without the victim
                    no_victim_pattern = re.compile(r'.*(?=\s(Vítima|Vitima))')
                    no_victim_search = no_victim_pattern.search(sentence.group())

                    if no_victim_search:
                        sentence = no_victim_search

                # First get the phrase without the first colon
                remove_first_colon_pattern = re.compile(r'(?<=:\s).*')
                no_first_colon_search = remove_first_colon_pattern.search(sentence.group())
                # if i == print_index or data.iloc[i]['processo'] == processo:
                #     print(f'\n\nsentence: ', sentence.group())
                if no_first_colon_search:
                    # Now get the author, which is the text before the word that is before the remaining colon
                    #author_pattern = re.compile(r'(?<=:\s).*(?=\s(\S+):)')
                    # if i == print_index or data.iloc[i]['processo'] == processo:
                    #     print(f'\n\nno_first_colon_search: ', no_first_colon_search.group())
                    author_pattern = re.compile(r'.*(?=\s(\S*):)')
                    author_search = author_pattern.search(no_first_colon_search.group())
                    if author_search:
                        # remove the case where the defendant part is written using "autor do fato"
                        remove_autor_do_pattern = re.compile(r'.*(?=\sAutor do)')
                        remove_search = remove_autor_do_pattern.search(author_search.group())
                        if remove_search:
                            author = remove_search.group()
                        else:
                            author = author_search.group()

                    # Get the defendant, which is the text after the remaining colon
                    defendant_pattern = re.compile(r'(?<=:\s).*')
                    defendant_search = defendant_pattern.search(no_first_colon_search.group())
                    if defendant_search:
                        defendant = defendant_search.group()
                    else:
                        # cant find a second colon, so the match is only for the author
                        author = no_first_colon_search.group()
            else:
                # check if there is only information about the defendant
                pattern = re.compile(main_pattern_string)
                sentence = pattern.search(text)
                if sentence:
                    check_victim_pattern = re.compile(r'(Vítima|Vitima)')
                    check_victim_search = check_victim_pattern.search(sentence.group())
                    if check_victim_search:
                        # There is the name of the victim in the text
                        victim_pattern = re.compile(r'(?<=(Vítima|Vitima)).*')
                        victim_search = victim_pattern.search(sentence.group())
                        if victim_search:
                            victim = victim_search.group()

                        # get the remaining text without the victim
                        no_victim_pattern = re.compile(r'.*(?=\s(Vítima|Vitima))')
                        no_victim_search = no_victim_pattern.search(sentence.group())

                        if no_victim_search:
                            sentence = no_victim_search

                    remove_first_colon_pattern = re.compile(r'(?<=:\s).*')
                    no_first_colon_search = remove_first_colon_pattern.search(sentence.group())
                    if no_first_colon_search:
                        defendant = no_first_colon_search.group()

            # Remove authors and defendants that are too long and therefore are probably wrong
            # if len(str(author)) > 100:
            #     author = np.nan
            # if len(str(defendant)) > 100:
            #     defendant = np.nan
            # if len(str(victim)) > 100:
            #     victim = np.nan
            # Remove extra whitespaces and colon
            if not self.isNaN(author):
                author = self.clean_extraction(author)

            if not self.isNaN(defendant):
                defendant = self.clean_extraction(defendant)
            if not self.isNaN(victim):
                victim = self.clean_extraction(victim)
            authors.append(author)
            defendants.append(defendant)
            victims.append(victim)
            i = i+1

        data = data.assign(autor=authors, réu=defendants, vítima=victims)
        # data['autor'] = dd.from_pandas(pd.Series(authors), npartitions=data.npartitions).reset_index()
        # data['réu'] =  dd.Series(defendants)
        # data['vítima'] =  dd.Series(victims)
        null_authors = data['autor'].isnull().sum()
        null_defendants = data['réu'].isnull().sum()
        null_victims = data['vítima'].isnull().sum()
        rows = data.shape[0]
        print(f'autores faltantes: {(null_authors/rows)*100}%\nréus faltantes:{(null_defendants/rows)*100}%\nvítimas faltantes:{(null_victims/rows)*100}%\n')
        return data

    def clean_extraction(self, string):
        string = re.sub(':', '', string)
        string = re.sub('- presente', '', string)
        string = re.sub('- ausente', '', string)
        string = re.sub('– presente', '', string)
        string = re.sub('– ausente', '', string)
        # Remove text after comma
        string = re.sub(',.*', '', string)
        string = re.sub('Réu.*', '', string)
        string = re.sub('Advogado.*', '', string)
        string = re.sub('e outro.*', '', string)
        string = str(string).strip()
        return string
        #author = str(unidecode.unidecode(author))
    def search_single_person(self,data):
        author_city_grouped_count = data.groupby(['comarca','autor'], as_index = True).size()
        author_city_grouped = data.groupby(['comarca','autor'], as_index = False)
        defendant_city_grouped_count = data.groupby(['comarca','réu'], as_index = True).size()
        defendant_city_grouped = data.groupby(['comarca','réu'], as_index = False)
        all_count = author_city_grouped_count.combine(defendant_city_grouped_count,lambda x,y:x+y, fill_value = 0)
        # author_count  = data['autor'].value_counts()
        # defendant_count = data['réu'].value_counts()
        # all_count = author_count.combine(defendant_count,lambda x,y:x+y, fill_value = 0)
        count_df = pd.DataFrame({'Número de aparições': all_count})
        not_unique = count_df.loc[count_df['Número de aparições'] > 1]
        total_length = len(count_df)
        not_unique_length = len(not_unique)
        print(f'Pessoas que estão em mais de 1 documento: {(not_unique_length/total_length)*100}%')

        # Recover de process code from the selected processes
        author_merge = not_unique.merge(data, left_index=True, right_on = ['comarca','autor'])
        author_merge = author_merge.drop('réu',axis=1)
        author_merge = author_merge.rename(columns={'autor': 'nome'})
        author_merge['autor ou réu'] = 'autor'
        defendant_merge = not_unique.merge(data, left_index=True, right_on = ['comarca','réu'])
        defendant_merge = defendant_merge.drop('autor',axis=1)
        defendant_merge = defendant_merge.rename(columns={'réu': 'nome'})
        defendant_merge['autor ou réu'] = 'réu'
        author_defendant_merge = pd.concat([author_merge,defendant_merge], sort = False)
        author_defendant_merge = author_defendant_merge.sort_values('nome').reset_index()

        # Drop null values
        author_defendant_merge = author_defendant_merge.replace(['nan',''],np.nan)
        author_defendant_merge = author_defendant_merge.dropna()

        return [author_defendant_merge]

    def is_person(self, name_series):
        is_name_list = []
        for name in name_series:
            first_name = name.split()[0]
            print(first_name)
            if get_gender(first_name) != None:
                print('is person\n')
                is_name_list.append(True)
            else:
                # It's not a person
                print('is not a person\n')
                is_name_list.append(False)
        return np.array(is_name_list)

    def set_part1_part2(self, dd):
        # Convert the useful columns to pandas dataframe
        useful_columns = dd.loc[:,['autor','réu','vítima']]
        # The part to be considered is the victim if it exists and the author otherwise
        useful_columns['parte1'] = np.where(useful_columns['vítima'] == 'nan', useful_columns['autor'], useful_columns['vítima'])
        useful_columns['parte2'] = useful_columns['réu']
        # Remove companies, government institutions, etc.
        # new_data['parte1'] = np.where(self.is_person(new_data['parte1']), new_data['parte1'], np.nan)
        # new_data['parte2'] = np.where(self.is_person(new_data['parte2']), new_data['parte2'], np.nan)
        useful_columns['parte1'] = np.where(useful_columns['parte1'].str.lower().str.contains('justiça pública', regex=False, na=False), np.nan, useful_columns['parte1'])
        useful_columns['parte2'] = np.where(useful_columns['parte2'].str.lower().str.contains('justiça pública', regex=False, na=False), np.nan, useful_columns['parte2'])

        # Sort so the order doesnt matter
        useful_columns['parte1'] = useful_columns['parte1'].map(lambda x: x.lower() if isinstance(x,str) else x)
        useful_columns['parte2'] = useful_columns['parte2'].map(lambda x: x.lower() if isinstance(x,str) else x)
        useful_columns[['parte1','parte2']] = np.sort(useful_columns[['parte1','parte2']].astype('str'), axis = 1)

        # Assign new columns to the dask dataframe
        dd = dd.assign(parte1 = useful_columns['parte1'], parte2 = useful_columns['parte2'])

        # Remove missing values
        dd = dd.replace(['nan','','NaN'],np.nan)
        dd = dd.dropna(axis = 0, how='any', subset=['parte1','parte2'])

        return dd
    def search_pairs(self,data):
        # Copy so it doesnt cause inconsistency
        new_data = data.copy().astype('str')
        dataTypeDict = dict(new_data.dtypes)
        dataTypeDict['parte1'] = 'object'
        dataTypeDict['parte2'] = 'object'
        new_data = new_data.map_partitions(self.set_part1_part2, meta=dataTypeDict)
        #new_data = new_data[['autor','réu','vítima']].compute()

        data_grouped_count = new_data.groupby(['parte1','parte2']).size().compute()
        data_count = pd.DataFrame({'Número de Aparições': data_grouped_count})
        not_unique = data_count.loc[data_count['Número de Aparições'] > 1]
        n_pairs = len(data_count)
        not_unique_pairs = len(not_unique)
        # Convert to dask dataframe
        not_unique = dd.from_pandas(not_unique.reset_index(), npartitions=1)

        # Merge to recover process code and remaining columns
        merged_pairs = not_unique.merge(new_data, left_index = False, left_on = ['parte1', 'parte2'], right_on = ['parte1','parte2'])

        # Assign a number to each group
        merged_pairs = merged_pairs.compute()
        merged_pairs['grupo'] = merged_pairs.groupby(['parte1','parte2']).ngroup()
        merged_pairs['grupo'] = merged_pairs['grupo'] + 1
        merged_pairs = merged_pairs.set_index('grupo')
        merged_pairs = merged_pairs.rename(columns = {'Número de Aparições': 'tamanho_grupo'})
        if 'pagina' in merged_pairs.columns:
            merged_pairs = merged_pairs.drop(columns=['pagina','parte1','parte2'])
        else:
            merged_pairs = merged_pairs.drop(columns=['parte1','parte2'])

        # Rearrange column order
        columns = list(merged_pairs.columns)
        columns.remove('autor')
        columns.remove('réu')
        columns.remove('vítima')
        # columns.remove('parte1')
        # columns.remove('parte2')
        merged_pairs = merged_pairs[['autor','réu','vítima']+columns]

        # Drop the victim column if its full o nan values
        merged_pairs = merged_pairs.replace(['nan',''],np.nan)
        merged_pairs = merged_pairs.dropna(axis=1, how='all')

        print(f'Pares que estão em mais de 1 documento: {(not_unique_pairs/n_pairs)*100}%')
        return [merged_pairs]

    def execute(self,data, extra_input):
        output = []
        # Extract author, defendant and victim from the text, add it as three new columns
        dataTypeDict = dict(data.dtypes)
        dataTypeDict['autor'] = 'object'
        dataTypeDict['réu'] = 'object'
        dataTypeDict['vítima'] = 'object'
        data = data.map_partitions(self.extract_people, meta=dataTypeDict)
        # gender1 = get_gender('Guilherme')
        # gender2 = get_gender('Justíça Pública')
        # print(gender1)
        # print(gender2)
        # Find the people that are part of more than one document
        #output += self.search_single_person(data)

        # Find the pair of people that appear together in more than one document
        output += self.search_pairs(data)
        return output
        # output_dict[self.get_name()] = output
        # ic(output_dict)

class WordCloud(ComponentModel):
    def get_name(self):
        return 'Nuvem de Palavras'

    def requires_extra_input(self):
        return False

    def get_description(self):
        return 'Gera uma nuvem de palavras a partir do inteiro teor dos documentos.'

    def execute(self,data, extra_input):
        # Define the stopwords
        output = []
        stopwords = set(wordcloud.STOPWORDS)
        # Unite it with the portuguese stopwords
        pt_stopwords = []
        cwd = os.getcwd()
        with open(cwd+'/gui/util/stopwords.txt') as f:
            [pt_stopwords.append(re.sub(r'\n','',word).strip()) for word in f]
        stopwords = stopwords.union(pt_stopwords)
        #print(stopwords)

        # Put all the texts together
        text = " ".join(document for document in data.julgado)

        # Generate and save the wordcloud image
        wc = wordcloud.WordCloud(min_font_size=10,
               max_font_size=300,
               background_color='black',
               mode="RGB",
               stopwords=stopwords,
               width=1000,
               height=500,
               normalize_plurals= True).generate(text)
        #wc.to_file(cwd+'/images/'+'nuvem_palavras'+'.png')
        plt.figure(figsize=(12,6))
        plt.imshow(wc,interpolation='bilinear')
        plt.axis('off')
        plt.savefig(cwd+'/images/'+'nuvem_palavras'+'.png')
        output.append(cwd+'/images/'+'nuvem_palavras'+'.png')
        return output
# class DateGraph(ComponentModel):
#     def get_name():
#         return 'Date Graph'
#
#     def requires_extra_input():
#         return False
#
#     def get_description():
#         return 'Gera um gráfico do número de documentos por período de tempo'
#
#     def execute(data, extra_input = None):
