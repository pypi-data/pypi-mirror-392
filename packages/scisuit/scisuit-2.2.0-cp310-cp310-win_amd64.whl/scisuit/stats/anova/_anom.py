from dataclasses import dataclass
from typing import Iterable
from numbers import Real

from ctypes import py_object, c_double, c_size_t
from ..._ctypeslib import pydll as _pydll

from ...settings import roundf


_pydll.c_stat_test_anova_anom_normal.argtypes = [py_object, c_double]
_pydll.c_stat_test_anova_anom_normal.restype=py_object

_pydll.c_stat_test_anova_anom_binomial.argtypes = [py_object, c_double, c_size_t]
_pydll.c_stat_test_anova_anom_binomial.restype=py_object

_pydll.c_stat_test_anova_anom_poisson.argtypes = [py_object, c_double]
_pydll.c_stat_test_anova_anom_poisson.restype=py_object


@dataclass
class anom_result:
	_type: str
	GrandMean: Real
	CI_Low: list[Real] | Real
	CI_High: list[Real] | Real
	Values:list[Real] #averages for normal, proportions for binomial, user entries for Poisson

	def __str__(self):
		s = f"   ANOM ({self._type}) Results \n"
		s += f"Grand Mean = {roundf(self.GrandMean)} \n"

		outsiders:list[Real] = []
		positions: list[int] = []
		for i, value in enumerate(self.Values):
			LowerLimit, UpperLimit = None, None
			if isinstance(self.CI_Low, list):
				LowerLimit = self.CI_Low[i]
				UpperLimit = self.CI_High[i]
			else:
				LowerLimit = self.CI_Low
				UpperLimit = self.CI_High

			if value<LowerLimit or value>UpperLimit:
				outsiders.append(roundf(value))
				positions.append(i)
		
		if len(outsiders)>0:
			zipped = zip(outsiders, [f"loc={e}" for e in positions])
			note = "(loc>=0)." if positions[0]>0  else ""
			areis = "is" if len(positions) == 1 else "are"
			s += f"{str(list(zipped))} {areis} outside confidence limits {note}"

		return s




def anom(*args, alpha:Real=0.05, samplesize:int|None=None, type="normal")->anom_result:
	"""
	Analysis of Means (ANOM)  

	args: list(s) of real numbers (each list corresponding to a column of data)  
	alpha: Level of significance  
	samplesize: Only for binomial data otherwise must be None  
	type: "normal", "binomial" or "poisson"
	"""
	assert isinstance(alpha, Real) and alpha>0 and alpha<1, "alpha must be Real and in (0, 1)"
	assert type in ["normal", "binomial", "poisson"], "type must be 'normal', 'binomial', 'poisson'"

	if type == "normal":
		assert len(args)>2, "For normal data, at least 3 iterable objects expected."
	else:
		assert len(args)==1, "For binomial and Poisson data, exactly 1 iterable object expected."

	for v in args:
		assert isinstance(v, Iterable), "Iterable objects expected."

	if type == "binomial":
		assert isinstance(samplesize, int) and samplesize>0, "If binomial is selected, samplesize must be int and >0"

	if type == "binomial":
		res:dict = _pydll.c_stat_test_anova_anom_binomial(args, alpha, samplesize)
		return anom_result(_type=type, **res)
	elif type == "poisson":
		resPoisson:dict = _pydll.c_stat_test_anova_anom_poisson(args, alpha)
		return anom_result(_type=type, Values=args[0], **resPoisson)
	
	res:dict = _pydll.c_stat_test_anova_anom_normal(args, alpha)
	return anom_result(_type=type, **res)