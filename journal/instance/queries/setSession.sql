UPDATE candle
SET session = CASE
  WHEN time(date) < '13:30:00' THEN 'PRE'
  WHEN time(date) > '20:00:00' THEN 'POST'
  ELSE 'REG'
END;