# -*- coding: utf-8 -*-
"""
Created on 10:15 04/07/2017 

@author: Man-Machine Department NTC UWB

Produces sankey diagram using Matplotlib also uses seaborn and sets some styles so be careful when importing,
modifiead version by NTC MMI UWB, original version by

Copyright (C) 2016  Anneya Golob

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
#
# plt.rc('text', usetex=False)
# plt.rc('font', family='serif')



def sankey(before, after, colorDict={}, aspect=4, rightColor=False, orderedlabs=None, sideLabs=None, xshift=0.04,
		   yshift=.5, ax=None):
	"""
	Utility fro creating pretty sankeys diagrams, uses two data sets before and after of the same length,
	each containing list of states of individual observations , observation of the same transtion from before to after
	are grouped together and plotted as flows.

		before: data to be plotted on the left, in format [label, label, ...]
		after: data to be plotted on the right, in format [label, label, ...]
		colorDict: dictionary with colors, one for each label in before/after or orderedLabs
		aspect: to adjust vertical extend of diagram
		rightColor: true to color flows by the right columns instead of left ones
		orderedlabs: labels from before/after in desired order from bottom to top one
		sideLabs: labels (left, right) to be displayed above columns on each side
		xshift: horizontal shift of the sideLabs to adjust for different plots
		yshift: vertical shift ot the sideLabs to adjust for different plots

	"""
	df = pd.DataFrame({'before': before, 'after': after}, index=range(len(before)))

	if orderedlabs:
		allLabels = orderedlabs
	else:
		# Identify all labels that appear 'before' or 'after'
		allLabels = pd.Series(np.r_[df.before.unique(), df.after.unique()]).unique()

	# If no colorDict given, make one
	if colorDict == {}:
		pal = "hls"
		cls = sns.color_palette(pal, len(allLabels))
		for i, l in enumerate(allLabels):
			colorDict[l] = cls[i]

	# Object approach to matplotlib interface
	if ax is None:
		fig, ax = plt.subplots()

	# Determine widths of individual strips
	ns = defaultdict()
	for l in allLabels:
		myD = {}
		for l2 in allLabels:
			myD[l2] = len(df[(df.before == l) & (df.after == l2)])
		ns[l] = myD

	# Determine positions of left and right label patches and total widths
	widths = defaultdict()
	for i, l in enumerate(allLabels):
		myD = {}
		myD['left'] = len(df[df.before == l])
		myD['right'] = len(df[df.after == l])
		myD['total'] = max(myD['left'], myD['right'])
		if i == 0:
			myD['bottom'] = 0
			myD['top'] = myD['total']
			myD['leftBottom'] = 0.5 * (myD['top'] + myD['bottom']) - 0.5 * myD['left']
			myD['rightBottom'] = 0.5 * (myD['top'] + myD['bottom']) - 0.5 * myD['right']
		else:
			myD['bottom'] = widths[allLabels[i - 1]]['top'] + 0.02 * len(df)
			myD['top'] = myD['bottom'] + myD['total']
			myD['leftBottom'] = 0.5 * (myD['top'] + myD['bottom']) - 0.5 * myD['left']
			myD['rightBottom'] = 0.5 * (myD['top'] + myD['bottom']) - 0.5 * myD['right']
			topEdge = myD['top']
		widths[l] = myD

	# Total vertical extent of diagram
	xMax = topEdge / aspect

	# Draw vertical bars on left and right of each  label's section & print label
	for l in allLabels:
		ax.fill_between([-0.02 * xMax, 0], 2 * [widths[l]['leftBottom']],
						 2 * [widths[l]['leftBottom'] + widths[l]['left']], color=colorDict[l], alpha=0.99)
		ax.fill_between([xMax, 1.02 * xMax], 2 * [widths[l]['rightBottom']],
						 2 * [widths[l]['rightBottom'] + widths[l]['right']], color=colorDict[l], alpha=0.99)

		txt = str.format("{t}\n{p:.2f}%", t=l, p=df[df['before'] == l]['before'].count()/float(len(df['before']))*100)
		ax.text(-0.05 * xMax, widths[l]['leftBottom'] + 0.5 * widths[l]['left'], txt, {'ha': 'right', 'va': 'center'})
		txt = str.format("{t}\n{p:.2f}%", t=l, p=df[df['after'] == l]['after'].count() / float(len(df['before'])) * 100)
		ax.text(1.05 * xMax, widths[l]['rightBottom'] + 0.5 * widths[l]['right'], txt, {'ha': 'left', 'va': 'center'})

	# Plot strips
	for l in allLabels:
		for l2 in allLabels:
			lc = l
			if rightColor:
				lc = l2
			if ns[l][l2] == 0:
				continue
			# Create array of y values for each strip, half at left value, half at right, convolve
			ys = np.array(
				50 * [widths[l]['leftBottom'] + 0.5 * ns[l][l2]] + 50 * [widths[l2]['rightBottom'] + 0.5 * ns[l][l2]])
			ys = np.convolve(ys, 0.05 * np.ones(20), mode='valid')
			ys = np.convolve(ys, 0.05 * np.ones(20), mode='valid')

			# Update bottom edges at each label so next strip starts at the right place
			widths[l]['leftBottom'] = widths[l]['leftBottom'] + ns[l][l2]
			widths[l2]['rightBottom'] = widths[l2]['rightBottom'] + ns[l][l2]
			ax.fill_between(np.linspace(0, xMax, len(ys)), ys - 0.5 * ns[l][l2], ys + 0.5 * ns[l][l2], alpha=0.65,
							 color=colorDict[lc])

	# Draw side labels
	if sideLabs:
		if len(sideLabs) != 2:
			raise ValueError('sideLabs must be a list with exactly 2 values!')
		ax.text(-xshift, topEdge + yshift, sideLabs[0], {'ha': 'left', 'va': 'center'})
		ax.text(xMax + xshift, topEdge + yshift, sideLabs[1], {'ha': 'right', 'va': 'center'})
	ax.axis('off')

def main():
	fig, ax = plt.subplots()
	left =  [1, 1 ,1,1,2 ,2 ,3 ,1, 2, 1,2,3,3,4,4,1]
	right = [2, 2 ,2,1,3 ,1 ,1 ,1, 3, 1,4,1,3,4,2,3]

	sankey(left, right, ax=ax)
	ax.set(title="Pokus")
	plt.show()

if __name__ == '__main__':
	main()
