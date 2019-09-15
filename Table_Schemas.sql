CREATE TABLE `air_monitors` (
  `id` int(11) DEFAULT NULL,
  `label` varchar(255) DEFAULT NULL,
  `created_at` varchar(255) DEFAULT NULL,
  `channel` varchar(1) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `last_status_change` bigint(20) DEFAULT NULL COMMENT 'unix timestamp (CST)'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `air_quality` (
  `record_id` int(11) NOT NULL AUTO_INCREMENT,
  `recorded_at` bigint(11) DEFAULT NULL COMMENT 'UTC',
  `AGE` int(11) DEFAULT NULL,
  `A_H` varchar(45) DEFAULT NULL,
  `DEVICE_BRIGHTNESS` varchar(45) DEFAULT NULL,
  `DEVICE_FIRMWAREVERSION` varchar(45) DEFAULT NULL,
  `DEVICE_HARDWAREDISCOVERED` varchar(255) DEFAULT NULL,
  `DEVICE_LOCATIONTYPE` varchar(255) DEFAULT NULL,
  `Flag` varchar(45) DEFAULT NULL,
  `Hidden` varchar(45) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  `Label` varchar(255) DEFAULT NULL,
  `LastSeen` int(11) DEFAULT NULL,
  `LastUpdateCheck` int(11) DEFAULT NULL,
  `Lat` decimal(8,6) DEFAULT NULL,
  `Lon` decimal(8,6) DEFAULT NULL,
  `PM2_5Value` decimal(4,2) DEFAULT NULL,
  `ParentID` int(11) DEFAULT NULL,
  `RSSI` int(11) DEFAULT NULL,
  `State` varchar(45) DEFAULT NULL,
  `Stats` varchar(255) DEFAULT NULL,
  `THINGSPEAK_PRIMARY_ID` varchar(45) DEFAULT NULL,
  `THINGSPEAK_PRIMARY_ID_READ_KEY` varchar(255) DEFAULT NULL,
  `THINGSPEAK_SECONDARY_ID` varchar(45) DEFAULT NULL,
  `THINGSPEAK_SECONDARY_ID_READ_KEY` varchar(255) DEFAULT NULL,
  `Type` varchar(45) DEFAULT NULL,
  `Uptime` int(11) DEFAULT NULL,
  `Version` varchar(45) DEFAULT NULL,
  `humidity` int(11) DEFAULT NULL,
  `is_owner` int(11) DEFAULT NULL,
  `pressure` decimal(10,2) DEFAULT NULL,
  `temp_f` decimal(10,2) DEFAULT NULL,
  `AQI` int(11) DEFAULT NULL,
  `current_pm_2_5` decimal(10,2) DEFAULT NULL COMMENT 'Real time or current PM2.5 value',
  `10_min_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg (v1)',
  `30_min_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg',
  `60_min_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg',
  `6_hr_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg',
  `24_hr_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg',
  `1_wk_avg` decimal(10,2) DEFAULT NULL COMMENT 'pm2.5 avg',
  PRIMARY KEY (`record_id`),
  KEY `ID` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=365068 DEFAULT CHARSET=latin1;