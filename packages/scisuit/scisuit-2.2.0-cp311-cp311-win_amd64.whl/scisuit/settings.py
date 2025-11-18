NDIGITS = 4
"""
Number of decimal points to be used when rounding a floating number (used during outputs)
"""

def roundf(x:float)->float:
	"""
	A convenience function   
	Uses package's global decimal point precision to round the float
	"""
	if isinstance(x, int):
		return x

	assert isinstance(x, float), "x must be float"
	return round(x, NDIGITS)