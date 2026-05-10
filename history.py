import sys
import pandas as pd

def simulate_starry_pro(monthly_contribution=1000, annual_returns=None, years=20):
    """
    annual_returns: 列表或数组，长度为 years，每个元素代表该年的年化收益率（小数形式，如 0.0546）
                    如果为 None，则默认使用固定 5.46%
    """
    if annual_returns is None:
        # 默认全部年份使用 5.46%
        annual_returns = [0.0546] * years
    elif len(annual_returns) != years:
        raise ValueError(f"annual_returns 长度必须等于 {years}")

    months = years * 12
    # 预计算每年的月收益率（每月复利）
    monthly_rates = []
    for yr in range(years):
        annual_r = annual_returns[yr]
        monthly_r = (1 + annual_r) ** (1/12) - 1
        monthly_rates.append(monthly_r)

    # 提早退出费率表 (剩余供款年期 -> 费率)
    exit_fee_table = {
        20: 1.00, 19: 0.96, 18: 0.92, 17: 0.88, 16: 0.84,
        15: 0.80, 14: 0.76, 13: 0.72, 12: 0.68, 11: 0.64,
        10: 0.60, 9: 0.56, 8: 0.52, 7: 0.48, 6: 0.44,
        5: 0.40, 4: 0.36, 3: 0.33, 2: 0.30, 1: 0.27, 0: 0.00
    }

    initial_balance = 0.0      # 首初账户
    accum_balance = 0.0        # 累积账户
    accum_principal = 0.0      # 累积账户累计供款本金

    yearly_records = []

    for t in range(1, months + 1):
        # 确定当前月份所属年份（1-20）
        year_idx = (t - 1) // 12   # 0-based
        monthly_rate = monthly_rates[year_idx]

        # 1. 当月供款划入对应账户
        if t <= 36:
            initial_balance += monthly_contribution
        else:
            accum_balance += monthly_contribution
            accum_principal += monthly_contribution

        # 2. 两个账户先获得当月收益（利润归各自账户）
        initial_balance *= (1 + monthly_rate)
        accum_balance *= (1 + monthly_rate)

        # 3. 扣除信托结算费（仅从首初账户）
        trust_fee = initial_balance * 0.0023
        initial_balance -= trust_fee

        # 4. 扣除行政费和组合服务费（仅从累积账户，第37个月起）
        if t >= 37:
            admin_fee = accum_principal * 0.0005          # 行政费基于累计本金
            accum_balance -= admin_fee
            combo_fee = accum_balance * 0.001             # 组合服务费基于扣除行政费后的价值
            accum_balance -= combo_fee

        # 防止浮点负数
        initial_balance = max(initial_balance, 0.0)
        accum_balance = max(accum_balance, 0.0)

        total_balance = initial_balance + accum_balance

        # 每年末记录
        if t % 12 == 0:
            year = t // 12
            total_contribution = year * 12 * monthly_contribution
            protection_value = total_contribution * 1.45

            if year < 20:
                if year == 1:
                    surrender_value = 0.0
                else:
                    remaining_years = 20 - year
                    fee_rate = exit_fee_table.get(remaining_years, 1.0)
                    exit_fee = initial_balance * fee_rate
                    surrender_value = max(total_balance - exit_fee, 0)
            else:
                surrender_value = total_balance

            yearly_records.append({
                '年份': year,
                '累计供款 (USD)': total_contribution,
                '账户价值 (费后) (USD)': round(total_balance, 2),
                '保护价值 (145%累计) (USD)': round(protection_value, 2),
                '解约价值 (USD)': round(surrender_value, 2)
            })

    return pd.DataFrame(yearly_records)

def main():
    plan_years = 20
    print("="*80)
    print("明烁Pro计划 - 收益测算（支持每年不同收益率）")
    print("规则：首初账户享有全部利润；信托费仅从首初账户扣；行政费从累积账户本金扣；组合服务费从累积账户价值扣。")
    print("="*80)

    # 示例：您可以在这里修改每年的年化收益率（百分数，例如第1年5.46%，第2年6.00%...）
    # 这里提供一个示例：前10年5.46%，后10年6.00%（仅作为演示，您可替换为真实数据）
    yearly_returns_percent = [
        3.00, 13.62, 3.53, -38.49, 23.45,
        12.78, 0.00, 13.40, 29.60, 11.39,
        -0.73, 9.54, 19.42, -6.24, 28.88,
        16.26, 26.89, -19.44, 24.23, 23.31
    ]

    # 转换为小数
    annual_returns = [x / 100.0 for x in yearly_returns_percent]

    monthly_payment = 1000   # 每月供款，可以修改

    print(f"\n模拟参数：每月供款 {monthly_payment} USD，计划期 {plan_years} 年")
    print("各年年化收益率：")
    for i, r in enumerate(yearly_returns_percent, 1):
        print(f"  第{i}年: {r}%")
    print("-"*80)

    df = simulate_starry_pro(monthly_contribution=monthly_payment,
                             annual_returns=annual_returns,
                             years=plan_years)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()