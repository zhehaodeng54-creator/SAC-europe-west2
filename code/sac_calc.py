import datetime
from fractions import Fraction

PDT = datetime.timezone(datetime.timedelta(hours=-7))
def pdt(y, m, d, H, M):
    return datetime.datetime(y, m, d, H, M, tzinfo=PDT)

# Verified from https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2
# Fractions below are the reported available shares during each service window.
cohorts = [
    ("CS",   Fraction(86, 100),        pdt(2022, 7, 19, 7, 18), pdt(2022, 7, 19, 8, 54)),   # ~86% ReadObject availability
    ("BT",   Fraction(30, 100),        pdt(2022, 7, 19, 7, 5),  pdt(2022, 7, 20, 2, 20)),   # ~70% had 100% unavailability -> 30% available
    ("CT",   Fraction(94, 100),        pdt(2022, 7, 19, 10, 5), pdt(2022, 7, 19, 13, 24)),  # 6% stopped delivering
    ("CSch", Fraction(94, 100),        pdt(2022, 7, 19, 10, 5), pdt(2022, 7, 19, 13, 24)),  # 6% stopped executing
    ("GKE",  Fraction(43, 100),        pdt(2022, 7, 19, 9, 30), pdt(2022, 7, 19, 21, 30)),  # 57% nodes unavailable -> 43% available
    ("VPC",  1 - Fraction(1275, 3509), pdt(2022, 7, 19, 10, 6), pdt(2022, 7, 19, 20, 32)),  # 1275/3509 unreachable
]
W = Fraction(1, 6)          # equal weights
THR = Fraction(8, 10)       # illustrative aggregate threshold
t0 = min(c[2] for c in cohorts)
t1 = max(c[3] for c in cohorts)
N = int((t1 - t0).total_seconds() // 60)

# Minute-level calculation on left-closed, right-open intervals.
sac = []
for t in range(N):
    tm = t0 + datetime.timedelta(minutes=t)
    fs = [av if s <= tm < e else Fraction(1) for (_, av, s, e) in cohorts]
    sac.append(sum(fs) * W)

min_sac = min(sac)
below = sum(1 for v in sac if v < THR)
sust = 0
for t in range(N - 1, -1, -1):
    if sac[t] < THR:
        sust = t + 1
        break
wsdh = sum(Fraction(1) - v for v in sac) / Fraction(60)

print("test_window_minutes =", N)
print("minimum_SAC =", float(min_sac))
print("time_below_0.80_minutes =", below, "=", below / 60, "h")
print("sustained_recovery_minutes =", sust, "=", sust / 60, "h")
print("WSDH_hours =", float(wsdh))

# Independent check using event boundaries.
events = []
for cid, av, s, e in cohorts:
    events.append((int((s - t0).total_seconds() // 60), +1, cid))
    events.append((int((e - t0).total_seconds() // 60), -1, cid))
events.sort(key=lambda x: (x[0], -x[1]))

pts = sorted(set([0] + [x[0] for x in events] + [N]))
by_id = {c[0]: c[1] for c in cohorts}
active = set()
seg = []
for i in range(len(pts) - 1):
    a, b = pts[i], pts[i + 1]
    for tm, d, cid in events:
        if tm == a:
            active.add(cid) if d == +1 else active.discard(cid)
    fs = [by_id[cid] if cid in active else Fraction(1) for cid in by_id]
    sac_i = sum(fs) * W
    seg.append((a, b, sac_i))
    for tm, d, cid in events:
        if a < tm < b:
            active.add(cid) if d == +1 else active.discard(cid)

print("\nsegments (start,end,SAC):")
for a, b, s in seg:
    print("  [%4d,%4d)  %.6f" % (a, b, float(s)))
print("piecewise min SAC =", float(min(s for _, _, s in seg)))
print("piecewise below-threshold minutes =", sum(b - a for a, b, s in seg if s < THR))
print("piecewise WSDH =", float(sum((Fraction(1) - s) * Fraction(b - a, 60) for a, b, s in seg)))

# A second WSDH check using individual cohort deficits.
per_service = []
for cid, av, s, e in cohorts:
    dur = Fraction(int((e - s).total_seconds() // 60), 60)
    per_service.append((cid, (Fraction(1) - av) * dur))
wsdh_alt = sum(g for _, g in per_service) / Fraction(6)
print("\nper-service deficit-hours (x1/6 sum) =", float(wsdh_alt), "== WSDH?", wsdh_alt == wsdh)
for cid, g in per_service:
    print("  %s: %.4f service-deficit-hours" % (cid, float(g)))
