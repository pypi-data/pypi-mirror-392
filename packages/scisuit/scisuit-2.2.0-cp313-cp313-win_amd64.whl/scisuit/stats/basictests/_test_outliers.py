import numbers
from dataclasses import dataclass
from typing import Iterable
from types import FunctionType

import numpy as _np

from ctypes import py_object
from ..._ctypeslib import pydll as _pydll






_pydll.stat_outliers_grubb.argtypes = [py_object]
_pydll.stat_outliers_grubb.restype=py_object


_pydll.stat_outliers_qratio.argtypes = [py_object]
_pydll.stat_outliers_qratio.restype=py_object



# ----  Grubbs -----

@dataclass
class grubbsResult:
	statistic:float
	pvalue: float
	mean:float
	stdev: float
	maxvalue: float
	minvalue: float
	outlier: float
	outlier_pos: int

	def __str__(self):
		s = "Grubbs Test \n"
		s += f"p-value: {round(self.pvalue, 4)} \n"
		s += f"Test statistic (G-value): {round(self.statistic, 4)} \n"
		s += f"Suspected outlier={self.outlier} at index={self.outlier_pos + 1}"

		return s


def grubbs(x:Iterable[numbers.Real])->grubbsResult:
	"""
	Performs Grubbs outlier test
	"""
	assert isinstance(x, Iterable), "x must be an Iterable object"
	
	_xx = [v for v in x if isinstance(v, numbers.Real)]
	assert len(x) == len(_xx), "x must contain only Real numbers"
	
	DictObj = _pydll.stat_outliers_grubb(x)
	return grubbsResult(**DictObj)




# ------- Dixon's Q-ratio


@dataclass
class dixonqratioResult:
	statistic:float
	pvalue: float
	mean:float
	stdev: float
	maxvalue: float
	minvalue: float
	ishighest:bool
	err: str

	def __str__(self):
		s = "Dixon's Q Test \n"
		s += f"p-value: {round(self.pvalue, 4)} \n"
		s += f"Test statistic (G-value): {round(self.statistic, 4)} \n"
		s += f"Suspected outlier is the {'highest' if self.ishighest else 'lowest'} value"

		return s

	
def dixon_qratio(x:Iterable[numbers.Real])->dixonqratioResult:
	"""
	Performs Dixon's Q test
	"""
	assert isinstance(x, Iterable), "x must be an Iterable object"
	
	_xx = [v for v in x if isinstance(v, numbers.Real)]
	assert len(x) == len(_xx), "x must contain only Real numbers"
	
	DictObj = _pydll.stat_outliers_qratio(x)
	DictObj["ishighest"] = True if DictObj["ishighest"]==1 else False
	
	return dixonqratioResult(**DictObj)
