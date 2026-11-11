from keystone.economics import booking_unit_economics, effective_promo_rate


def test_points_are_cheaper_than_equal_cash_discount():
    cash_6 = effective_promo_rate("cash", 0.06)
    pts_9 = effective_promo_rate("points", 0.09, breakage=0.36, repeat_ad_saving=0.25)
    assert abs(cash_6 - 0.06) < 1e-9
    assert abs(pts_9 - 0.0432) < 1e-9
    assert pts_9 < cash_6


def test_booking_unit_economics_prefers_points_over_cash():
    cash_book = booking_unit_economics(hotel_net=200.0, mechanic="cash", nominal_rate=0.06, cancelled=False)
    points_book = booking_unit_economics(hotel_net=200.0, mechanic="points", nominal_rate=0.09, cancelled=False)
    assert points_book.net_contribution_before_ads > cash_book.net_contribution_before_ads
