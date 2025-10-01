from zipfile import ZipFile
from pathlib import Path
from lxml import etree
from tqdm.notebook import tqdm_notebook
from collections import defaultdict
import pandas as pd
import io

def add_context(df: pd.DataFrame, df_metadata: pd.DataFrame) -> pd.DataFrame:
    df['month'] = df['date'].str[:7] # extract year-month from date
    df = df.merge(df_metadata, right_on='month',left_on='month', how='left') # merge metadata to newspaper dataframe
    return df # return the dataframe with added metadata

class Zip2CSV(object):
    """class to transform alto2txt metadata files to a csv format"""
    def __init__(self, nlp: str , directory: str='data', include_text: bool=True):
        """set location of zip files"""
        self.directory = Path(directory)
        self.nlp = nlp
        self.metadata = ZipFile(self.directory / 'metadata' / f'{self.nlp}_metadata.zip')
        self.include_text = include_text
        if self.include_text:
            self.content = ZipFile(self.directory / 'plaintext' / f'{self.nlp}_plaintext.zip')
        else: 
            self.content = ''

    @property
    def xml_files(self):
        """create a generator with all xml files"""
        return (f for f in self.metadata.namelist() if f.endswith('.xml'))

    def extract_metadata(self,file: str):
        """retrieve metadata from an alto2txt xml file
        """
        # keys correspond to the parents, the values are a list of all children
        metadata_fields = {'item':['title','item_type','ocr_quality_mean','ocr_quality_sd','word_count','plain_text_file'],
                           'issue':['date'],
                           'publication':['title','location','source']}
        metadata_dict = dict()

        with self.metadata.open(file,'r') as in_xml:
            tree = etree.parse(in_xml)  
            for parent,fields in metadata_fields.items():
                
                for field in fields:
    
                    try:
                        metadata_dict[f'{parent}/{field}'] = tree.xpath(f'.//{parent}/{field}')[0].text
                    except:
                        metadata_dict[f'{parent}/{field}'] = None

        return metadata_dict

    def proces_corpus(self):
        """process the articles, extract metadata from xml 
        and retrieve content from zip archive"""
        self.corpus = defaultdict(dict)
        for xml_file in tqdm_notebook(self.xml_files):
            self.corpus[xml_file] = self.extract_metadata(xml_file)
            if self.include_text:
                with io.TextIOWrapper(self.content.open(xml_file[:-4].rstrip('_metadata')+'.txt')) as text: #,'r').read()
                    self.corpus[xml_file]['text'] = text.read()

    def convert(self,output: str='.'):
        """convert a newspaper to a csv file
        """
        output = Path(output)
        output.mkdir(exist_ok=True)

        self.proces_corpus()
        df = pd.DataFrame(self.corpus).T
        df.rename(columns={"publication/title": "newspaper_title"}, inplace=True)
        df.columns = [c.split('/')[-1] for c in df.columns]
  
        df['year'] = df['date'].apply(lambda x: x.split('-')[0])
        df['month'] = df['date'].apply(lambda x: x.split('-')[1])
        df['day'] = df['date'].apply(lambda x: x.split('-')[1])
        df['nlp'] = df['plain_text_file'].apply(lambda x: x.split('_')[0])
        df['issue'] = df['plain_text_file'].apply(lambda x: x.split('_')[1][3:])
        df['art_num'] = df['plain_text_file'].apply(lambda x: x.split('_')[-1].split('.txt')[0])
        

        df.rename(columns={"nlp": "NLP", 'title':'article_headline'}, inplace=True)

        # df.rename(columns={"issue": "issue_id",
        #                    'nlp': 'publication_code',
        #                    'art_num':'item_id',
        #                    'source':'data_provider',
        #                    'ocr_quality_mean':'ocrquality'}, inplace=True)

        df.to_csv(output/f'{self.nlp}.csv')

        

            
