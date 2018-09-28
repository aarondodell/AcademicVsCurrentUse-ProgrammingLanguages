import os
import textwrap
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
STEP 2: defining Create Language Label Image
"""
def CreateLangLabelImg_fx(lang_rank, lang_name, vote_percent, vote_count, q_name, tmp_imageObj_dict):
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
		if lang_title_fnt.getsize(lang_title_str)[1] <= 110:
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
		if lang_voteperc_fnt.getsize(lang_voteperc_str)[1] <= 70:
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
		if lang_votecount_fnt.getsize(lang_votecount_str)[1] <= 60:
			break	
	
	# defining Lang VoteCount Size
	lang_votecount_size = lang_votecount_fnt.getsize(lang_votecount_str)
	
	'''White Background creation'''
	# determining the width
	# first, find the longer length between the Title, Perc, and Count
	farthest_x = max([lang_title_size[0], lang_voteperc_size[0] + lang_votecount_size[0] + 20])
	
	# creating Background Size, picking between Farthest Title or Count for the X width
	background_size = (farthest_x + 215, 190)
		
	# creating white background
	background_img = Image.new('RGBA', background_size, 'white')
	# adding border
	if 'JavaScript' in lang_name or 'SQL' in lang_name:
		background_img = ImageOps.expand(background_img, border = 3, fill = lang_color)
		background_img = ImageOps.expand(background_img, border = 2, fill = '#3f3f3f')
	else:
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
	
	# drawing black outlines for JavaScript and SQL
	if 'JavaScript' in lang_name or 'SQL' in lang_name:
		for tmp_text_pos, tmp_text_str, tmp_fnt in zip([(200, 5), (220, 105), (240 + lang_voteperc_size[0], 125)],
													   [lang_title_str, lang_voteperc_str, lang_votecount_str],
													   [lang_title_fnt, lang_voteperc_fnt, lang_votecount_fnt]):
			for position_tup in (list(it.product(np.arange(tmp_text_pos[0] - 3, tmp_text_pos[0] + 4), [tmp_text_pos[1] + 1])) +	#bottom border
								 list(it.product(np.arange(tmp_text_pos[0] - 1, tmp_text_pos[0] + 2), [tmp_text_pos[1] + 2])) +	#bottom border extra
								 list(it.product(np.arange(tmp_text_pos[0] - 3, tmp_text_pos[0] + 4), [tmp_text_pos[1] - 1])) +	#top border
								 list(it.product(np.arange(tmp_text_pos[0] - 1, tmp_text_pos[0] + 2), [tmp_text_pos[1] - 2])) +	#top border extra
								 list(it.product([tmp_text_pos[0] - 1], np.arange(tmp_text_pos[1] -3, tmp_text_pos[1] +4))) +	#left border
								 list(it.product([tmp_text_pos[0] - 2], np.arange(tmp_text_pos[1] -1, tmp_text_pos[1] +2))) +	#left border extra
								 list(it.product([tmp_text_pos[0] + 1], np.arange(tmp_text_pos[1] -3, tmp_text_pos[1] +4))) +	#right border
								 list(it.product([tmp_text_pos[0] + 2], np.arange(tmp_text_pos[1] -1, tmp_text_pos[1] +2)))):	#right border extra
				# drawing black shift
				full_draw.text(position_tup, tmp_text_str, fill = '#3f3f3f', font = tmp_fnt)
	# drawing colored center for title
	full_draw.text(lang_title_position, lang_title_str, fill = lang_color, font = lang_title_fnt)
	
	# drawing Lang VotePerc
	full_draw.text((220, 5 + 100), lang_voteperc_str, fill = lang_color, font = lang_voteperc_fnt)
	
	# drawing Lang VoteCount
	full_draw.text((240 + lang_voteperc_size[0], 5 + 120), lang_votecount_str, fill = lang_color, font = lang_votecount_fnt)
	
	# adding the image obj to the Dict
	tmp_imageObj_dict[q_name + '_' + lang_name] = full_img
	
	# returning the Image Obj dict
	return tmp_imageObj_dict

'''applying function'''
#creating the Image Object dict
labels_imageObj_dict = {}

# Q1
q1_df = main_survey_df[['Language', 'Q1_Academic', 'Q1_Academic_Perc']]
# sorting
q1_df = q1_df.sort_values('Q1_Academic', ascending = False).reset_index(drop = True)

# iterating through each Q1 row
for tmp_i, tmp_row in q1_df.iterrows():
	# running function
	labels_imageObj_dict = CreateLangLabelImg_fx(lang_rank = tmp_i, lang_name = tmp_row['Language'],
												 vote_percent = tmp_row['Q1_Academic_Perc'],
												 vote_count = tmp_row['Q1_Academic'],
												 q_name = 'Q1Academic',
												 tmp_imageObj_dict = labels_imageObj_dict)

# Q2
q2_df = main_survey_df[['Language', 'Q2_Current', 'Q2_Current_Perc']]
# sorting
q2_df = q2_df.sort_values('Q2_Current', ascending = False).reset_index(drop = True)

# iterating through each Q1 row
for tmp_i, tmp_row in q2_df.iterrows():
	# running function
	labels_imageObj_dict = CreateLangLabelImg_fx(lang_rank = tmp_i, lang_name = tmp_row['Language'],
												 vote_percent = tmp_row['Q2_Current_Perc'],
												 vote_count = tmp_row['Q2_Current'],
												 q_name = 'Q2Current',
												 tmp_imageObj_dict = labels_imageObj_dict)

"""
STEP 3A: initial parallel coordinates plot
"""
# initial Parallel df
parallel_df = pd.melt(main_survey_df, id_vars = 'Language', value_vars = ['Q1_Academic_Perc', 'Q2_Current_Perc'],
                      var_name = 'QType', value_name = 'Percent')
# nudging the tie apart a bit
parallel_df.loc[parallel_df.index[parallel_df['Language'] == 'Java'], 'Percent'] += 0.001
parallel_df.loc[parallel_df.index[parallel_df['Language'] == 'JavaScript'], 'Percent'] -= 0.001

# creating the PercentLabels_df
percentLabels_df = pd.DataFrame(data = {'y_position': list(np.arange(0, 0.26, 0.05)) * 2, 
										'x_position': np.repeat(['Q1_Academic_Perc', 'Q2_Current_Perc'], 6)})
percentLabels_df['my_label'] = (percentLabels_df['y_position']*100).astype(int).astype(str) + "%"

# creating the QuestionStrings
questionStrings_lst = ['"Languages formally taught\nin School or University?"',
				 '"Languages you Currently\nUse on a regular basis?"']

# initial ggplot obj
parallel_ggplot = (ggplot(mapping = aes(x = 'QType', y = 'Percent'),
						  data = parallel_df) +
				   geom_text(mapping = aes(x = 'x_position', y = 'y_position', label = 'my_label'),
							 data = percentLabels_df,
							 ha = 'right', va = 'bottom',
							 size = 20, fontstyle = 'oblique',
							 nudge_x = -0.05) +
				   geom_line(data = parallel_df[parallel_df['Language'].isin(['JavaScript','SQL'])],
							 mapping = aes(group = 'Language'), color = 'black', size = 4.5) +
				   geom_line(mapping = aes(color = 'Language', group = 'Language'), size = 3.5) +
				   geom_point(size = 7, color = 'black') +
				   geom_point(mapping = aes(color = 'Language', group = 'Language'), size = 6) +
				   scale_color_manual(values = colorhex_sortedlst, guide = False) +
				   scale_x_discrete(expand = (0.05,0)) +
				   scale_y_continuous(limits = (0,0.25),
									  breaks = list(np.arange(0,0.3,0.05)),
									  expand = (0.02,0)) +
				   labs(title = 'Programmer Survey:\nWhich Languages were Learned in School\ncompared to those in Current Use',
						x = 'Question', y = 'Percentage') +
				   theme_538() +
				   theme(axis_title_y = element_blank(), axis_text_y = element_blank(),
						 axis_title_x = element_blank(), axis_text_x = element_blank(),
						 panel_grid = element_line(color = 'black'), panel_grid_minor_y = element_blank(),
						 plot_title = element_text(size = 30)))
    
parallel_ggplot.save('parallel_ggplot.png', width = 3, height = 22, dpi = 200)

# reading the Parallel GGPlot as an Image
paraPlot_img = Image.open('parallel_ggplot.png')

# creating grey background
fullPlot_background_img = Image.new('RGBA', (2700, paraPlot_img.size[1] + 270), '#F0F0F0')

# pasting the Paraplot onto the Background image
fullPlot_img = fullPlot_background_img.copy()
fullPlot_img.paste(paraPlot_img, box = (int(1350 - (paraPlot_img.size[0]/2)), 0))

"""
STEP 3B: pasting the Lang Labels onto the sides of the plot
then Lines
pasting Question text
"""
''' Lang Labels '''
# defining the qAndLang To PlotPosition dict
qAndLang_to_plotYPosition_dict = {'Q1Academic_Java': 330, 'Q1Academic_C': 1130,
								  'Q1Academic_C++': 1590, 'Q1Academic_Python': 1850,
								  'Q1Academic_Assembly' : 2100, 'Q1Academic_MATLAB': 2350,
								  'Q1Academic_C#': 2580, 'Q1Academic_JavaScript': 2810,
								  'Q1Academic_SQL': 3040, 'Q1Academic_PHP': 3270,
								  'Q2Current_Python': 675,  'Q2Current_Java':1165,
								  'Q2Current_JavaScript': 1365, 'Q2Current_C++': 1890,
								  'Q2Current_C': 2220, 'Q2Current_C#': 2450,
								  'Q2Current_SQL': 2680, 'Q2Current_PHP': 2910,
								  'Q2Current_Assembly': 3140, 'Q2Current_MATLAB': 3340}

# iterating through each LangLabel image, pasting the Label where it belongs on the ParaPlot
for qAndLang_str, label_imageObj in labels_imageObj_dict.items():
	# plotting Label onto image
	try:
		if 'Academic' in qAndLang_str:
			fullPlot_img.paste(label_imageObj,
							   (1040 - label_imageObj.size[0] ,qAndLang_to_plotYPosition_dict[qAndLang_str]))
		elif 'Current' in qAndLang_str:
			fullPlot_img.paste(label_imageObj,
							   (1670 ,qAndLang_to_plotYPosition_dict[qAndLang_str]))
	except KeyError:
		print(f'{qAndLang_str} missing')

'''Lines to labels '''
# creating draw object
fullPlot_draw = ImageDraw.Draw(fullPlot_img)

# defining Q1 LineToLabels DataFrame
q1_lineToLabels_df = pd.DataFrame({"Language": [lang for lang in q1_df['Language'] if lang in
												['Python', 'Assembly', 'MATLAB', 'C#', 'JavaScript', 'SQL', 'PHP']],
								   'Color': [colors_ref.at[lang, 'color'] for lang in q1_df['Language']
											 if lang in ['Python', 'Assembly', 'MATLAB', 'C#', 'JavaScript', 'SQL', 'PHP']],
								   'Start_xy': [(1050, y_pos + 100) for y_pos in
												[qAndLang_to_plotYPosition_dict['Q1Academic_{}'.format(lang)] for lang in q1_df['Language'] if lang in
												 ['Python', 'Assembly', 'MATLAB', 'C#', 'JavaScript', 'SQL', 'PHP']]],
								   'End_xy': [(1120, y_pos) for y_pos in 
											  [2180, 2400, 2800, 2910, 2970, 3030, 3060]]})
# plotting each line
for tmp_i, tmp_row in q1_lineToLabels_df.iterrows():
	fullPlot_draw.line(xy = [tmp_row['Start_xy'], tmp_row['End_xy']], fill = tmp_row['Color'], width = 8)

# defining Q2 LineTOLabels DF
q2_lineToLabels_df = pd.DataFrame({"Language": [lang for lang in q2_df['Language'] if lang in ['Assembly', 'MATLAB']],
								   'Color': [colors_ref.at[lang, 'color'] for lang in q2_df['Language'] if lang in ['Assembly', 'MATLAB']],
								   'Start_xy': [(1660, y_pos) for y_pos in [3200, 3450]],
								   'End_xy': [(1510, y_pos + 100) for y_pos in
												[qAndLang_to_plotYPosition_dict['Q2Current_{}'.format(lang)] for lang in q2_df['Language'] if lang in
												 ['Assembly', 'MATLAB']]]})
# plotting each line
for tmp_i, tmp_row in q2_lineToLabels_df.iterrows():
	fullPlot_draw.line(xy = [tmp_row['Start_xy'], tmp_row['End_xy']], fill = tmp_row['Color'], width = 8)

'''Questions X Axis '''
# defining font
question_xaxis_fnt = ImageFont.truetype('ARLRDBD.TTF', 70)

'''Q1'''
# defining Question1 _Position
question1_position = (200,3600)
# defining Q1 Str
question1_textstr = textwrap.fill("What languages were you formally taught in school or University?", width = 26)

# drawing black background
for position_tup in (list(it.product(np.arange(question1_position[0] - 3, question1_position[0] + 4), [question1_position[1] + 1])) +	#bottom border
					 list(it.product(np.arange(question1_position[0] - 1, question1_position[0] + 2), [question1_position[1] + 2])) +	#bottom border extra
					 list(it.product(np.arange(question1_position[0] - 3, question1_position[0] + 4), [question1_position[1] - 1])) +	#top border
					 list(it.product(np.arange(question1_position[0] - 1, question1_position[0] + 2), [question1_position[1] - 2])) +	#top border extra
					 list(it.product([question1_position[0] - 1], np.arange(question1_position[1] -3, question1_position[1] +4))) +	#left border
					 list(it.product([question1_position[0] - 2], np.arange(question1_position[1] -1, question1_position[1] +2))) +	#left border extra
					 list(it.product([question1_position[0] + 1], np.arange(question1_position[1] -3, question1_position[1] +4))) +	#right border
					 list(it.product([question1_position[0] + 2], np.arange(question1_position[1] -1, question1_position[1] +2)))):	#right border extra
	# drawing black shift
	fullPlot_draw.text(position_tup, question1_textstr, fill = '#3f3f3f', font = question_xaxis_fnt)

# drawing White Center
# fullPlot_draw.text(question1_position, question1_textstr, fill = 'white', font = question_xaxis_fnt)

'''Q2'''
# defining Question1 _Position
question2_position = (1700,3600)
# defining Q1 Str
question2_textstr = textwrap.fill(
		"What languages are you currently the most familiar with, and use on a regular basis?", width = 26)

# drawing black background
for position_tup in (list(it.product(np.arange(question2_position[0] - 3, question2_position[0] + 4), [question2_position[1] + 1])) +	#bottom border
					 list(it.product(np.arange(question2_position[0] - 1, question2_position[0] + 2), [question2_position[1] + 2])) +	#bottom border extra
					 list(it.product(np.arange(question2_position[0] - 3, question2_position[0] + 4), [question2_position[1] - 1])) +	#top border
					 list(it.product(np.arange(question2_position[0] - 1, question2_position[0] + 2), [question2_position[1] - 2])) +	#top border extra
					 list(it.product([question2_position[0] - 1], np.arange(question2_position[1] -3, question2_position[1] +4))) +	#left border
					 list(it.product([question2_position[0] - 2], np.arange(question2_position[1] -1, question2_position[1] +2))) +	#left border extra
					 list(it.product([question2_position[0] + 1], np.arange(question2_position[1] -3, question2_position[1] +4))) +	#right border
					 list(it.product([question2_position[0] + 2], np.arange(question2_position[1] -1, question2_position[1] +2)))):	#right border extra
	# drawing black shift
	fullPlot_draw.text(position_tup, question2_textstr, fill = '#3f3f3f', font = question_xaxis_fnt)

# drawing White Center
# fullPlot_draw.text(question2_position, question2_textstr, fill = 'white', font = question_xaxis_fnt)

# saving fullPlot Image
fullPlot_img.save("parallel_ggplot.png")

# TOC
tt.toc()