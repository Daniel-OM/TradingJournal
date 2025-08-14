
DELETE FROM candle
WHERE DATE(created_at) = DATE('now', 'localtime');