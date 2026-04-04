# Was going to be used in a project. May revisit at a later date.

import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from typing import Literal

def formula_change(_formula: str, _predictors:list, _outcome:str,_itr:int) -> str:
    if _formula == "":
        _formula = f"{_outcome} ~ {_predictors[0]}"
    else:
        _formula = _formula + f" + {_predictors[_itr]}"
    return _formula

def hierarchical_model(_dataframe:pd.DataFrame,
                   _outcome:str,
                   _predictors:list[str],
                   _cov_type:Literal["nonrobust", "HC0", "HC1", "HC2", "HC3",
                                     "HAC", "hac-panel", "hac-groupsum", "cluster"] = "nonrobust") -> list:

    itr:int = 0
    _model:sm.regression.linear_model.RegressionResultsWrapper
    _model_list = []
    _formula:str = ""

    _formula = formula_change(_formula,_predictors,_outcome,itr)
    
    while itr<len(_predictors):
        if itr==0:
            _model = smf.ols(formula=_formula,data=_dataframe).fit(cov_type=_cov_type)
            _model_list.append(_model)
            itr += 1
            _formula = formula_change(_formula,_predictors,_outcome,itr)

        model_itr = smf.ols(formula=_formula, data=_dataframe).fit(cov_type=_cov_type)
        _model = model_itr
        _model_list.append(_model)
        itr += 1
        if itr == len(_predictors):
            break
        _formula = formula_change(_formula,_predictors,_outcome,itr)

    return _model_list