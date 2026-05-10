import sys
import pandas as pd

def simulate_starry_pro(monthly_contribution=1000, annual_return=0.05, years=20):
    months = years * 12
    monthly_rate = (1 + annual_return) ** (1/12) - 1

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
        # 1. 当月供款划入对应账户
        if t <= 36:
            initial_balance += monthly_contribution
        else:
            accum_balance += monthly_contribution
            accum_principal += monthly_contribution

        # 2. 两个账户分别获得当月收益（先增值）
        initial_balance *= (1 + monthly_rate)
        accum_balance *= (1 + monthly_rate)

        # 3. 扣除各项费用（后扣费）
        # 信托结算费：从首初账户扣除（每月0.23%）
        trust_fee = initial_balance * 0.0023
        initial_balance -= trust_fee

        # 行政费和组合服务费：从第37个月起，从累积账户扣除
        if t >= 37:
            # 行政费：基于累积账户累计供款本金（0.05%）
            admin_fee = accum_principal * 0.0005
            accum_balance -= admin_fee
            # 组合服务费：基于扣除行政费后的累积账户余额（0.1%）
            combo_fee = accum_balance * 0.001
            accum_balance -= combo_fee

        # 防御负数
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
    print("                   明烁Pro计划 - 收益测算 (先增值后扣费)")
    print("费用扣除顺序：当月供款 → 按月收益率增值 → 扣除信托费、行政费、组合费")
    print("="*80)

    if len(sys.argv) >= 3:
        monthly_payment = float(sys.argv[1])
        annual_return = float(sys.argv[2]) / 100.0

        print(f"\n模拟参数：每月供款 {monthly_payment:.0f} USD，年化收益率 {annual_return*100:.2f}%，计划期 {plan_years} 年")
        print("-"*80)

        df = simulate_starry_pro(monthly_contribution=monthly_payment,
                                 annual_return=annual_return,
                                 years=plan_years)
        print(df.to_string(index=False))
    else:
        print("\n用法: python main.py <每月供款金额> <年化收益率%>")
        print("示例: python main.py 1000 5.46")

if __name__ == "__main__":
    main()