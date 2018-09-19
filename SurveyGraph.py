import os
import pandas as pd
import numpy as np
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
STEP 2: defining Create Language Label Image
"""
def CreateLangLabelImg_fx(lang_rank, lang_name, vote_percent, vote_count, q_name):
	'''finding Color and finding Logo image'''
	# addition to lang_rank
	lang_rank += 1
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
	
	'''Logo resizing'''
	# resizing LangLogo
	# if WIDE, then scale the height according to width
	if lang_logo.size[0] > lang_logo.size[1]:
		# since WIDE, we find the nu_height
		nuheight_float = (160/lang_logo.size[0]) * lang_logo.size[1]
		nuheight_int = round(nuheight_float/2.0) * 2
		# resiziing LangLogo
		lang_logo = lang_logo.resize((160, nuheight_int))
	# if TALL, then scale the width according to the height
	elif lang_logo.size[1] > lang_logo.size[0]:
		# since TALL, we find NuWidth
		nuwidth_float = (160/lang_logo.size[1]) * lang_logo.size[0]
		nuwidth_int = round(nuwidth_float/2.0) * 2
		# resizing LangLogo
		lang_logo = lang_logo.resize((nuwidth_int, 160))
	# if neither tall nor wide, then EVEN, and just resize to 280,280
	else:
		lang_logo = lang_logo.resize((160,160))
	
	'''Title sizing'''
	# defining Lang Title Str for the #2 current tie
	if q_name == 'Q2Current' and lang_name in ['Java', 'JavaScript']:
		lang_title_str = '2 (tie): ' + lang_name
	# defining the normal Lang Title Str
	else:
		lang_title_str = str(lang_rank) + ': ' + lang_name
	
	# determing which font number is closest to 80 height for the Title
	for fsize in np.arange(100,0,-1):
		# creating langFont
		lang_title_fnt = ImageFont.truetype('ARLRDBD.TTF', fsize)
		# testing if at or below 80, breaking if so
		if lang_title_fnt.getsize(lang_title_str)[1] <= 80:
			break
	
	# finding the size of the title
	lang_title_size = lang_title_fnt.getsize(lang_title_str)
	
	'''Vote Perc sizing'''
	# defining Lang VotePerc Str
	lang_voteperc_str = '{:.1%}'.format(vote_percent)
	
	# determing which font number is closest to 50 height for the Percent
	for fsize in np.arange(100,0,-1):
		# creating langFont
		lang_voteperc_fnt = ImageFont.truetype('ARLRDBD.TTF', fsize)
		# testing if below 50, breaking if so
		if lang_voteperc_fnt.getsize(lang_voteperc_str)[1] <= 50:
			break
	
	# defining Lang VotePerc Size
	lang_voteperc_size = lang_voteperc_fnt.getsize(lang_voteperc_str)
	
	'''Vote Count sizing'''
	# defining Lang VoteCount Str
	lang_votecount_str = '(' + str(int(vote_count)) + ' votes)'
	
	# determing which font number is closest to 30 height for the Count
	for fsize in np.arange(100,0,-1):
		# creating langFont
		lang_votecount_fnt = ImageFont.truetype('ARLRDBD.TTF', fsize)
		# testing if below 30, breaking if so
		if lang_votecount_fnt.getsize(lang_votecount_str)[1] <= 30:
			break	
	
	# defining Lang VoteCount Size
	lang_votecount_size = lang_votecount_fnt.getsize(lang_votecount_str)
	
	'''White Background creation'''
	# determining the width
	# first, find the longer length between the Title, Perc, and Count
	farthest_x = max([lang_title_size[0], lang_voteperc_size[0] + 20, lang_votecount_size[0] + 40])
	
	# creating Background Size, picking between Farthest Title or Count for the X width
	background_size = (farthest_x + 215, 190)
		
	# creating white background
	background_img = Image.new('RGBA', background_size, 'white')
	# adding border
	background_img = ImageOps.expand(background_img, border = 5, fill = lang_color)
	
	'''Pasting Logo'''
	# pasting LangLogo onto background, creating full image
	full_img = background_img.copy()
	# calculating the position of the logo
	logo_position = (int(20 + (160-lang_logo.size[0])/2), int(20 + (160-lang_logo.size[1])/2))
	# try as mask
	try:
		full_img.paste(lang_logo, logo_position, mask = lang_logo)
	# if logo is no mask, paste as normal
	except ValueError:
		full_img.paste(lang_logo, logo_position)
	
	'''Drawing on Title, Vote Perc, and Vote Count'''
	# determining Title position
	lang_title_position = (200,5)
	# creating draw object
	full_draw = ImageDraw.Draw(full_img)
	# drawing colored center
	full_draw.text(lang_title_position, lang_title_str, fill = lang_color, font = lang_title_fnt)
	
	# drawing Lang VotePerc
	full_draw.text((220, 5 + 90), lang_voteperc_str, fill = lang_color, font = lang_voteperc_fnt)
	
	# drawing Lang VoteCount
	full_draw.text((240, 5 + 90 + 60), lang_votecount_str, fill = lang_color, font = lang_votecount_fnt)
	
	# drawing black outline... anchor is (290, 30)
	# FIX LATER
	'''
	for position_tup in (list(it.product(np.arange(287, 294), [18])) +	#top border
							  list(it.product(np.arange(289, 291), [17])) +	#top border extra
							  list(it.product([292], np.arange(18, 23))) +	#right border
							  list(it.product([293], np.arange(19, 22))) +	#right border extra
							  list(it.product(np.arange(287,294), [22])) +	#bottom border
							  list(it.product(np.arange(289,291), [23])) +	#bottom border extra
							  list(it.product([288], np.arange(18,23))) +	#left border
							  list(it.product([287], np.arange(19,22)))):	#left border extra
		full_draw.text(position_tup, lang_name, fill = 'black', font = lang_title_fnt)
	'''
	
	# moving into proper folder and saving image
	os.chdir('.\LanguageLabels')
	full_img.save(q_name + '_' + str(lang_rank) + lang_name + '.png')
	os.chdir('..')

'''applying function'''
# Q1
q1_df = main_survey_df[['Language', 'Q1_Academic', 'Q1_Academic_Perc']]
# sorting
q1_df = q1_df.sort_values('Q1_Academic', ascending = False).reset_index(drop = True)

# iterating through each Q1 row
for tmp_i, tmp_row in q1_df.iterrows():
	# running function
	CreateLangLabelImg_fx(lang_rank = tmp_i, lang_name = tmp_row['Language'],
						  vote_percent = tmp_row['Q1_Academic_Perc'],
						  vote_count = tmp_row['Q1_Academic'],
						  q_name = 'Q1Academic')

# Q2
q2_df = main_survey_df[['Language', 'Q2_Current', 'Q2_Current_Perc']]
# sorting
q2_df = q2_df.sort_values('Q2_Current', ascending = False).reset_index(drop = True)

# iterating through each Q1 row
for tmp_i, tmp_row in q2_df.iterrows():
	# running function
	CreateLangLabelImg_fx(lang_rank = tmp_i, lang_name = tmp_row['Language'],
						  vote_percent = tmp_row['Q2_Current_Perc'],
						  vote_count = tmp_row['Q2_Current'],
						  q_name = 'Q2Current')

"""
STEP 3A: initial parallel coordinates plot
"""
# initial Parallel df
parallel_df = pd.melt(main_survey_df, id_vars = 'Language', value_vars = ['Q1_Academic_Perc', 'Q2_Current_Perc'],
                      var_name = 'QType', value_name = 'Percent')

# initial ggplot obj
parallel_ggplot = (ggplot(mapping = aes(x = 'QType', y = 'Percent', color = 'Language', group = 'Language'),
						  data = parallel_df) +
					geom_point(size = 5) +
					geom_line(size = 3) +
					scale_color_manual(values = colorhex_sortedlst, guide = False) +
					scale_x_discrete(expand = (0.05,0)) +
					scale_y_continuous(limits = (0,0.25),
									   breaks = list(np.arange(0,0.3,0.05)),
									   labels = ['{:.0%}'.format(num) for num in np.arange(0,0.3, 0.05)],
									   expand = (0.01,0)) +
					labs(title = 'Programmer Survey: Languages Academic vs. CurrentUse',
						 x = 'Question', y = 'Percentage') +
					theme_538() +
					theme(axis_title_y = element_blank()))
    
parallel_ggplot.save('parallel_ggplot.png', width = 3, height = 16, dpi = 200)

# reading the Parallel GGPlot as an Image
paraPlot_img = Image.open('parallel_ggplot.png')

# creating grey background
fullPlot_background_img = Image.new('RGBA', (1800, paraPlot_img.size[1]), '#F0F0F0')

# pasting the Paraplot onto the Background image
fullPlot_img = fullPlot_background_img.copy()
fullPlot_img.paste(paraPlot_img, box = (int(900 - (paraPlot_img.size[0]/2)), 0))

"""
STEP 3B: pasting the Lang Labels onto the sides of the plot
"""
# moving into the LanguageLabels directory
os.chdir('./LanguageLabels')

# iterating through each LangLabel, pasting the Label where it belongs on the ParaPlot
for label_fname in os.listdir():
	# defining the ImageObj of this label
	label_imageObj = Image.open(label_fname)
	
	# asdf
	if label_fname == 'Q1Academic_1Java.png':
		fullPlot_img.paste(label_imageObj, (100,130))
	elif label_fname == 'Q1Academic_2C.png':
		fullPlot_img.paste(label_imageObj, (140, 600))
	elif label_fname == 'Q1Academic_3C++.png':
		fullPlot_img.paste(label_imageObj, (120, 880))
	elif label_fname == 'Q1Academic_4Python.png':
		fullPlot_img.paste(label_imageObj, (100, 1300))
	elif label_fname == 'Q1Academic_5Assembly.png':
		fullPlot_img.paste(label_imageObj, (70, 1420))

# moving out into the main directory
os.chdir('..')
# saving fullPlot Image
fullPlot_img.save("parallel_ggplot.png")

# TOC
tt.toc()