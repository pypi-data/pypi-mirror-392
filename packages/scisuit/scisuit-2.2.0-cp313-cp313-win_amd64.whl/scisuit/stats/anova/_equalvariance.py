from dataclasses import dataclass
from typing import Iterable
from numbers import Real

from ctypes import py_object, c_double, c_int
from ..._ctypeslib import pydll as _pydll

from ...settings import roundf
from ...util import to_table


_pydll.c_stat_test_anova_equalvar_bartlett.argtypes = [py_object]
_pydll.c_stat_test_anova_equalvar_bartlett.restype=py_object

_pydll.c_stat_test_anova_equalvar_levene.argtypes = [py_object]
_pydll.c_stat_test_anova_equalvar_levene.restype=py_object

_pydll.c_stat_test_anova_equalvar_bonferroni.argtypes = [py_object, c_double, c_int]
_pydll.c_stat_test_anova_equalvar_bonferroni.restype=py_object



@dataclass
class bartlett_result:
	pvalue: Real
	statistic: Real

	def __str__(self):
		s = f"   Bartlett Test Results \n"
		s += f"p-value = {roundf(self.pvalue)} \n"
		s += f"statistic = {roundf(self.statistic)}"

		return s


def bartlett(*args)->bartlett_result:
	"""
	Bartlett's Test for Testing Equal Variances (Normal Data) 

	args: list(s) of real numbers (each list corresponding to a column of data)  
	"""
	for v in args:
		assert isinstance(v, Iterable), "Iterable objects expected."

	
	res:dict = _pydll.c_stat_test_anova_equalvar_bartlett(args)
	return bartlett_result(**res)





#--------------------------------------------------------------

@dataclass
class levene_result:
	pvalue: Real
	statistic: Real

	def __str__(self):
		s = f"   Levene Test Results \n"
		s += f"p-value = {roundf(self.pvalue)} \n"
		s += f"statistic = {roundf(self.statistic)}"

		return s


def levene(*args)->levene_result:
	"""
	Levene's Test for Testing Equal Variances 

	args: list(s) of real numbers (each list corresponding to a column of data)  
	"""
	for v in args:
		assert isinstance(v, Iterable), "Iterable objects expected."

	
	res:dict = _pydll.c_stat_test_anova_equalvar_levene(args)
	return levene_result(**res)






#------------------------------------------------------------------

@dataclass
class bonferroni_result:
	_isnormal: bool
	CI_lower: list[Real]
	CI_upper: list[Real]
	stdevs: list[Real]
	samplesizes: list[int]

	def __str__(self):
		s = f"   Bonferroni CIs for Standard Deviations ({'normal' if self._isnormal else 'non-normal'}) \n"
		
		Data = [["Sample", "N", "StDev", "CI"]]
		for i in range(len(self.CI_lower)):
			tbl = [
				f"Entry {i}", 
				self.samplesizes[i], 
				self.stdevs[i], 
				f"({roundf(self.CI_lower[i])}, {roundf(self.CI_upper[i])})"
			]

			Data.append(tbl)

		s += to_table(Data)

		return s


def bonferroni(*args, alpha=0.05, normal=True)->bonferroni_result:
	"""
	Bonferroni Confidence Intervals for Normal and Non-normal Data

	args: list(s) of real numbers (each list corresponding to a column of data)  
	alpha: Significance level
	normal: Is the data from a normal distribution
	"""
	for v in args:
		assert isinstance(v, Iterable), "Iterable objects expected."

	
	res:dict = _pydll.c_stat_test_anova_equalvar_bonferroni(args, c_double(alpha), c_int(0 if normal else 1))
	return bonferroni_result(**res, _isnormal=normal)