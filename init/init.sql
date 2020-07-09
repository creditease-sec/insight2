-- MySQL dump 10.17  Distrib 10.3.18-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: insight2
-- ------------------------------------------------------
-- Server version	5.7.30

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app`
--

CREATE DATABASE insight2 character set utf8;

DROP TABLE IF EXISTS `app`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `appname` varchar(255) NOT NULL,
  `apptype` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `sec_level` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `comment` varchar(255) NOT NULL,
  `check_time` double NOT NULL,
  `offonline_time` double NOT NULL,
  `create_time` double NOT NULL,
  `update_time` double NOT NULL,
  `sec_owner` int(11) NOT NULL,
  `sensitive_data_count` int(11) NOT NULL,
  `sensitive_data` text NOT NULL,
  `secure_level` int(11) NOT NULL,
  `business_cata` text,
  `downtime` int(11) NOT NULL,
  `is_open` int(11) NOT NULL,
  `is_interface` int(11) NOT NULL,
  `is_https` int(11) NOT NULL,
  `eid` varchar(255) NOT NULL,
  `crontab` varchar(255) NOT NULL,
  `op_user_id` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_group_id` (`group_id`),
  CONSTRAINT `app_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app`
--

LOCK TABLES `app` WRITE;
/*!40000 ALTER TABLE `app` DISABLE KEYS */;
/*!40000 ALTER TABLE `app` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `alias` varchar(255) NOT NULL,
  `category` int(11) NOT NULL,
  `author` varchar(255) NOT NULL,
  `publish_time` double NOT NULL,
  `publish_datetime` datetime NOT NULL,
  `modify_time` double NOT NULL,
  `status` int(11) NOT NULL,
  `cover` longtext,
  `summary` text NOT NULL,
  `content_type` int(11) NOT NULL,
  `raw_content` longtext NOT NULL,
  `md_raw_content` longtext NOT NULL,
  `content` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `article`
--

LOCK TABLES `article` WRITE;
/*!40000 ALTER TABLE `article` DISABLE KEYS */;
/*!40000 ALTER TABLE `article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asset`
--

DROP TABLE IF EXISTS `asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `asset` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `app_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `is_open` int(11) NOT NULL,
  `is_https` int(11) NOT NULL,
  `apptype` varchar(255) NOT NULL,
  `status` int(11) NOT NULL,
  `create_time` double NOT NULL,
  `update_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asset`
--

LOCK TABLES `asset` WRITE;
/*!40000 ALTER TABLE `asset` DISABLE KEYS */;
/*!40000 ALTER TABLE `asset` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authmode`
--

DROP TABLE IF EXISTS `authmode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `authmode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `mode` varchar(255) NOT NULL,
  `desc` varchar(255) NOT NULL,
  `config` text NOT NULL,
  `enable` int(11) NOT NULL,
  `create_time` double NOT NULL,
  `update_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authmode`
--

LOCK TABLES `authmode` WRITE;
/*!40000 ALTER TABLE `authmode` DISABLE KEYS */;
/*!40000 ALTER TABLE `authmode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `extension`
--

DROP TABLE IF EXISTS `extension`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `extension` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `eid` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL,
  `type` int(11) NOT NULL,
  `version` varchar(255) NOT NULL,
  `remark` varchar(255) NOT NULL,
  `desc` varchar(255) NOT NULL,
  `status` int(11) NOT NULL,
  `config_template` text NOT NULL,
  `config` text NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `extension`
--

LOCK TABLES `extension` WRITE;
/*!40000 ALTER TABLE `extension` DISABLE KEYS */;
/*!40000 ALTER TABLE `extension` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `extensionlog`
--

DROP TABLE IF EXISTS `extensionlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `extensionlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `eid` varchar(255) NOT NULL,
  `app_id` int(11) NOT NULL,
  `is_auto` int(11) NOT NULL,
  `op_user_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `path` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `status` int(11) NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `extensionlog`
--

LOCK TABLES `extensionlog` WRITE;
/*!40000 ALTER TABLE `extensionlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `extensionlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `desc` varchar(255) NOT NULL,
  `owner_id` int(11) NOT NULL,
  `parent` int(11) NOT NULL,
  `create_time` double NOT NULL,
  `update_time` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `group_owner_id` (`owner_id`),
  CONSTRAINT `group_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
INSERT INTO `group` VALUES (1,'5ec6379fff8390854aea563d','安全部','安全部 ...',1,0,1590048671.29034,1590048671.29034);
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groupuser`
--

DROP TABLE IF EXISTS `groupuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groupuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `groupuser_user_id` (`user_id`),
  KEY `groupuser_group_id` (`group_id`),
  KEY `groupuser_role_id` (`role_id`),
  CONSTRAINT `groupuser_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `groupuser_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `group` (`id`),
  CONSTRAINT `groupuser_ibfk_3` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groupuser`
--

LOCK TABLES `groupuser` WRITE;
/*!40000 ALTER TABLE `groupuser` DISABLE KEYS */;
INSERT INTO `groupuser` VALUES (1,'5ec6379fff8390854aea563e',1,1,3,1590048671.33214);
/*!40000 ALTER TABLE `groupuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `message_id` varchar(255) NOT NULL,
  `message_type` varchar(255) NOT NULL,
  `title` text NOT NULL,
  `content` text NOT NULL,
  `to_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `message_to_id` (`to_id`),
  CONSTRAINT `message_ibfk_1` FOREIGN KEY (`to_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messagepoint`
--

DROP TABLE IF EXISTS `messagepoint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messagepoint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `message_id` varchar(255) NOT NULL,
  `from_uid` int(11) NOT NULL,
  `to_uid` int(11) NOT NULL,
  `title` text NOT NULL,
  `content` text NOT NULL,
  `total_points` varchar(255) NOT NULL,
  `frozen_points` varchar(255) NOT NULL,
  `available_points` varchar(255) NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messagepoint`
--

LOCK TABLES `messagepoint` WRITE;
/*!40000 ALTER TABLE `messagepoint` DISABLE KEYS */;
/*!40000 ALTER TABLE `messagepoint` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `level` int(11) NOT NULL,
  `accesses` text,
  `desc` varchar(255) NOT NULL,
  `type` int(11) NOT NULL,
  `default` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'5ec6379fff8390854aea5639','超级管理员',0,'action.authmode.AuthModeTest,action.authmode.AuthModeList,action.authmode.AuthModeAll,action.authmode.AuthModeDel,action.authmode.AuthModeUpsert,action.role.RoleList,action.role.RoleAdd,action.role.RoleDel,action.role.RoleDefault,action.point.PointFrozen,action.point.PointReward,action.point.PointList,action.point.PointLog,action.point.PointUnFrozen,action.group.GroupList,action.group.GroupUpsert,action.groupuser.GroupUserDel,action.groupuser.GroupUserUpsert,action.group.GroupDel,action.groupuser.GroupUserList,action.group.GroupOwnerSet,action.article.ArticleDel,action.article.ArticleUpsert,action.category.CategoryUpsert,action.category.CategoryDel,action.extension.ExtensionLogList,action.extension.ExtensionDel,action.extension.ExtensionRun,action.extension.ExtensionCrontabCalendar,action.extension.ExtensionLogAdd,action.extension.ExtensionConfig,action.extension.ExtensionEnable,action.extension.ExtensionUpload,action.extension.ExtensionList,action.vullog.VulLogList,action.vullog.VulLogDel,action.system.SystemConfig,action.system.SystemMailConfig,action.system.SystemConfigGet,action.system.SystemVulConfig,action.vul.VulDelay,action.vul.VulSendNotificationEmail,action.vul.VulExport,action.vul.VulList,action.assets.AssetImport,action.assets.AssetGet,action.assets.AssetDel,action.assets.AssetAdd,action.assets.AssetList,action.assets.AssetAll,action.user.UserList,action.user.UserAdd,action.user.UserDel,action.user.UserClear,action.docs.LogList,action.app.AppList,action.app.AppDel,action.app.AppExConfig,action.app.AppAdd,action.app.AppGet,action.auditing.AuditingIgnore,action.auditing.AuditingUndo,action.auditing.AuditingConfirm,action.auditing.AuditingReject,action.auditing.AuditingFixed','',0,0),(2,'5ec6379fff8390854aea563a','普通用户',5,'','',0,0),(3,'5ec6379fff8390854aea563b','安全人员',8,'','',1,0);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `systemsettings`
--

DROP TABLE IF EXISTS `systemsettings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `systemsettings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `smtp_host` varchar(255) DEFAULT NULL,
  `smtp_port` varchar(255) DEFAULT NULL,
  `smtp_user` varchar(255) DEFAULT NULL,
  `smtp_pass` varchar(255) DEFAULT NULL,
  `smtp_head` varchar(255) DEFAULT NULL,
  `smtp_sign` varchar(255) DEFAULT NULL,
  `smtp_auth_type` varchar(255) DEFAULT NULL,
  `mail_list` varchar(255) DEFAULT NULL,
  `vul_setting` varchar(255) DEFAULT NULL,
  `global_setting` varchar(255) DEFAULT NULL,
  `point_setting` varchar(255) DEFAULT NULL,
  `site_status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `systemsettings`
--

LOCK TABLES `systemsettings` WRITE;
/*!40000 ALTER TABLE `systemsettings` DISABLE KEYS */;
INSERT INTO `systemsettings` VALUES (1,'5ec6379fff8390854aea563f','','25','','88888888','','',NULL,'',NULL,'{\"group_member_limit\": \"10\", \"isCreateGroup\": \"1\", \"isSendEmail\": \"1\"}','{\"one_level_point\": 1, \"three_level_point\": 1, \"times_level_point\": 1, \"other_level_point\": 1, \"two_level_point\": 1, \"ti_level_point\": 1}',NULL);
/*!40000 ALTER TABLE `systemsettings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test` (
  `_id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test`
--

LOCK TABLES `test` WRITE;
/*!40000 ALTER TABLE `test` DISABLE KEYS */;
/*!40000 ALTER TABLE `test` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `nickname` varchar(255) NOT NULL,
  `avatar` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `token_enable` int(11) NOT NULL,
  `is_del` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `enable` int(11) NOT NULL,
  `ldap_online` int(11) NOT NULL,
  `ldap_offline_time` double NOT NULL,
  `auth_from` varchar(255) NOT NULL,
  `role_id` int(11) NOT NULL,
  `create_time` double NOT NULL,
  `update_time` double NOT NULL,
  `active_time` double NOT NULL,
  `login_time` double NOT NULL,
  `total_points` int(11) NOT NULL,
  `frozen_points` int(11) NOT NULL,
  `available_points` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_username` (`username`),
  KEY `user_role_id` (`role_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'5ec6379fff8390854aea563c','admin','','','',1,0,'','1ceabd2cb3b5ae2f7398cf23749b559e',1,0,0,'LOCAL',1,1590048671.24865,1590048671.24865,1590048671.24865,0,0,0,0);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vul`
--

DROP TABLE IF EXISTS `vul`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vul` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `vul_name` varchar(255) DEFAULT NULL,
  `vul_type` int(11) NOT NULL,
  `vul_level` int(11) NOT NULL,
  `self_rank` varchar(255) DEFAULT NULL,
  `vul_desc_type` int(11) NOT NULL,
  `vul_poc` longtext,
  `vul_poc_html` longtext,
  `vul_solution` longtext,
  `vul_solution_html` longtext,
  `article_id` varchar(255) DEFAULT NULL,
  `audit_user_id` int(11) NOT NULL,
  `reply` text,
  `user_id` int(11) NOT NULL,
  `submit_time` double NOT NULL,
  `audit_time` double NOT NULL,
  `notice_time` double NOT NULL,
  `update_time` double NOT NULL,
  `fix_time` double NOT NULL,
  `vul_status` int(11) NOT NULL,
  `asset_level` int(11) NOT NULL,
  `real_rank` int(11) NOT NULL,
  `score` int(11) NOT NULL,
  `risk_score` int(11) NOT NULL,
  `left_risk_score` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  `vul_source` int(11) NOT NULL,
  `send_msg` int(11) NOT NULL,
  `is_retest` int(11) NOT NULL,
  `layer` int(11) NOT NULL,
  `delay_days` int(11) NOT NULL,
  `delay_reason` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vul`
--

LOCK TABLES `vul` WRITE;
/*!40000 ALTER TABLE `vul` DISABLE KEYS */;
/*!40000 ALTER TABLE `vul` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vullog`
--

DROP TABLE IF EXISTS `vullog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vullog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_id` varchar(255) NOT NULL,
  `vul_id` int(11) NOT NULL,
  `title` text NOT NULL,
  `user_id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `action` text NOT NULL,
  `content` text NOT NULL,
  `create_time` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vullog`
--

LOCK TABLES `vullog` WRITE;
/*!40000 ALTER TABLE `vullog` DISABLE KEYS */;
/*!40000 ALTER TABLE `vullog` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-05-21 16:20:43
