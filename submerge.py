#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Tao Chen <pro711@gmail.com>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


'''
Merge two subtitles into a single file.
'''

import sys
import pysrt

############################################
# Parameters
############################################

# The max time difference of two lines
SLACK = 500
# Whether combine each language into a single line
JOIN_LINES = True

def srttime_to_ms(t):
	'Convert srttime object to number of milliseconds.'
	return 1000*(t.hours*3600+t.minutes*60+t.seconds)+t.milliseconds

def indicator(d):
	if abs(d) < SLACK:
		return 0
	elif d > 0:
		return 1
	else:
		return -1

def timediff_to_indicator(std, etd):
	'''Indicator function for time difference'''
	std = srttime_to_ms(std)
	etd = srttime_to_ms(etd)
	if abs(std) + abs(etd) < 2 * SLACK:
		return (0, 0)
	else:
		return (indicator(std), indicator(etd))

def compare_srtitem(a, b):
	'''
	Compare two subtitle items to determine precedence.
	Returns: a tuple indicating the relative precedence of 
	the start and end of two items.
	'''
	# perfect match
	if a.start == b.start and a.end == b.end:
		return (0, 0)
	# fuzzy match
	std = a.start-b.start
	etd = a.end-b.end
	
	return timediff_to_indicator(std, etd)

def merge_lines(*lines):
	subs = []
	for line in lines:
		if JOIN_LINES:
			line = line.replace('\n', ' ')
		subs.append(line)
	return '\n'.join(subs)

def merge(sub1, sub2):
	try:
		sub1 = pysrt.SubRipFile.open(sub1)
	except UnicodeDecodeError:
		sub1 = pysrt.SubRipFile.open(sub1, encoding='GBK')

	try:
		sub2 = pysrt.SubRipFile.open(sub2)
	except UnicodeDecodeError:
		sub2 = pysrt.SubRipFile.open(sub2, encoding='GBK')
	n_sub1 = len(sub1)
	n_sub2 = len(sub2)
	# merged subtitle
	subm = pysrt.SubRipFile()
	i = 0
	j = 0
	k = 0
	while (i < n_sub1 and j < n_sub2):
		a = sub1[i]
		b = sub2[j]
		(si, ei) = compare_srtitem(a, b)
		if (si == 0 and ei == 0):
			item = pysrt.SubRipItem(start=a.start, end=a.end, text=merge_lines(a.text, b.text))
			subm.append(item)
			i = i + 1
			j = j + 1
		elif (si == 0 and ei == -1):
			a_next = sub1[i+1]
			if compare_srtitem(a_next, b)[1] == 0:
				# combine two items of sub1
				text1 = a.text + ' ' + a_next.text
				text2 = b.text
				item = pysrt.SubRipItem(start=b.start, end=b.end, text=merge_lines(text1, text2))
				subm.append(item)
				i = i + 2
				j = j + 1
			else:
				item = pysrt.SubRipItem(start=a.start, end=a.end, text=a.text)
				subm.append(item)
				i = i + 1
		elif (si == 0 and ei == 1):
			b_next = sub2[j+1]
			if compare_srtitem(a, b_next)[1] == 0:
				# combine two items of sub1
				text1 = a.text
				text2 = b.text + ' ' + b_next.text
				item = pysrt.SubRipItem(start=a.start, end=a.end, text=merge_lines(text1, text2))
				subm.append(item)
				i = i + 1
				j = j + 2
			else:
				item = pysrt.SubRipItem(start=b.start, end=b.end, text=b.text)
				subm.append(item)
				j = j + 1
		elif (si < 0):
			item = pysrt.SubRipItem(start=a.start, end=a.end, text=a.text)
			subm.append(item)
			i = i + 1
		else:
			item = pysrt.SubRipItem(start=b.start, end=b.end, text=b.text)
			subm.append(item)
			j = j + 1
	# add any lines left
	if i < n_sub1:
		subm.extend(sub1[i:])
	if j < n_sub2:
		subm.extend(sub2[j:])
	# correct indexes
	subm.clean_indexes()
	# write output file
	subm.save('merged.srt')

def main(sub1, sub2):
	merge(sub1, sub2)

if __name__ == '__main__':
	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print 'Usage: '+sys.argv[0]+' sub1.srt sub2.srt'
