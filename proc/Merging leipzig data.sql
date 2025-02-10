
SELECT Word, Sum(Freq) as Freq FROM (
SELECT Word, Freq FROM "Single word frequency" 

WHERE Freq > 0 AND freq Is NOT NULL AND freq GLOB '[0-9]*' AND Word NOT LIKE "%,%"

union all 

SELECT Word, Freq FROM "Neighbor Word frequency" 

WHERE Freq > 0 AND freq Is NOT NULL AND freq GLOB '[0-9]*'  and Word NOT LIKE "%,%") A

GROUP BY Word
