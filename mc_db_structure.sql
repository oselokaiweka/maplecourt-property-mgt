CREATE DATABASE  IF NOT EXISTS `maplecourt` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `maplecourt`;
-- MySQL dump 10.13  Distrib 8.0.32, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: maplecourt
-- ------------------------------------------------------
-- Server version	8.0.32-0ubuntu0.22.04.2

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
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Cashflow`
--

LOCK TABLES `Cashflow` WRITE;
/*!40000 ALTER TABLE `Cashflow` DISABLE KEYS */;
INSERT INTO `Cashflow` VALUES (1,'2023-04-02 04:29:00','Credit',50000.00,': 000015230401155925006201003111|Apr. Diesel|1422108259||TOUFIC SABA REF:000015230401155925006201003111',799837.33,799837.33),(2,'2023-04-02 19:38:00','Credit',50000.00,': /21.5/ATMNIP - ANY Account Transfer from SOWEMIMO SOMUYIWA to CHROMETRO NIGERIA LTD',849787.33,849787.33),(3,'2023-04-02 20:15:00','Debit',250000.00,': Via GAPSLITE REF:330337654000002500002304022013 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',599518.58,599518.58),(4,'2023-04-03 18:58:00','Debit',3.75,': 000013230403185745000094381166 VAT ON NIP TRANSFER FOR 000013230403185745000094381166 via GTWORLD Pr TO OKAKAH PATIENCE ESELE ReF:GW330337654000002000002304031858',399246.03,399246.03),(5,'2023-04-03 18:58:00','Debit',50.00,': 000013230403185745000094381166 NIP TRANSFER COMMISSION FOR 000013230403185745000094381166 via GTWORLD Pr TO OKAKAH PATIENCE ESELE ReF:GW330337654000002000002304031858',399249.78,399249.78),(6,'2023-04-03 18:58:00','Debit',200000.00,': 000013230403185745000094381166 via GTWORLD Pr TO OKAKAH PATIENCE ESELE /53.75/REF:GW3303376540000020000023040318 f',399249.78,399249.78),(7,'2023-04-04 20:40:00','Debit',150000.00,': Via GAPSLITE P REF:330337654000001500002304042039 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',249084.23,249084.23),(8,'2023-04-05 14:21:00','Debit',30000.00,': Via GAPSLITE Laptop battery REF:330337654000000300002304051421 from CHROMETRO NIGERIA LTD to ONYEUKWU CHRISTOPHER CHINEDU',219051.98,219051.98),(9,'2023-04-05 14:24:00','Debit',3.75,': 000013230405142421000099531870 VAT ON NIP TRANSFER FOR 000013230405142421000099531870 via GTWORLD Lawani 2 TO UGWU UCHENNA ReF:GW33033765400200000.012304051424',18779.42,18779.42),(10,'2023-04-05 14:24:00','Debit',50.00,': 000013230405142421000099531870 NIP TRANSFER COMMISSION FOR 000013230405142421000099531870 via GTWORLD Lawani 2 TO UGWU UCHENNA ReF:GW33033765400200000.012304051424',18783.17,18783.17),(11,'2023-04-05 14:24:00','Debit',200000.01,': 000013230405142421000099531870 via GTWORLD Lawani 2 TO UGWU UCHENNA /53.75/REF:GW33033765400200000.0123040514',18783.17,18783.17),(12,'2023-04-07 17:10:00','Debit',18000.00,': Via GAPSLITE Lawani 2 REF:330337654000000180002304071709 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',763.82,763.82),(13,'2023-04-08 09:51:00','Credit',440017.00,': 000015230408094920449212013884|SC, mngmnt, incidentals, reimburse|221933706||ENKOLAR BUSINESS MANAGEMENT LIMITED REF:000015230408094920449212013884',440730.82,440730.82),(14,'2023-04-08 09:57:00','Credit',320979.00,': 000015230408095612748220024615|SC Etc MC2CHROMETRO NIGERIA LTD|221933911||ENKOLAR BUSINESS MANAGEMENT LIMITED REF:000015230408095612748220024615',761659.82,761659.82),(15,'2023-04-08 12:30:00','Debit',355000.00,': Via GAPSLITE General REF:330337654000003550002304081230 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',406278.19,406278.19),(16,'2023-04-08 16:20:00','Debit',60000.00,': Via GAPSLITE Gen REF:330337654000000600002304081619 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',346213.69,346213.69),(17,'2023-04-10 02:40:00','Debit',150000.00,': Via GAPSLITE P REF:330337654000001500002304100239 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',196052.44,196052.44),(18,'2023-04-11 10:35:00','Debit',1.87,': 000013230411103334000113504151 VAT ON NIP TRANSFER FOR 000013230411103334000113504151 via GTWORLD TO ITORO ESUA EKPO ReF:GW330337654000000500002304111033',145965.62,145965.62),(19,'2023-04-11 10:35:00','Debit',25.00,': 000013230411103334000113504151 NIP TRANSFER COMMISSION FOR 000013230411103334000113504151 via GTWORLD TO ITORO ESUA EKPO ReF:GW330337654000000500002304111033',145967.49,145967.49),(20,'2023-04-11 10:35:00','Debit',50000.00,': 000013230411103334000113504151 via GTWORLD TO ITORO ESUA EKPO /26.875/REF:GW3303376540000005000023041110 f',145967.49,145967.49),(21,'2023-04-11 14:22:00','Debit',80000.20,': Via GAPSLITE REF:330337654000080000.22304111422 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',65881.29,65881.29),(22,'2023-04-12 09:14:00','Debit',65000.00,': Via GAPSLITE REF:330337654000000650002304120913 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',798.51,798.51),(23,'2023-04-18 08:49:00','Credit',130958.00,': 000015230418084723239472031368|Bal Feb 23 sc|222639222||ENKOLAR BUS.MGT LTD REF:000015230418084723239472031368',131702.21,131702.21),(24,'2023-04-19 09:10:00','Debit',25.00,': 000013230419091009000132759809 NIP TRANSFER COMMISSION FOR 000013230419091009000132759809 via GTWORLD Lawani 2 TO NWEKE CHIBUIKE MIRACLE ReF:GW330337654000000230002304190910',108646.28,108646.28),(25,'2023-04-19 09:23:00','Debit',105000.00,': Via GAPSLITE REF:330337654000001050002304190923 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',3533.40,3533.40),(26,'2023-04-19 12:23:00','Credit',40956.15,': 000014230419122243245551417439|TRFManagement fee to March 31stFRM ATSEN JONATHAN AHUA TO CHROMETRO NIGERIA LTD|000014230419122145281853517010||ATSEN JONATHAN AHUA REF:000014230419122243245551417439',44439.55,44439.55),(27,'2023-04-19 12:31:00','Credit',35621.04,': 000014230419122954214883723542|TRFMangement Fee Apil - June 2023FRM ATSEN JONATHAN AHUA TO CHROMETRO NIGERIA LTD|000014230419122846277568022974||ATSEN JONATHAN AHUAREF:000014230419122954214883723542',80010.59,80010.59),(28,'2023-04-23 09:03:00','Credit',57600.00,': 000015230423090221723216020288|16 7% of 360k MC2F2|223033421||ENKOLAR BUSINESS MANAGEMENT LIMITED REF:000015230423090221723216020288',58441.26,58441.26),(29,'2023-04-24 06:46:00','Debit',58000.00,': Via GAPSLITE REF:330337654000000580002304240646 from CHROMETRO NIGERIA LTD to IWEKA OSELOKA CHINEDU',374.61,374.61),(30,'2023-05-01 02:58:00','Debit',140.49,':',161.04,161.04),(31,'2023-05-01 18:54:00','Credit',50000.00,': 000015230501185250481256013574|Diesel|1468188380||TOUFIC SABA REF:000015230501185250481256013574',50251.53,50251.53),(32,'2023-05-02 10:39:00','Credit',100000.00,': MBANKING - Flat 4 April and May Diesel Contribution REF:666961658970947300001111826163 ANY Account Transfer from IMAM MOHAMMED SALIHU to CHROMETRO NIGERIA LTD',150188.63,150188.63),(33,'2023-05-02 10:56:00','Credit',50000.00,': /21.5/ATMNIP - ANY Account Transfer from SOWEMIMO SOMUYIWA to CHROMETRO NIGERIA LTD',200138.63,200138.63),(34,'2023-05-02 12:08:00','Credit',100000.00,': Via GTWorld Diesel April and May REF:323299801000001000002305021306 from TALSMA, ADAM to CHROMETRO NIGERIA LTD',300088.63,300088.63),(35,'2023-05-02 16:19:00','Debit',50.00,': 000013230502161912000165583026 NIP TRANSFER COMMISSION FOR 000013230502161912000165583026 via GTWORLD Lawani2-plumb-labour-bal TO UGWU UCHENNA ReF:GW330337654000000900002305021619',209938.08,209938.08),(36,'2023-05-02 16:19:00','Debit',90000.00,': 000013230502161912000165583026 via GTWORLD Lawani2-plumb-labour-bal TO UGWU UCHENNA /53.75/REF:GW3303376540000009000023050216',209938.08,209938.08),(37,'2023-05-03 12:13:00','Debit',0.75,': 000013230503121311000167612887 VAT ON NIP TRANSFER FOR 000013230503121311000167612887 via GTWORLD Mc1-rodent-bait TO MAIWADA YOHANNA ReF:GW330337654000000050002305031213',204882.49,204882.49),(38,'2023-05-03 12:13:00','Debit',10.00,': 000013230503121311000167612887 NIP TRANSFER COMMISSION FOR 000013230503121311000167612887 via GTWORLD Mc1-rodent-bait TO MAIWADA YOHANNA ReF:GW330337654000000050002305031213',204883.24,204883.24),(39,'2023-05-03 12:13:00','Debit',5000.00,': 000013230503121311000167612887 via GTWORLD Mc1-rodent-bait TO MAIWADA YOHANNA /10.75/REF:GW3303376540000000500023050312',204883.24,204883.24),(40,'2023-05-03 17:08:00','Credit',135000.00,': Via GTWorld Refund REF:322324094000001350002305031708 from IWEKA OSELOKA CHINEDU to CHROMETRO NIGERIA LTD',339833.24,339833.24),(41,'2023-05-03 17:21:00','Debit',3.75,': 000013230503172034000168512075 VAT ON NIP TRANSFER FOR 000013230503172034000168512075 via GTWORLD Mc1-diesel-465/730/339450 TO ALEXANDER AGADA ReF:GW330337654000003185002305031720',20933.30,20933.30),(42,'2023-05-03 17:21:00','Debit',50.00,': 000013230503172034000168512075 NIP TRANSFER COMMISSION FOR 000013230503172034000168512075 via GTWORLD Mc1-diesel-465/730/339450 TO ALEXANDER AGADA ReF:GW330337654000003185002305031720',20937.05,20937.05),(43,'2023-05-03 17:21:00','Debit',318500.00,': 000013230503172034000168512075 via GTWORLD Mc1-diesel-465/730/339450 TO ALEXANDER AGADA /53.75/REF:GW3303376540000031850023050317 f',20937.05,20937.05);
/*!40000 ALTER TABLE `Cashflow` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Landlords`
--

LOCK TABLES `Landlords` WRITE;
/*!40000 ALTER TABLE `Landlords` DISABLE KEYS */;
INSERT INTO `Landlords` VALUES (1,'Enkolar Business Mgt Ltd','carolinemorah@gmail.com','+2349059221868'),(2,'Atsen Ahua','atsen.ahua@gmail.com','+2349097099360'),(3,'Shaver Multi-Business Ltd','paulbemgba@gmail.com','+2348032332476');
/*!40000 ALTER TABLE `Landlords` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Maintenance`
--

LOCK TABLES `Maintenance` WRITE;
/*!40000 ALTER TABLE `Maintenance` DISABLE KEYS */;
/*!40000 ALTER TABLE `Maintenance` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Property`
--

LOCK TABLES `Property` WRITE;
/*!40000 ALTER TABLE `Property` DISABLE KEYS */;
INSERT INTO `Property` VALUES (1,'Maple Court 1','18 Audu Ogbeh, Jabi, Abuja',1),(2,'Maple Court 2A','Plot 1002 Rajab Naibi, Life-Camp, Abuja',1),(3,'Maple Court 2B','Plot 1002 Rajab Naibi, Life-Camp, Abuja',2),(4,'Maple Court 2C','Plot 1002 Rajab Naibi, Life-Camp, Abuja',3);
/*!40000 ALTER TABLE `Property` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Rentals`
--

LOCK TABLES `Rentals` WRITE;
/*!40000 ALTER TABLE `Rentals` DISABLE KEYS */;
INSERT INTO `Rentals` VALUES (100,1,'2022-08-15',3500000,450000,250000,'Signed',6,'2023-08-15'),(101,2,'2021-11-01',3000000,450000,NULL,'Pending',5,'2022-11-01'),(102,3,'2021-07-15',3000000,450000,NULL,'Pending',4,'2022-07-15'),(103,4,'2022-09-15',3000000,450000,NULL,'Pending',3,'2023-09-15'),(104,5,'2022-01-01',3000000,450000,NULL,'Pending',2,'2023-01-01'),(105,6,'2022-01-12',3000000,450000,NULL,'Pending',1,'2023-01-12'),(106,7,'2022-08-15',3500000,450000,250000,'Signed',7,'2023-08-15'),(107,8,'2020-12-31',1905000,395000,NULL,'signed',8,'2023-07-01'),(108,9,'2021-03-31',1905000,395000,NULL,'signed',9,'2023-07-01'),(109,10,'2022-03-15',1905000,395000,NULL,'pending',10,'2023-03-15'),(110,11,'2022-03-01',1905000,395000,NULL,'pending',11,'2023-03-01'),(111,12,'2022-06-01',1905000,395000,NULL,'pending',12,'2023-06-10'),(112,13,'2022-07-01',1905000,395000,NULL,'pending',13,'2023-07-10');
/*!40000 ALTER TABLE `Rentals` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Supplies`
--

LOCK TABLES `Supplies` WRITE;
/*!40000 ALTER TABLE `Supplies` DISABLE KEYS */;
/*!40000 ALTER TABLE `Supplies` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Tenants`
--

LOCK TABLES `Tenants` WRITE;
/*!40000 ALTER TABLE `Tenants` DISABLE KEYS */;
INSERT INTO `Tenants` VALUES (1,'Segun','Oguntoyinbo','hanovia_medical@yahoo.co.uk','+2348035033941',6),(2,'Franck','Momgbe','franckmon@yahoo.fr','+2347036623028',5),(3,'Muhammed','Imam','mo_imam@yahoo.com','+2348092228742',4),(4,'Dr. L','Jack','warijack@gmail.com','+2348077066423',3),(5,'Adam','Talsma','abtalsma@gmail.com','+2348183273915',2),(6,'Toufic','Saba','touficms@gmail.com','+2348031333334',1),(7,'Somuyiwa','Sowemimo','office@muyi-sowemimolegal.com','+2348130101275',7),(8,'Atsen','Ahua','oselokaiweka@gmail.com','+2349097099360',8),(9,'Paul','Gbemba','yellosey@yahoo.co.uk','+2348032332476',9),(10,'Isaiah','David','isaiahdavid76@gmail.com','+2348039183276',10),(11,'Paul','Lasu','paullasu@aol.com','+2348055261758',11),(12,'Ibrahim','Suleiman','ibrahim.h.suleiman@gmail.com','+2348036566493',12),(13,'Alex','Ogbu','aogbu@klausyale.com','+2348095040608',13);
/*!40000 ALTER TABLE `Tenants` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `Units`
--

LOCK TABLES `Units` WRITE;
/*!40000 ALTER TABLE `Units` DISABLE KEYS */;
INSERT INTO `Units` VALUES (1,'MC1F1',3,4,1),(2,'MC1F2',3,4,1),(3,'MC1F3',3,4,1),(4,'MC1F4',3,4,1),(5,'MC1F5',3,4,1),(6,'MC1F6',3,4,1),(7,'MC1F7',3,4,1),(8,'MC2F1',3,4,3),(9,'MC2F2',3,4,4),(10,'MC2F3',3,4,2),(11,'MC2F4',3,4,2),(12,'MC2F5',3,4,2),(13,'MC2F6',3,4,2);
/*!40000 ALTER TABLE `Units` ENABLE KEYS */;
UNLOCK TABLES;

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

-- Dump completed on 2023-05-04 21:58:37
