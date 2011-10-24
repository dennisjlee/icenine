-- MySQL dump 10.11
--
-- Host: localhost    Database: icenine2
-- ------------------------------------------------------
-- Server version	5.0.32-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

USE icenine2;

--
-- Table structure for table `ice9_directory`
--

DROP TABLE IF EXISTS `ice9_directory`;
CREATE TABLE `ice9_directory` (
  `id` int(11) NOT NULL auto_increment,
  `type` varchar(20) NOT NULL,
  `name` varchar(150) NOT NULL,
  `parent_id` int(11) default NULL,
  `found` tinyint(1) NOT NULL,
  `info_link` varchar(255) NOT NULL,
  `relative_path` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `type` (`type`,`name`,`parent_id`),
  KEY `ice9_directory_type` (`type`),
  KEY `ice9_directory_name` (`name`),
  KEY `ice9_directory_parent_id` (`parent_id`),
  KEY `ice9_directory_found` (`found`),
  KEY `ice9_directory_relative_path` (`relative_path`)
) ENGINE=MyISAM AUTO_INCREMENT=79 DEFAULT CHARSET=utf8;

--
-- Table structure for table `ice9_file`
--

DROP TABLE IF EXISTS `ice9_file`;
CREATE TABLE `ice9_file` (
  `id` int(11) NOT NULL auto_increment,
  `type` varchar(20) NOT NULL,
  `name` varchar(150) NOT NULL,
  `path` varchar(255) NOT NULL,
  `size` bigint(20) unsigned NOT NULL,
  `addition_date` datetime NOT NULL,
  `found` tinyint(1) NOT NULL,
  `directory_id` int(11) NOT NULL,
  `info_link` varchar(255) NOT NULL,
  `relative_path` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `path` (`path`),
  KEY `ice9_file_type` (`type`),
  KEY `ice9_file_name` (`name`),
  KEY `ice9_file_addition_date` (`addition_date`),
  KEY `ice9_file_found` (`found`),
  KEY `ice9_file_directory_id` (`directory_id`),
  KEY `ice9_file_relative_path` (`relative_path`)
) ENGINE=MyISAM AUTO_INCREMENT=4097 DEFAULT CHARSET=utf8;

--
-- Table structure for table `ice9_log`
--

DROP TABLE IF EXISTS `ice9_log`;
CREATE TABLE `ice9_log` (
  `id` int(11) NOT NULL auto_increment,
  `completed` tinyint(1) NOT NULL,
  `user_id` int(11) NOT NULL,
  `file_id` int(11) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime default NULL,
  `error_message` varchar(255) NOT NULL,
  `ip_address` char(15) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `ice9_log_user_id` (`user_id`),
  KEY `ice9_log_file_id` (`file_id`),
  KEY `ice9_log_start_time` (`start_time`),
  KEY `ice9_log_ip_address` (`ip_address`)
) ENGINE=MyISAM AUTO_INCREMENT=10838 DEFAULT CHARSET=utf8;

--
-- Table structure for table `ice9_movie`
--

DROP TABLE IF EXISTS `ice9_movie`;
CREATE TABLE `ice9_movie` (
  `file_id` int(11) NOT NULL,
  `keywords` varchar(255) NOT NULL,
  `rating` decimal(6,3) NOT NULL,
  PRIMARY KEY  (`file_id`),
  KEY `ice9_movie_file_id` (`file_id`),
  KEY `ice9_movie_rating` (`rating`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Table structure for table `ice9_user`
--

DROP TABLE IF EXISTS `ice9_user`;
CREATE TABLE `ice9_user` (
  `user_id` int(11) NOT NULL,
  `legacy_id` int(11) NOT NULL,
  `email` varchar(75) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `comment` varchar(255) NOT NULL,
  `addition_date` datetime NOT NULL,
  PRIMARY KEY  (`user_id`),
  UNIQUE KEY `legacy_id` (`legacy_id`),
  KEY `ice9_user_user_id` (`user_id`),
  KEY `ice9_user_email` (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
