-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: maplecourt
-- ------------------------------------------------------
-- Server version	8.0.33-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Cashflow`
--

DROP TABLE IF EXISTS `Cashflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cashflow` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Date` datetime DEFAULT NULL,
  `Type` varchar(20) DEFAULT NULL,
  `Amount` decimal(10,2) DEFAULT NULL,
  `Reference` varchar(500) DEFAULT NULL,
  `CurrentBal` decimal(10,2) DEFAULT NULL,
  `AvailableBal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `unique_record` (`Date`,`Reference`,`Amount`,`CurrentBal`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb3 */ ;
/*!50003 SET character_set_results = utf8mb3 */ ;
/*!50003 SET collation_connection  = utf8mb3_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'IGNORE_SPACE,ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`admin`@`%`*/ /*!50003 TRIGGER `insert_Landlords_payments` AFTER INSERT ON `Cashflow` FOR EACH ROW BEGIN
    INSERT INTO
        Landlords_payments(
            PaymentDate,
            Descriptions,
            PaymentAmount,
            Landlord,
            PropertyID
        )
    SELECT
        date(Date),
        Reference,
        Amount,
        CASE
            WHEN Reference LIKE '% ENKOLAR %' THEN (SELECT FullName from Landlords where LandlordID = 1)
            WHEN Reference LIKE '% ATSEN %'
                OR Reference LIKE '% AHUA %' THEN (SELECT FullName from Landlords where LandlordID = 2)
            WHEN Reference LIKE '% PAUL BENGBA %'
                OR Reference LIKE '% BEMGBA %'
                OR Reference LIKE '% SHAVER MULTI%' THEN (SELECT FullName from Landlords where LandlordID = 3)
            ELSE NULL
        END,
        CASE
            WHEN Reference LIKE '% ENKOLAR %'
            AND Reference LIKE '%MC2%' THEN 2
            WHEN Reference LIKE '% ENKOLAR %'
            AND Reference LIKE '%MC1%' THEN 1
            WHEN Reference LIKE '% ATSEN %'
            OR Reference LIKE '% AHUA %' THEN 3
            WHEN Reference LIKE '% PAUL BENGBA %'
            OR Reference LIKE '% BEMGBA %'
            OR Reference LIKE '% SHAVER MULTI%' THEN 4
            ELSE NULL
        END
    FROM Cashflow
    where Type = 'Credit'
    AND lower(Reference) LIKE '%management fee%'
        OR lower(Reference) LIKE '%mgt fee%'
        OR lower(Reference) LIKE '%atsen jonathan ahua%'
        OR lower(Reference) LIKE '%atsen % ahua%'
        OR lower(Reference) LIKE '%enkolar %'
        OR lower(Reference) LIKE '%enkolar business %'
        OR lower(Reference) LIKE '%sc reimbursement %'
        OR lower(Reference) LIKE '%mc% service%charge%'
        OR lower(Reference) LIKE '%mc% sc%'
        OR lower(Reference) LIKE '%mc% sc%reimbursement%'
        OR lower(Reference) LIKE '%mc% sc%reimburse%'
        OR lower(Reference) LIKE '%mc% mgt%fee%'
        OR lower(Reference) LIKE '%mc% management%fee%'
        OR lower(Reference) LIKE '%mc% incident%'
    ;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `Landlords`
--

DROP TABLE IF EXISTS `Landlords`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Landlords` (
  `LandlordID` int NOT NULL,
  `FullName` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `Email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `PhoneNumber` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`LandlordID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Landlords_payments`
--

DROP TABLE IF EXISTS `Landlords_payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Landlords_payments` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `PaymentDate` date NOT NULL,
  `Descriptions` varchar(500) DEFAULT NULL,
  `PaymentAmount` decimal(10,2) NOT NULL,
  `Landlord` varchar(45) NOT NULL,
  `PropertyID` int DEFAULT NULL,
  `ValidDate` date DEFAULT NULL,
  `ServiceCharge` decimal(10,2) DEFAULT '0.00',
  `ManagementFee` decimal(10,2) DEFAULT '0.00',
  `Incidentals` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`PaymentID`),
  KEY `fk_cashflow_Property_PropertyID_idx` (`PropertyID`),
  CONSTRAINT `fk_cashflow_Property_PropertyID` FOREIGN KEY (`PropertyID`) REFERENCES `Property` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Maintenance`
--

DROP TABLE IF EXISTS `Maintenance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Maintenance` (
  `MaintenanceID` int NOT NULL,
  `UnitID` int DEFAULT NULL,
  `Date` date NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Cost` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`MaintenanceID`),
  KEY `unitID_fk` (`UnitID`),
  CONSTRAINT `unitID_fk` FOREIGN KEY (`UnitID`) REFERENCES `Units` (`UnitID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `ManagementFee`
--

DROP TABLE IF EXISTS `ManagementFee`;
/*!50001 DROP VIEW IF EXISTS `ManagementFee`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `ManagementFee` AS SELECT 
 1 AS `PropertyID`,
 1 AS `Unit`,
 1 AS `Tenant`,
 1 AS `Period`,
 1 AS `Rent_Paid`,
 1 AS `Mgt_Fee_7.5%`,
 1 AS `Mgt_Fee/Day`,
 1 AS `Bill_Period(Days)`,
 1 AS `Bill_Month`,
 1 AS `Mgt_Fee(NGN)`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `Property`
--

DROP TABLE IF EXISTS `Property`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Property` (
  `ID` int NOT NULL,
  `PropertyName` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Address` varchar(250) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `LandlordID` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `LandlordID` (`LandlordID`),
  CONSTRAINT `Property_ibfk_1` FOREIGN KEY (`LandlordID`) REFERENCES `Landlords` (`LandlordID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Rentals`
--

DROP TABLE IF EXISTS `Rentals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Rentals` (
  `RentalID` int NOT NULL AUTO_INCREMENT,
  `UnitID` int DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `RentPrice` int DEFAULT NULL,
  `ServiceCharge` int DEFAULT NULL,
  `CautionDeposit` int DEFAULT NULL,
  `ContractStatus` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `TenantID` int DEFAULT NULL,
  `StopDate` date DEFAULT NULL,
  PRIMARY KEY (`RentalID`),
  UNIQUE KEY `RentalID` (`RentalID`),
  KEY `UnitID` (`UnitID`),
  KEY `TenantID` (`TenantID`),
  KEY `idx_stopdate` (`StopDate`),
  CONSTRAINT `Rentals_ibfk_1` FOREIGN KEY (`UnitID`) REFERENCES `Units` (`UnitID`),
  CONSTRAINT `Rentals_ibfk_2` FOREIGN KEY (`TenantID`) REFERENCES `Tenants` (`TenantID`),
  CONSTRAINT `Rentals_chk_1` CHECK ((`ContractStatus` in (_utf8mb4'Pending',_utf8mb4'Signed')))
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Supplies`
--

DROP TABLE IF EXISTS `Supplies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Supplies` (
  `SupplyID` int NOT NULL,
  `UnitID` int DEFAULT NULL,
  `SupplyDate` date DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Cost` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`SupplyID`),
  KEY `supply_unitID_fk` (`UnitID`),
  CONSTRAINT `supply_unitID_fk` FOREIGN KEY (`UnitID`) REFERENCES `Units` (`UnitID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Tenants`
--

DROP TABLE IF EXISTS `Tenants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Tenants` (
  `TenantID` int NOT NULL,
  `FirstName` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `LastName` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `Email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `PhoneNumber` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `UnitID` int DEFAULT NULL,
  PRIMARY KEY (`TenantID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `UnitID` (`UnitID`),
  CONSTRAINT `Tenants_ibfk_1` FOREIGN KEY (`UnitID`) REFERENCES `Units` (`UnitID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Units`
--

DROP TABLE IF EXISTS `Units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Units` (
  `UnitID` int NOT NULL,
  `UnitCode` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Bedrooms` int NOT NULL,
  `Bathrooms` int NOT NULL,
  `PropertyID` int DEFAULT NULL,
  PRIMARY KEY (`UnitID`),
  KEY `PropertyID` (`PropertyID`),
  CONSTRAINT `Units_ibfk_1` FOREIGN KEY (`PropertyID`) REFERENCES `Property` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `rent_tracker`
--

DROP TABLE IF EXISTS `rent_tracker`;
/*!50001 DROP VIEW IF EXISTS `rent_tracker`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `rent_tracker` AS SELECT 
 1 AS `FullName`,
 1 AS `PropertyName`,
 1 AS `UnitCode`,
 1 AS `Email`,
 1 AS `RentPrice`,
 1 AS `StopDate`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'maplecourt'
--

--
-- Dumping routines for database 'maplecourt'
--
/*!50003 DROP FUNCTION IF EXISTS `max_ValidDate` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb3 */ ;
/*!50003 SET character_set_results = utf8mb3 */ ;
/*!50003 SET collation_connection  = utf8mb3_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'IGNORE_SPACE,ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`admin`@`%` FUNCTION `max_ValidDate`(v_PropertyID int) RETURNS date
    DETERMINISTIC
BEGIN declare v_max_ValidDate date;

SELECT
    max(ValidDate) INTO @v_max_ValidDate
FROM
    Landlords_payments
WHERE
    PropertyID = v_PropertyID
    AND ValidDate IS NOT NULL
GROUP BY
    PropertyID;

RETURN @v_max_ValidDate;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `rent_tracking` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `rent_tracking`()
BEGIN
DECLARE done bool DEFAULT False;
declare Landlord_ varchar(200);
declare Property_ varchar(200);
declare Unit_ varchar (10);
declare Contact_ varchar(200);
declare Rent_ int;
declare Due_ date;
declare tracking_cur cursor for select Landlords.FullName, Property.PropertyName, Units.UnitCode, Tenants.Email, Rentals.RentPrice, Rentals.StopDate from Landlords, Property, Units, Tenants, Rentals where Landlords.LandlordID = Property.LandlordID and Property.ID = Units.PropertyID and Units.UnitID = Tenants.UnitID and Units.UnitID = Rentals.UnitID;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = True;
OPEN tracking_cur;
loop1:loop fetch tracking_cur into Landlord_, Property_, Unit_, Contact_, Rent_, Due_;
if done then leave loop1;
end if;
select Landlord_, Property_, Unit_, Contact_, Rent_, Due_;
end loop;
CLOSE tracking_cur;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `ManagementFee`
--

/*!50001 DROP VIEW IF EXISTS `ManagementFee`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`admin`@`%` SQL SECURITY DEFINER */
/*!50001 VIEW `ManagementFee` AS with `last_payment_date` as (select `Landlords_payments`.`PropertyID` AS `PropertyID`,max(`Landlords_payments`.`ValidDate`) AS `max_date` from `Landlords_payments` where (`Landlords_payments`.`ValidDate` is not null) group by `Landlords_payments`.`PropertyID`) select `U`.`PropertyID` AS `PropertyID`,`U`.`UnitCode` AS `Unit`,concat(`T`.`FirstName`,', ',`T`.`LastName`) AS `Tenant`,(to_days(`R`.`StopDate`) - to_days(`R`.`StartDate`)) AS `Period`,format(`R`.`RentPrice`,2) AS `Rent_Paid`,format(((`R`.`RentPrice` * 7.5) / 100),2) AS `Mgt_Fee_7.5%`,format((((`R`.`RentPrice` * 7.5) / 100) / (to_days(`R`.`StopDate`) - to_days(`R`.`StartDate`))),2) AS `Mgt_Fee/Day`,(case when (`R`.`StopDate` > cast(last_day(curdate()) as date)) then (to_days(last_day(curdate())) - to_days(`L`.`max_date`)) when (`R`.`StopDate` < cast(last_day(curdate()) as date)) then (to_days(`R`.`StopDate`) - to_days(`L`.`max_date`)) end) AS `Bill_Period(Days)`,monthname(curdate()) AS `Bill_Month`,format(((((`R`.`RentPrice` * 7.5) / 100) / (to_days(`R`.`StopDate`) - to_days(`R`.`StartDate`))) * (case when (`R`.`StopDate` > cast(last_day(curdate()) as date)) then (to_days(last_day(curdate())) - to_days(`L`.`max_date`)) when (`R`.`StopDate` < cast(last_day(curdate()) as date)) then (to_days(`R`.`StopDate`) - to_days(`L`.`max_date`)) end)),2) AS `Mgt_Fee(NGN)` from (((`Rentals` `R` join `Tenants` `T` on((`R`.`TenantID` = `T`.`TenantID`))) join `Units` `U` on((`T`.`UnitID` = `U`.`UnitID`))) left join `last_payment_date` `L` on((`U`.`PropertyID` = `L`.`PropertyID`))) where (`R`.`StopDate` > curdate()) order by `U`.`UnitCode` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `rent_tracker`
--

/*!50001 DROP VIEW IF EXISTS `rent_tracker`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_unicode_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `rent_tracker` AS select `Landlords`.`FullName` AS `FullName`,`Property`.`PropertyName` AS `PropertyName`,`Units`.`UnitCode` AS `UnitCode`,`Tenants`.`Email` AS `Email`,`Rentals`.`RentPrice` AS `RentPrice`,`Rentals`.`StopDate` AS `StopDate` from ((((`Landlords` join `Property`) join `Units`) join `Tenants`) join `Rentals`) where ((`Landlords`.`LandlordID` = `Property`.`LandlordID`) and (`Property`.`ID` = `Units`.`PropertyID`) and (`Units`.`UnitID` = `Tenants`.`UnitID`) and (`Units`.`UnitID` = `Rentals`.`UnitID`)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-13 20:25:42
