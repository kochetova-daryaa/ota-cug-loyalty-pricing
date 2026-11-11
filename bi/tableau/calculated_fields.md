# Tableau Calculated Fields & LOD Expressions (`Keystone`)

1. **Conversion Rate**
   ```
   SUM([converted]) / COUNT([session_id])
   ```
2. **Cannibalization Share (among bookings)**
   ```
   SUM(IF [converted] = 1 THEN [cannibalized] ELSE 0 END) / SUM([converted])
   ```
3. **Effective Points Cost Rate (LOD by Fence)**
   ```
   { FIXED [fence_id] : SUM([promo_cost]) / SUM([gbv]) }
   ```
4. **Net Contribution per Session**
   ```
   SUM([contribution]) / COUNT([session_id])
   ```
5. **Fence Share of Total Net Contribution**
   ```
   SUM([contribution]) / SUM({ FIXED : SUM([contribution]) })
   ```
