-- stored procedures / functions for icenine database
DELIMITER $$

DROP FUNCTION IF EXISTS `icenine`.`episodeName`$$
CREATE FUNCTION `icenine`.`episodeName` (filename VARCHAR(255)) RETURNS VARCHAR(255)
DETERMINISTIC
NO SQL
BEGIN
DECLARE trailingStr VARCHAR(255);
DECLARE epName VARCHAR(255);
SET trailingStr = substring_index(filename, '-', -1);
SET epName = trim(substring(trailingStr, 1, length(trailingStr)-4));
-- handle names that have \d\d\d\d and no hyphen separators
IF epName REGEXP '^[[:digit:]]{3,4} ' THEN
  RETURN trim(replace(epName, substring_index(epName, ' ', 1), ''));
ELSE
  RETURN epName;
END IF;
END$$

DROP PROCEDURE IF EXISTS `icenine`.`mergeTwoFiles`$$
CREATE PROCEDURE `icenine`.`mergeTwoFiles` (oldId INT, newId INT)
BEGIN
DECLARE date1 DATE;
DECLARE date2 DATE;
select additiondate INTO date1 from files where fileId = oldId; 
select additiondate INTO date2 from files where fileId = newId;

UPDATE logs SET FileID = newId where FileID = oldId;
IF date1 < date2 THEN
  UPDATE files SET additiondate = date1 where fileId = newId;
END IF;
DELETE FROM files where FileID = oldId;
END$$

DELIMITER ;

