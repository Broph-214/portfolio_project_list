```
-- What are the top 5 cars in terms of horse power?
SELECT 
manufacturer,
model, 
description, 
manual_or_automatic, 
fuel_type, 
power_hp
FROM euro
ORDER BY power_hp DESC
LIMIT 5;
```
