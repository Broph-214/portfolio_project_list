<h1><ins> Performance and Fuel Efficiency of New Cars 2026</ins></h1>
<i>Data dated from 01/01/2026 to 16/03/2026. Information provided in the Vehicle's Certification Agency's New Car Fuel Consumption & Emission may be subject to change</i>

<h2>Data Source</h2>

Dataset Name: Vehicle Certification Agency Car and Fuel Emissions Data

Dataset Link: https://carfueldata.vehicle-certification-agency.gov.uk/downloads/default.aspx

<h2>Tools</h2>

Language: PostgreSQL

Software: DBeaver

<h2>Skills</h2>

<ul>
	<li>Common Table Expressions</li>
	<li>Percentiles</li>
	<li>Data Transformation</li>
	<li>Domain Reasoning</li>
	<li>Discrepancy Handling</li>
</ul>

<h2> Engine Performance (Imperial Horsepower)</h2>

Horsepower for the cars was derived from metric horsepower (ps) using the formula:

$HP$ = $Metric\ Horsepower(ps)$ $\cdot$ $0.98632$

```SQL
-- What are the top unique car models with the most horsepower?
WITH unique_models AS (
	SELECT DISTINCT ON(model) * 
	FROM euro
	ORDER BY model, power_hp DESC
)
SELECT 
manufacturer,
model, 
description, 
manual_or_automatic, 
fuel_type, 
power_hp
FROM unique_models
ORDER BY power_hp DESC
LIMIT 5;
```

![](assets\sql_cars\top_cars_hp.PNG)

The vehicles with the most powerful engines were electric, manufactured by either Tesla or Porche. This was expected as electric drivetrains deliver maximum torque immediately compared to vehicles with internal combustion engines. To filter out electric vehicles the following where clause was added to the above query:

```SQL
WHERE fuel_type IN ('Petrol','Diesel')
```

![](assets\sql_cars\top_zeroelec_hp.PNG)

Aston Martin and Mclaren manufactured cars with the most horsepower across diesel and petrol vehicles. While the data showed that the Valiant and Valour models both output 705 imperial horsepower from their engines, specifications from Aston Martin indicate that the Valiant's power is 745ps or ~735hp. Reported by the New Car Fuel Consumption & Emission Figures, model definitions were taken from EC Type Approval Documentation, which may be slightly different from commercial descriptions (Vehicle Certification Agency, 2025). This may also be the reason why engine performance values may differ from certification data. Alternatively, the data was dated for 2026, and was accessed for this analysis in March 2026. It is possible that future amendments to the data set could still occur, which could involve changes being made to the performance values. 

```SQL
-- How many unique models did the top 5 manufacturers make where the car's engine power was in the top 5% of all models for that year?
WITH top_95 AS (
	SELECT PERCENTILE_DISC(0.95) WITHIN GROUP(ORDER BY power_hp) top_models
	FROM euro
),
top_cars AS (
	SELECT * 
	FROM euro
	WHERE power_hp >= (SELECT top_models FROM top_95)
)
SELECT 
manufacturer,
COUNT(DISTINCT model) model_count
FROM top_cars
GROUP BY manufacturer
ORDER BY model_count DESC
LIMIT 5;
```

![](assets\sql_cars\engine_percentile_count.PNG)

Aston Martin had the most unique models in the top 20% of engine performance. Something to note is that different body styles of Aston Martin cars (DB12, DB12 Coupe, DB12 Volante) were classified as different models in the dataset. However, if some of the model's reported performance differ from commercially reported values (i.e. the Aston Martin Valiant), then these figures may not provide an actual count for models in the 95<sup>th</sup> percentile.

Overall, while the analysis may not have answered the question it had intended to, it provided valuable insight into the discrepancies between commercially reported figures and offically certified figures.

<h2>Fuel Efficiency</h2>

Fuel efficiency data is collected through the Worldwide Light Vehicle Test Procedure (WLTP) and is used to measure fuel consumption. To compare fuel efficiency between fuel types, the miles per kilowatt-hour metric (mi/kWh) for electric vehicles will need converted to a MPG equivalent (MPGe).

The following formula was used for conversion:

$MPGe$ = $mi/kWh$ $\cdot\ 33.7$ 

```SQL
-- What are the top 5 unique models for fuel efficiency?
WITH mpg_equivalent AS (
	SELECT *,
		CASE
			WHEN wltp_imperial_combined = 0 AND fuel_type = 'Electricity'
				THEN ("electric_energy_consumption_miles/kwh" * 33.7) 
				ELSE wltp_imperial_combined
	END AS mpge
	FROM euro
),
unique_model AS (
	SELECT
	DISTINCT ON (model)
	manufacturer,
	model,
	description, 
	manual_or_automatic, 
	fuel_type,
	mpge::int8
	FROM mpg_equivalent
	WHERE mpge IS NOT NULL
	AND
	mpge != 0
	ORDER BY model, mpge DESC
)
SELECT * FROM unique_model
ORDER BY mpge DESC
LIMIT 5;
```

![](assets\sql_cars\top_cars_fe.PNG)

Expectedly, electric cars were the most fuel efficient with the Mini Aceman coming out on top as the most efficient. Electric vehicles are more efficient when converting energy into motion as cars with internal combustion engines will lose energy from heat and friction.  

After filtering out electric vehicles, hybrids were the next most efficient group in terms of $MPGe$.

```SQL
-- Hybrids
SELECT * FROM unique_model
WHERE fuel_type NOT LIKE 'Electricity'
ORDER BY mpge DESC;
```

![](assets\sql_cars\top_hybrids_fe.PNG)

Then, any vehicles that could be charged electrically were filtered out:

```SQL
-- Fuel
SELECT * FROM unique_model
WHERE fuel_type IN ('Petrol','Diesel')
ORDER BY mpge DESC;
```

![](assets\sql_cars\top_fuel_fe.PNG)

```SQL
-- How many unique models did the top 5 manufacturers make where the car's fuel efficiency was in the top 5% of all models for that year?
WITH mpg_equivalent AS (
	SELECT *,
		CASE
			WHEN wltp_imperial_combined = 0 AND fuel_type = 'Electricity'
				THEN ("electric_energy_consumption_miles/kwh" * 33.7) 
				ELSE wltp_imperial_combined
	END AS mpge
	FROM euro
),
top_95 AS (
	SELECT PERCENTILE_DISC(0.95) WITHIN GROUP(ORDER BY mpge) top_models
	FROM mpg_equivalent
),
top_cars AS (
	SELECT * 
	FROM mpg_equivalent
	WHERE mpge >= (SELECT top_models FROM top_95)
)
SELECT 
manufacturer,
COUNT(DISTINCT model) model_count
FROM top_cars
GROUP BY manufacturer
ORDER BY model_count DESC
LIMIT 5;
```

![](assets\sql_cars\efficiency_percentile_count.PNG)

The top 5 companies each made 4 models that made it into the top 5% of fuel efficient cars. The following 9 places were filled with companies that had made 3 cars each. These companies included Fiat, Lexus, and Mercedes, amongst others.

<h2>References</h2>

Vehicle Certification Agency. 2025. https://www.vehicle-certification-agency.gov.uk/fuel-consumption-co2/fuel-consumption-guide/general-points/#topic-title 