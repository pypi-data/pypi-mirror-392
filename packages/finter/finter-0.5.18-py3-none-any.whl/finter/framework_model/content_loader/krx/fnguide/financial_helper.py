import pandas as pd
import polars as pl


def subtract_quarters(fiscal_col, n):
    """
    분기를 빼는 함수

    Args:
        fiscal_col: YYYYQQ 형식의 fiscal column
        n: 빼려는 분기 수

    Returns:
        n개 분기 이전의 fiscal
    """
    year = fiscal_col // 100
    quarter = fiscal_col % 100
    total_quarters = year * 4 + quarter - n
    new_year = (total_quarters - 1) // 4
    new_quarter = ((total_quarters - 1) % 4) + 1
    return new_year * 100 + new_quarter


def calculate_rolling_quarters(
    df: pd.DataFrame, quarters: int = 4, operation: str = "mean"
) -> pd.DataFrame:
    """
    rolling n분기 계산을 위한 helper 함수

    Args:
        df: pandas DataFrame (wide format with nested dict values)
        quarters: 계산할 분기 개수 (기본값: 4)
        operation: 집계 방식 ('mean', 'sum', 'diff', 'last')
            - 'mean': n개 분기 평균
            - 'sum': n개 분기 합계
            - 'diff': 최근 분기 - n분기 전 값
            - 'last': n분기 전 값 (quarters=0이면 현재 분기 값)

    Returns:
        pandas DataFrame (wide format: pit index, id columns, rolling values)
    """
    # 1. pandas DataFrame을 long format으로 변환
    rows = []
    for idx, value in df.stack().items():
        if isinstance(value, dict):
            for fiscal, amount in value.items():
                rows.append((*idx, fiscal, amount))
        elif pd.notna(value):
            rows.append((*idx, None, value))

    df_long = pd.DataFrame(rows, columns=["pit", "id", "fiscal", "value"])

    # 2. polars로 변환
    df_long_pl = pl.from_pandas(df_long)

    # 3. fiscal이 null인 행 제거 및 중복 제거
    df_long_pl = df_long_pl.filter(pl.col("fiscal").is_not_null()).unique(
        subset=["id", "pit", "fiscal"], keep="last"
    )

    # 4. cummax_fiscal 계산
    df_base = df_long_pl.sort(["id", "pit"]).with_columns(
        [pl.col("fiscal").cum_max().over("id").alias("cummax_fiscal")]
    )

    # 5. 각 분기별로 처리해서 리스트에 저장
    q_dfs = []

    # last operation에서 quarters=0을 지원하기 위해 최소 1개는 계산
    n_quarters_to_calc = max(quarters, 1) if operation == "last" else quarters

    for i in range(n_quarters_to_calc):
        # target fiscal 계산
        df_temp = df_base.select(["id", "pit", "cummax_fiscal"]).with_columns(
            [subtract_quarters(pl.col("cummax_fiscal"), i).alias("target_fiscal")]
        )

        # self-join
        df_joined = df_temp.join(
            df_base.select(["id", "pit", "fiscal", "value"]),
            left_on=["id", "target_fiscal"],
            right_on=["id", "fiscal"],
            how="left",
            suffix="_right",
        )

        # 현재 pit 이하 중 최대값
        df_q = (
            df_joined.filter(
                (pl.col("pit_right") <= pl.col("pit")) | pl.col("pit_right").is_null()
            )
            .group_by(["id", "pit"])
            .agg([pl.col("value").max().alias(f"q{i}")])
        )

        q_dfs.append(df_q)

    # 6. 원본에 순차적으로 join
    df_result = df_base
    for df_q in q_dfs:
        df_result = df_result.join(df_q, on=["id", "pit"], how="left")

    # 7. 집계 계산
    col_name = f"rolling_{operation}_{quarters}q"

    if operation == "mean":
        # 평균
        sum_expr = pl.col("q0")
        for i in range(1, quarters):
            sum_expr = sum_expr + pl.col(f"q{i}")
        df_result = df_result.with_columns([(sum_expr / quarters).alias(col_name)])

    elif operation == "sum":
        # 합계
        sum_expr = pl.col("q0")
        for i in range(1, quarters):
            sum_expr = sum_expr + pl.col(f"q{i}")
        df_result = df_result.with_columns([sum_expr.alias(col_name)])

    elif operation == "diff":
        # 차이: 최근 분기(q0) - n분기 전(q{n-1})
        df_result = df_result.with_columns(
            [(pl.col("q0") - pl.col(f"q{quarters - 1}")).alias(col_name)]
        )

    elif operation == "last":
        # n분기 전 값 (quarters=0이면 현재 분기 값)
        if quarters == 0:
            df_result = df_result.with_columns([pl.col("q0").alias(col_name)])
        else:
            df_result = df_result.with_columns([pl.col(f"q{quarters - 1}").alias(col_name)])

    else:
        raise ValueError(
            f"operation must be one of ['mean', 'sum', 'diff', 'last'], got '{operation}'"
        )

    # 8. wide format으로 변환
    df_wide = (
        df_result.select(["pit", "id", col_name])
        .unique(subset=["pit", "id"], keep="first")
        .pivot(index="pit", on="id", values=col_name)
        .sort("pit")
    )

    # 9. forward fill
    df_filled = df_wide.with_columns([pl.all().forward_fill(limit=500)])

    # 10. columns를 int로 변환
    df_pandas = df_filled.to_pandas().set_index("pit")
    df_pandas.columns = df_pandas.columns.astype(int)

    return df_pandas


def calculate_rolling_4q(df: pd.DataFrame) -> pd.DataFrame:
    """
    backward compatibility를 위한 wrapper 함수

    Args:
        df: pandas DataFrame (wide format with nested dict values)

    Returns:
        pandas DataFrame (wide format: pit index, id columns, rolling_mean_4q values)
    """
    return calculate_rolling_quarters(df, quarters=4, operation="mean")


if __name__ == "__main__":
    from finter.data import ContentFactory

    cf = ContentFactory("kr_stock", 20230101, 20250101)

    df = cf.get_df("krx-spot-total_assets")

    print(calculate_rolling_quarters(df, quarters=4, operation="mean"))
    print(calculate_rolling_quarters(df, quarters=4, operation="sum"))
    print(calculate_rolling_quarters(df, quarters=4, operation="diff"))
