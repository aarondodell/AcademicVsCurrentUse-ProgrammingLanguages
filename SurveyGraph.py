import os
import pandas as pd
from pytictoc import TicToc
from PIL import Image, ImageFont, ImageDraw
from plotnine import *

# TIC
tt = TicToc()
tt.tic()

# reading raw_survey
os.chdir('.\Sources')
raw_survey = pd.read_csv('Surveys.csv')
os.chdir('..')

# reading color references for languages
os.chdir('.\LanguageInfo')
colors_ref = pd.read_json('LanguageColors.json').transpose()
os.chdir('..')

# splitting RawSurvey into two
main_survey_df = raw_survey.loc[:9,:]
main_survey_df['Q1_Academic'] = main_survey_df['Q1_Academic'].astype('int64')

questions_df = raw_survey.loc[20:, ['Language','Q1_Academic']].\
					rename(columns = {'Language': 'Question', 'Q1_Academic': 'Text'}).reset_index(drop = True)

# fixing Matlab and SQL color indices
colors_index = colors_ref.index.tolist()
colors_index[colors_index.index('Matlab')] = 'MATLAB'
colors_index[colors_index.index('PLSQL')] = 'SQL'
colors_ref.index = colors_index

# finding hex codes sorted
colornames_sortedlst = sorted(main_survey_df['Language'].unique())
colorhex_sortedlst = [colors_ref.at[cname, 'color'] for cname in colornames_sortedlst]

# initial Parallel df
parallel_df = pd.melt(main_survey_df, id_vars = 'Language', value_vars = ['Q1_Academic_Perc', 'Q2_Current_Perc'],
                      var_name = 'QType', value_name = 'Percent')

# assigning PercentNum and Log(1 + percentNum)
parallel_df['PercentNum'] = parallel_df['Percent'] * 100

# initial ggplot obj
parallel_ggplot = (ggplot(mapping = aes(x = 'QType', y = 'PercentNum', color = 'Language', group = 'Language'),
							  data = parallel_df) +
						geom_point() +
						geom_line() +
						geom_label(mapping = aes(label = 'Language')) +
						scale_color_manual(values = colorhex_sortedlst, guide = False) +
						labs(title = 'Programmer Survey: Languages Academic vs. CurrentUse',
							   x = 'Question', y = 'Percentage') +
						theme_538())
    
parallel_ggplot.save('parallel_ggplot.png', width = 5, height = 10, dpi = 200)

# TOC
tt.toc()