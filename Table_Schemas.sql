CREATE TABLE `readings` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sensor_id` int(11) DEFAULT NULL,
  `context_id` int(11) DEFAULT NULL,
  `pm1.0` decimal(10,2) DEFAULT NULL,
  `pm2.5` decimal(10,2) DEFAULT NULL,
  `pm2.5_10minute` decimal(10,2) DEFAULT NULL,
  `pm2.5_30minute` decimal(10,2) DEFAULT NULL,
  `pm2.5_60minute` decimal(10,2) DEFAULT NULL,
  `pm2.5_6hour` decimal(10,2) DEFAULT NULL,
  `pm2.5_24hour` decimal(10,2) DEFAULT NULL,
  `pm2.5_1week` decimal(10,2) DEFAULT NULL,
  `pm10.0` decimal(10,2) DEFAULT NULL,
  `0.3_um_count` decimal(10,2) DEFAULT NULL,
  `0.5_um_count` decimal(10,2) DEFAULT NULL,
  `1.0_um_count` decimal(10,2) DEFAULT NULL,
  `2.5_um_count` decimal(10,2) DEFAULT NULL,
  `5.0_um_count` decimal(10,2) DEFAULT NULL,
  `10.0_um_count` decimal(10,2) DEFAULT NULL,
  `humidity` decimal(10,2) DEFAULT NULL,
  `temperature` decimal(10,2) DEFAULT NULL COMMENT 'Temp inside sensor housing. Typically 8*F higher than ambient conditions',
  `pressure` decimal(10,2) DEFAULT NULL,
  `voc` decimal(10,2) DEFAULT NULL,
  `ozone1` decimal(10,2) DEFAULT NULL,
  `ten_minute_aqi` decimal(10,2) DEFAULT NULL,
  `aqi_level` varchar(255) DEFAULT NULL,
  `time_stamp` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE `contexts` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sensor_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `location_type` enum('OUTSIDE','INSIDE') DEFAULT NULL,
  `latitude` decimal(8,6) DEFAULT NULL,
  `longitude` decimal(8,6) DEFAULT NULL,
  `altitude` int(11) DEFAULT NULL,
  `channel_state` enum('No PM','PM-A','PM-B','PM-A+PM-B') DEFAULT NULL,
  `channel_flags` enum('Normal','A-Downgraded','B-Downgraded','A+B-Downgraded') DEFAULT NULL,
  `context_created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `sensors` (
  `id` int(11) unsigned NOT NULL,
  `context_id` int(11) DEFAULT NULL,
  `latest_reading_id` int(11) DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  `last_status_change` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



CREATE TABLE `twitter_sensors` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sensor_id` int(11) DEFAULT NULL,
  `twitter_label` varchar(255) DEFAULT NULL,
  `send_tweets` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;




