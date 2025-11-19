from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

from finter.data.content_model.usage import QUARTERS_USAGE_TEXT
from finter.framework_model.content import Loader
from finter.framework_model.content_loader.krx.fnguide.financial_helper import (
    calculate_rolling_4q,
    calculate_rolling_quarters,
)

initial_date = 20000101


def safe_apply_fiscal(x):
    if pd.isna(x):
        return x
    return max(x.keys())


def safe_apply_value(x):
    if pd.isna(x):
        return x
    return x[max(x.keys())]


def slice_df(df, start, end):
    return df.dropna(how="all").loc[
        datetime.strptime(str(start), "%Y%m%d") : datetime.strptime(str(end), "%Y%m%d")
    ]


class KrFinancialLoader(Loader):
    def __init__(self, cm_name):
        self.__CM_NAME = cm_name
        self.__FREQ = cm_name.split(".")[-1]

    @staticmethod
    def quarters_usage():
        """quarters 파라미터 사용법을 출력합니다."""
        print(QUARTERS_USAGE_TEXT)

    @staticmethod
    def _filter_dup_val(s, pair, k_lst=[]):
        if isinstance(s, pd.Series):
            key_list = []
            return s.apply(
                lambda x: KrFinancialLoader._filter_dup_val(x, pair, key_list)
            )
        elif isinstance(s, dict):
            val = {}
            for k, v in s.items():
                if pair and ([k, v] not in k_lst):
                    k_lst.append([k, v])
                    val[k] = s[k]
                elif not pair and (k not in k_lst):
                    k_lst.append(k)
                    val[k] = s[k]
            return val

    def get_df(
        self,
        start: int,
        end: int,
        fill_nan=True,
        preprocess_type: str = None,
        dataguide_ccid=False,
        quarters=None,
        *args,
        **kwargs,
    ):
        # quarters 파라미터 처리
        if quarters is not None:
            if preprocess_type is not None:
                raise ValueError(
                    "Cannot use both 'quarters' and 'preprocess_type' parameters together"
                )

            # quarters 파라미터 파싱
            if isinstance(quarters, tuple) and len(quarters) == 2:
                n_quarters, operation = quarters
            else:
                raise ValueError(
                    "quarters must be tuple (quarters, operation). "
                    "Example: quarters=(4, 'mean'). "
                    "Use cf.usage(item_name) for more details."
                )

            # 2년 앞당긴 start로 데이터 로드 (forward fill limit 500을 위해)
            start_date = datetime.strptime(str(start), "%Y%m%d")
            prestart_date = start_date - relativedelta(years=2)
            prestart = int(prestart_date.strftime("%Y%m%d"))
            raw = self._load_cache(
                self.__CM_NAME,
                prestart,
                end,
                freq=self.__FREQ,
                fill_nan=False,
                *args,
                **kwargs,
            )
            raw = slice_df(raw, prestart, end)
            result = calculate_rolling_quarters(
                raw, quarters=n_quarters, operation=operation
            )

            result = slice_df(result, start, end)

            if fill_nan and not result.empty:
                result.iloc[-1] = np.nan
            return result

        raw = self._load_cache(
            self.__CM_NAME,
            initial_date,
            end,
            freq=self.__FREQ,
            fill_nan=fill_nan,
            *args,
            **kwargs,
        )
        if preprocess_type == "unpivot":
            raw = slice_df(raw, start, end)
            unpivot_df = raw.unstack().dropna().reset_index()
            unpivot_df.columns = ["id", "pit", "val"]
            m = (
                pd.DataFrame([*unpivot_df["val"]], unpivot_df.index)
                .stack()
                .rename_axis([None, "fiscal"])
                .reset_index(1, name="value")
            )
            result = unpivot_df[
                [
                    "id",
                    "pit",
                ]
            ].join(m)
            return result

        elif preprocess_type == "default":
            max_fiscal = raw.applymap(safe_apply_fiscal).astype(float)
            raw = raw.applymap(safe_apply_value)
            raw = raw[max_fiscal == max_fiscal.cummax()]
            raw = slice_df(raw, start, end)

        elif preprocess_type == "duplicated_pair":
            raw = slice_df(raw, start, end)
            raw = raw.apply(lambda x: KrFinancialLoader._filter_dup_val(x, pair=True))
            raw = raw.where(raw.astype(bool))

        elif preprocess_type == "duplicated_fiscal":
            raw = slice_df(raw, start, end)
            raw = raw.apply(lambda x: KrFinancialLoader._filter_dup_val(x, pair=False))
            raw = raw.where(raw.astype(bool))

        elif preprocess_type == "rolling_4q":
            raw = slice_df(raw, start, end)
            return calculate_rolling_4q(raw)

        else:
            raw = slice_df(raw, start, end)

        # todo: check if remove id convert logic in parquet
        return raw.dropna(how="all")
        # return (
        #     raw
        #     if kwargs.get("code_format")
        #     else fnguide_entity_id_to_dataguide_ccid(raw)
        # ).dropna(how="all")
