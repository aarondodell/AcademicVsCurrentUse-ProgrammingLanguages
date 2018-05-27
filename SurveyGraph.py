import os
import pandas as pd
import numpy as np
import itertools as it
from pytictoc import TicToc
from PIL import Image, ImageOps, ImageFont, ImageDraw
from plotnine import *

# TIC
tt = TicToc()
tt.tic()

"""
STEP 1: reading and processing Survey and Language info
"""

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

"""
STEP 2: creating Language Label images
"""
for lang_name in colornames_sortedlst:
	# finding lang color using Ref table
	lang_color = colors_ref.at[lang_name, 'color']
	
	# reading Logo
	os.chdir('.\LanguageInfo')
	if lang_name == 'C++':
		lang_logo = Image.open('Cpp.png')
	elif lang_name == 'C#':
		lang_logo = Image.open('Csharp.png')
	else:
		lang_logo = Image.open(lang_name+'.png')
	
	os.chdir('..')
	
	print(lang_name, lang_logo.size)
	
	# creating white background
	background_img = Image.new('RGBA', (680, 280), 'white')
	# adding border
	background_img = ImageOps.expand(background_img, border = 10, fill = lang_color)
	
	# resizing LangLogo
	lang_logo = lang_logo.resize((240,240))
	
	# pasting LangLogo onto background, creating full image
	full_img = background_img.copy()
	# try as mask
	try:
		full_img.paste(lang_logo, (30,30), mask = lang_logo)
	# if logo is no mask, paste as normal
	except ValueError:
		full_img.paste(lang_logo, (30,30))
	
	# creating colored font
	lang_fnt = ImageFont.truetype('ARLRDBD.TTF', 72)
	# finding label size, given the name
	lang_labelsize = lang_fnt.getsize(lang_name)
	# determining location of the Language Label
	
	
	# draw object
	full_draw = ImageDraw.Draw(full_img)
	
	# drawing black outline... anchor is (290, 30)
	for position_tup in (list(it.product(np.arange(287, 294), [18])) +	#top border
							  list(it.product(np.arange(289, 291), [17])) +	#top border extra
							  list(it.product([292], np.arange(18, 23))) +	#right border
							  list(it.product([293], np.arange(19, 22))) +	#right border extra
							  list(it.product(np.arange(287,294), [22])) +	#bottom border
							  list(it.product(np.arange(289,291), [23])) +	#bottom border extra
							  list(it.product([288], np.arange(18,23))) +	#left border
							  list(it.product([287], np.arange(19,22)))):	#left border extra
		full_draw.text(position_tup, lang_name, fill = 'black', font = lang_fnt)
	
	# drawing colored center
	full_draw.text((290,20), lang_name, fill = lang_color, font = lang_fnt)
	
	# saving image
	os.chdir('.\LanguageLabels')
	full_img.save(lang_name+'.png')
	os.chdir('..')

"""
STEP 3: ggplotting
"""

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