CREATE TABLE assigned_models
	SELECT *
	FROM model a
	WHERE EXISTS (SELECT 1
				  FROM classification b
				  WHERE a.id = b.model_id);