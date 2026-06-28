import yaml

with open("recommendation_rules.yml", "r") as f:
    RULES = yaml.safe_load(f)


def recommend_stock(stock_data: dict) -> dict:

    score = 0
    reasons = []

    valuation = stock_data["valuation"]
    profitability = stock_data["profitability"]
    growth = stock_data["growth"]
    analyst = stock_data["analyst"]
    price = stock_data["price"]

    # PE RATIO

    pe = valuation.get("pe_ratio")

    if pe is not None:
        cfg = RULES["pe"]

        if pe < cfg["excellent"]:
            print("PE: excellent condition met")
            score += cfg["excellent_score"]
            reasons.append(
                f"PE Ratio ({pe:.2f}) is below {cfg['excellent']} (+{cfg['excellent_score']})"
            )

        elif pe < cfg["acceptable"]:
            print("PE: acceptable condition met")
            score += cfg["acceptable_score"]
            reasons.append(
                f"PE Ratio ({pe:.2f}) is below {cfg['acceptable']} (+{cfg['acceptable_score']})"
            )

        else:
            print("PE: poor condition met")
            score += cfg["poor_score"]
            reasons.append(
                f"PE Ratio ({pe:.2f}) is above {cfg['acceptable']} ({cfg['poor_score']})"
            )

    # RETURN ON EQUITY

    roe = profitability.get("return_on_equity")

    if roe is not None:
        cfg = RULES["roe"]

        if roe > cfg["excellent"]:
            print("ROE: excellent condition met")
            score += cfg["excellent_score"]
            reasons.append(
                f"ROE ({roe:.2%}) is above {cfg['excellent']:.0%} (+{cfg['excellent_score']})"
            )

        elif roe > cfg["acceptable"]:
            print("ROE: acceptable condition met")
            score += cfg["acceptable_score"]
            reasons.append(
                f"ROE ({roe:.2%}) is above {cfg['acceptable']:.0%} (+{cfg['acceptable_score']})"
            )

        else:
            print("ROE: poor condition met")
            score += cfg["poor_score"]
            reasons.append(
                f"ROE ({roe:.2%}) is below {cfg['acceptable']:.0%} ({cfg['poor_score']})"
            )

    # PROFIT MARGIN

    margin = profitability.get("profit_margin")

    if margin is not None:
        cfg = RULES["profit_margin"]

        if margin > cfg["excellent"]:
            print("Profit Margin: excellent condition met")
            score += cfg["excellent_score"]
            reasons.append(
                f"Profit Margin ({margin:.2%}) is above {cfg['excellent']:.0%} (+{cfg['excellent_score']})"
            )

        else:
            print("Profit Margin: poor condition met")
            score += cfg["poor_score"]
            reasons.append(
                f"Profit Margin ({margin:.2%}) is below {cfg['excellent']:.0%} ({cfg['poor_score']})"
            )

    # REVENUE GROWTH

    revenue = growth.get("revenue_growth")

    if revenue is not None:
        cfg = RULES["revenue_growth"]

        if revenue > cfg["excellent"]:
            print("Revenue Growth: excellent condition met")
            score += cfg["excellent_score"]
            reasons.append(
                f"Revenue Growth ({revenue:.2%}) is above {cfg['excellent']:.0%} (+{cfg['excellent_score']})"
            )

        elif revenue > cfg["acceptable"]:
            print("Revenue Growth: acceptable condition met")
            score += cfg["acceptable_score"]
            reasons.append(
                f"Revenue Growth ({revenue:.2%}) is positive (+{cfg['acceptable_score']})"
            )

        else:
            print("Revenue Growth: poor condition met")
            score += cfg["poor_score"]
            reasons.append(
                f"Revenue Growth ({revenue:.2%}) is negative ({cfg['poor_score']})"
            )

    # EARNINGS GROWTH

    earnings = growth.get("earnings_growth")

    if earnings is not None:
        cfg = RULES["earnings_growth"]

        if earnings > cfg["excellent"]:
            print("Earnings Growth: excellent condition met")
            score += cfg["excellent_score"]
            reasons.append(
                f"Earnings Growth ({earnings:.2%}) is above {cfg['excellent']:.0%} (+{cfg['excellent_score']})"
            )

        elif earnings > cfg["acceptable"]:
            print("Earnings Growth: acceptable condition met")
            score += cfg["acceptable_score"]
            reasons.append(
                f"Earnings Growth ({earnings:.2%}) is positive (+{cfg['acceptable_score']})"
            )

        else:
            print("Earnings Growth: poor condition met")
            score += cfg["poor_score"]
            reasons.append(
                f" Earnings Growth ({earnings:.2%}) is negative ({cfg['poor_score']})"
            )

    # BETA

    beta = valuation.get("beta")

    if beta is not None:
        cfg = RULES["beta"]

        if beta < cfg["safe"]:
            print("Beta: safe condition met")
            score += cfg["safe_score"]
            reasons.append(
                f"✓ Beta ({beta:.2f}) is below {cfg['safe']} (+{cfg['safe_score']})"
            )

        elif beta > cfg["risky"]:
            print("Beta: risky condition met")
            score += cfg["risky_score"]
            reasons.append(
                f"✗ Beta ({beta:.2f}) is above {cfg['risky']} ({cfg['risky_score']})"
            )

    # PRICE TREND

    current = price.get("current_price")
    sma50 = price.get("fifty_day_average")
    sma200 = price.get("two_hundred_day_average")

    cfg = RULES["trend"]

    if current is not None and sma50 is not None:

        if current > sma50:
            print("Price Trend: above 50-DMA condition met")
            score += cfg["above_50_score"]
            reasons.append(
                f" Current Price (₹{current:.2f}) is above 50-DMA (₹{sma50:.2f}) (+{cfg['above_50_score']})"
            )

        else:
            print("Price Trend: below 50-DMA condition met")
            score += cfg["below_score"]
            reasons.append(
                f" Current Price (₹{current:.2f}) is below 50-DMA (₹{sma50:.2f}) ({cfg['below_score']})"
            )

    if current is not None and sma200 is not None:

        if current > sma200:
            print("Price Trend: above 200-DMA condition met")
            score += cfg["above_200_score"]
            reasons.append(
                f"Current Price (₹{current:.2f}) is above 200-DMA (₹{sma200:.2f}) (+{cfg['above_200_score']})"
            )

        else:
            print("Price Trend: below 200-DMA condition met")
            score += cfg["below_score"]
            reasons.append(
                f" Current Price (₹{current:.2f}) is below 200-DMA (₹{sma200:.2f}) ({cfg['below_score']})"
            )

    # ANALYST RECOMMENDATION

    recommendation = analyst.get("recommendation")

    if recommendation:
        print(f"Analyst: {recommendation.lower()} condition met")

        analyst_score = RULES["analyst"].get(
            recommendation.lower(),
            0
        )

        score += analyst_score

        reasons.append(
            f"Analyst Recommendation: {recommendation.upper()} "
            f"(Mean Rating: {analyst.get('recommendation_mean')}, "
            f"Target Price: ₹{analyst.get('target_mean_price')}) "
            f"(+{analyst_score})"
        )

    # FINAL VERDICT

    cfg = RULES["recommendation"]

    if score >= cfg["strong_buy"]:
        print("Verdict: Strong Buy condition met")
        verdict = "Strong Buy"

    elif score >= cfg["buy"]:
        print("Verdict: Buy condition met")
        verdict = "Buy"

    elif score >= cfg["hold"]:
        print("Verdict: Hold condition met")
        verdict = "Hold"

    else:
        print("Verdict: Avoid condition met")
        verdict = "Avoid"

    return {
        "score": score,
        "recommendation": verdict,
        "reasons": reasons
    }