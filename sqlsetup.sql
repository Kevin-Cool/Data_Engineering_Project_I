-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema scrape
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema scrape
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `scrape` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `scrape` ;

-- -----------------------------------------------------
-- Table `scrape`.`municipality`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`municipality` (
  `zipcode` INT NOT NULL,
  `name` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`zipcode`),
  UNIQUE INDEX `zipcode_UNIQUE` (`zipcode` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`adress`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`adress` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `street` VARCHAR(45) NOT NULL,
  `zipcode` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `zipcode_idx` (`zipcode` ASC) VISIBLE,
  CONSTRAINT `zipcode`
    FOREIGN KEY (`zipcode`)
    REFERENCES `scrape`.`municipality` (`zipcode`))
ENGINE = InnoDB
AUTO_INCREMENT = 204
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`durabilitycategories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`durabilitycategories` (
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE INDEX `nam_UNIQUE` (`name` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`durabilityterms`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`durabilityterms` (
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(128) NULL DEFAULT NULL,
  `durabilitycategoriesID` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE,
  INDEX `categorie_idx` (`durabilitycategoriesID` ASC) VISIBLE,
  CONSTRAINT `categorie`
    FOREIGN KEY (`durabilitycategoriesID`)
    REFERENCES `scrape`.`durabilitycategories` (`name`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`durabilitykeywords`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`durabilitykeywords` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `durabilityterms` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `term_idx` (`durabilityterms` ASC) VISIBLE,
  CONSTRAINT `term`
    FOREIGN KEY (`durabilityterms`)
    REFERENCES `scrape`.`durabilityterms` (`name`))
ENGINE = InnoDB
AUTO_INCREMENT = 185
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`finance`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`finance` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `turnover` DOUBLE NOT NULL,
  `totalAssets` DOUBLE NOT NULL,
  `netValueAdded` DOUBLE NOT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 194
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`kmo`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`kmo` (
  `ID` VARCHAR(16) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NULL DEFAULT NULL,
  `workforce` INT NULL DEFAULT NULL,
  `telephone` VARCHAR(45) NULL DEFAULT NULL,
  `website` VARCHAR(45) NULL DEFAULT 'None',
  `adressID` INT NULL DEFAULT NULL,
  `financeID` INT NULL DEFAULT NULL,
  `b2b` TINYINT NOT NULL DEFAULT '0',
  `humancapitalScore` INT NULL DEFAULT NULL,
  `naturalcapitalScore` INT NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE INDEX `ID_UNIQUE` (`ID` ASC) VISIBLE,
  INDEX `AdressID_idx` (`adressID` ASC) VISIBLE,
  INDEX `income_idx` (`financeID` ASC) VISIBLE,
  CONSTRAINT `adress`
    FOREIGN KEY (`adressID`)
    REFERENCES `scrape`.`adress` (`ID`),
  CONSTRAINT `income`
    FOREIGN KEY (`financeID`)
    REFERENCES `scrape`.`finance` (`ID`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`kmo_employees`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`kmo_employees` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `kmo_ID` VARCHAR(16) NOT NULL,
  `columnText` VARCHAR(45) NOT NULL,
  `fulltime` DOUBLE NULL DEFAULT NULL,
  `parttime` DOUBLE NULL DEFAULT NULL,
  `total` DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `kmo_idx` (`kmo_ID` ASC) VISIBLE,
  CONSTRAINT `kmo_emp`
    FOREIGN KEY (`kmo_ID`)
    REFERENCES `scrape`.`kmo` (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 365
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`kmodurabilityitems`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`kmodurabilityitems` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `kmoID` VARCHAR(16) NULL DEFAULT NULL,
  `durabilitykeywordID` INT NULL DEFAULT NULL,
  `context` VARCHAR(512) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  INDEX `kmo_idx` (`kmoID` ASC) VISIBLE,
  INDEX `keyword_idx` (`durabilitykeywordID` ASC) VISIBLE,
  CONSTRAINT `keyword`
    FOREIGN KEY (`durabilitykeywordID`)
    REFERENCES `scrape`.`durabilitykeywords` (`ID`),
  CONSTRAINT `kmo`
    FOREIGN KEY (`kmoID`)
    REFERENCES `scrape`.`kmo` (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 294
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`population_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`population_scores` (
  `ABCD_score` CHAR(1) NOT NULL,
  `HumancapitalScore` DOUBLE NOT NULL,
  `NaturalcapitalScore` DOUBLE NOT NULL,
  `TotalScore` DOUBLE NOT NULL,
  PRIMARY KEY (`ABCD_score`),
  UNIQUE INDEX `ABCD_score_UNIQUE` (`ABCD_score` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`sector`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`sector` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `humancapitalScore` DOUBLE NULL DEFAULT NULL,
  `naturalcapitalScore` DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 145
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`sector_population_scores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`sector_population_scores` (
  `ABCD_score` CHAR(1) NOT NULL,
  `HumancapitalScore` DOUBLE NOT NULL,
  `NaturalcapitalScore` DOUBLE NOT NULL,
  `TotalScore` DOUBLE NOT NULL,
  PRIMARY KEY (`ABCD_score`),
  UNIQUE INDEX `ABCD_score_UNIQUE` (`ABCD_score` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `scrape`.`sectorlist`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scrape`.`sectorlist` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `kmoID` VARCHAR(16) NOT NULL,
  `sectorID` INT NOT NULL,
  PRIMARY KEY (`ID`),
  INDEX `sec_idx` (`sectorID` ASC) VISIBLE,
  INDEX `kmoID_idx` (`kmoID` ASC) VISIBLE,
  CONSTRAINT `kmoID`
    FOREIGN KEY (`kmoID`)
    REFERENCES `scrape`.`kmo` (`ID`),
  CONSTRAINT `sectorID`
    FOREIGN KEY (`sectorID`)
    REFERENCES `scrape`.`sector` (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 84
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

USE `scrape` ;

-- -----------------------------------------------------
-- procedure insertAdress
-- -----------------------------------------------------

DELIMITER $$
USE `scrape`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertAdress`(
	IN kmo_name varchar(64), IN nr_person varchar(64), IN telephone varchar(64), IN email varchar(64), IN kmo_ID varchar(64), IN kmo_webadress varchar(64),IN b2bIN varchar(64),
    IN streetIN varchar(64), IN zipcodeIN varchar(64),
    IN omzet varchar(64), IN total_value varchar(64), IN netto_toe varchar(64)
)
BEGIN
    DECLARE `_rollback` BOOL DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET `_rollback` = 1;
    START TRANSACTION;
    
	INSERT INTO scrape.adress (street,zipcode) VALUES (streetIN,zipcodeIN);
    SELECT LAST_INSERT_ID() into @adress_ID ;
	INSERT INTO scrape.finance (turnover,totalAssets,netValueAdded) VALUES (omzet,total_value,netto_toe);
    SELECT LAST_INSERT_ID() into @finance_ID ;
	INSERT INTO scrape.kmo (ID,name,email,workforce,telephone,website,adressID,financeID,b2b) VALUES (kmo_ID,kmo_name,email,nr_person,telephone,kmo_webadress,@adress_ID,@finance_ID,b2bIN);
    
    IF `_rollback` THEN
        ROLLBACK;
    ELSE
        COMMIT;
    END IF;
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure insertSectorRef_and_sector
-- -----------------------------------------------------

DELIMITER $$
USE `scrape`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `insertSectorRef_and_sector`(
	IN kmo_ID varchar(64), IN sector_name varchar(64)
)
BEGIN
    DECLARE `_rollback` BOOL DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET `_rollback` = 1;
    START TRANSACTION;
    
	INSERT INTO scrape.sector (name) VALUES (sector_name);
    SELECT LAST_INSERT_ID() into @sector_ID ;
	INSERT INTO scrape.sectorlist (kmoID,sectorID) VALUES (kmo_ID,@sector_ID);
 
    IF `_rollback` THEN
        ROLLBACK;
    ELSE
        COMMIT;
    END IF;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
