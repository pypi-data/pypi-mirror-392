from dataclasses import dataclass
from typing import Iterable

from ctypes import py_object, c_double, c_char_p, c_size_t
from ..._ctypeslib import pydll as _pydll

from ...settings import roundf

_pydll.stat_essential_vartest_onesample.argtypes = [py_object, c_double, c_double, c_char_p, c_size_t]
_pydll.stat_essential_vartest_onesample.restype = py_object

_pydll.stat_essential_vartest_twosample.argtypes = [py_object, py_object, c_double, c_double, c_char_p, c_size_t]
_pydll.stat_essential_vartest_twosample.restype = py_object




@dataclass
class testvar_onesample_Result:
	_method: int
	pvalue:float
	statistic:float | None #computed value
	df:int|None
	var:float
	CI_lower:float 
	CI_upper:float
	alternative:str

	def __str__(self):
		DF = f"def={self.df}, " if self._method == 0 else ""

		s = "    One-Sample Variance Test for " + self.alternative + "\n"
		s += f"{DF}var={roundf(self.var)} \n"
		s += f"statistic={roundf(self.statistic)} \n" if self._method == 0 else ""
		s += f"p-value ={roundf(self.pvalue)} \n"
		s += f"Confidence interval (std): ({roundf(self.CI_lower)}, {roundf(self.CI_upper)})"

		return s




@dataclass
class testvar_twosample_Result:
	pvalue:float
	statistic:float #computed value
	df1:int
	df2:int
	var1:float
	var2:float
	CI_lower:float 
	CI_upper:float
	alternative:str

	
	def __str__(self):
		s = "    Two-Sample Variance Testfor " + self.alternative + "\n"
		s += f"df1={self.df1}, df2={self.df2}, var1={roundf(self.var1)}, var2={roundf(self.var2)} \n"
		s += f"statistic={roundf(self.statistic)} \n"
		s += f"p-value ={roundf(self.pvalue)} \n"
		s += f"Confidence interval: ({roundf(self.CI_lower)}, {roundf(self.CI_upper)})"

		return s






def test_variance(
		x:Iterable, 
		y:Iterable|None = None, 
		hypothesized:float|None = None, 
		ratio:float|None = 1.0,
		alternative:str = "two.sided", 
		conflevel:float = 0.95,
		method:int = 0)->testvar_onesample_Result | testvar_twosample_Result:
	"""
	Performs One or Two Sample Variance Test 

	## Input
	x: First sample  
	y: Second sample (optional)  
	alternative: "two.sided", "less", "greater"  
	ratio: Assumed ratio of variances of the samples (two-sample)  
	hypothesized: Assumed standard deviation of the sample (one-sample)  
	conflevel: Confidence level, [0,1]  
	method: One-sample (chisq:0, bonett:1), Two-sample (f-test:0, bonett-seier:1)
	"""
	assert conflevel>=0.0 or conflevel <= 1.0, "conflevel must be in range (0, 1)"
	assert isinstance(x, Iterable), "x must be Iterable"
	
	assert isinstance(alternative, str), "alternative must be str"
	assert isinstance(method, int), "method must be int"


	if y == None:
		assert isinstance(hypothesized, float), "hypothesized must be float"
		dct = _pydll.stat_essential_vartest_onesample(
			x, 
			c_double(hypothesized), 
			c_double(conflevel), 
			c_char_p(alternative.encode()), 
			c_size_t(method))
		
		if method == 1:
			dct["df"] = None
			dct["statistic"] = None
		
		return testvar_onesample_Result(alternative=alternative, _method=method, **dct)
	

	# y!=None
	if method == 0:
		assert isinstance(ratio, float), "ratio must be float"

	assert isinstance(y, Iterable), "y must be Iterable"

	dct = _pydll.stat_essential_vartest_twosample(
			x, 
			y,
			c_double(ratio if isinstance(ratio, float) else 1.0), 
			c_double(conflevel), 
			c_char_p(alternative.encode()), 
			c_size_t(method))
	
	return testvar_twosample_Result(alternative=alternative, **dct)
