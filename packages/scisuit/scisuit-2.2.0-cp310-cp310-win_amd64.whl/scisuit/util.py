import math
from numbers import Real
from typing import Iterable as _Iterable
import numpy as np
from numpy.dtypes import StringDType

from . import settings


def minmax(X:_Iterable)->tuple[Real]:
	_min = X[0]
	_max = X[0]
	for i in range(1, len(X)):
		_min = X[i] if X[i]<_min else _min
		_max = X[i] if X[i]>_max else _max
	
	return _min, _max




def to_table(data:list[list[object]], width = 3)->str:
	"""
	Takes a 2D list of different sub-list sizes and prepares a formatted output.  
	Uses `settings.NDIGITS` for number of decimal points. If no formatting is wished, set it to `None`  
	
	---
	data: A 2D list comprised of object with len function and can be converted to string  
	width: number of characters between each column   
	"""
	assert isinstance(width, int) and width>1, "width must be an integer > 1"
	assert isinstance(data, list) and isinstance(data[0], list), "data must be 2D list"

	#New List as we will modify data (it might contain sub-list of different lengths)
	DataList = [None]*len(data)
	
	maxElem = 0
	for lst in data:
		maxElem = max(maxElem, len(lst))
		
	
	for i, lst in enumerate(data):
		DataList[i] = data[i] + (maxElem-len(lst))*[""]
		if settings.NDIGITS == None:
			continue
		for j, elem in enumerate(DataList[i]):
			if isinstance(elem, float):
				DataList[i][j] = round(elem, settings.NDIGITS)

	#Array comprised of only strings
	arr_str = np.array(DataList, dtype=StringDType)
	lenfunc = np.vectorize(len)

	#Array comprised of length of each string
	arr = lenfunc(arr_str) 

	#max width for each column
	maxwidth = np.max(arr, 0) 

	LstFormat = ["{:<"+str(w + width) + "} " for w in maxwidth] #{:<10}
	strFormat = "".join(LstFormat)
	strFormat += "\n"

	return "".join([strFormat.format(*lst) for lst in DataList])



if __name__ == "__main__":
	data = [[12.36258966588, "defgh", "bbcd"], ["aaaaaaaaaaa", "bcdrfer"]]
	print(to_table(data=data, width=2, ndigits=3))

	print(data)
