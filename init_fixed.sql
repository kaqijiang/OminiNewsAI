CREATE DATABASE IF NOT EXISTS news;
USE news;

# 用户表
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_superuser` tinyint(1) NOT NULL DEFAULT '0',
  `full_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# 新闻列表
CREATE TABLE `news_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `original_title` varchar(255) DEFAULT NULL COMMENT '原始标题',
  `processed_title` varchar(255) DEFAULT NULL COMMENT '处理后标题',
  `original_content` text COMMENT '原始内容',
  `processed_content` text COMMENT '处理后内容',
  `source_url` varchar(255) DEFAULT NULL COMMENT 'URL',
  `create_time` int(11) DEFAULT '0' COMMENT '邮件时间',
  `type` varchar(255) DEFAULT NULL COMMENT '类型',
  `generated` int(1) DEFAULT '0' COMMENT '生成状态',
  `send` int(1) DEFAULT '0' COMMENT '发布状态',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

# 新闻分类
CREATE TABLE `news_categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(25) NOT NULL,
  `category_value` varchar(100) NOT NULL,
  `rss_feed_url` varchar(255) DEFAULT NULL COMMENT 'RSS订阅源URL',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

# 平台表
CREATE TABLE `platforms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `platform_name` varchar(50) NOT NULL COMMENT '平台名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# 授权信息表 (platform_credentials)
CREATE TABLE `platform_credentials` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `platform_id` int(11) NOT NULL,
  `account` varchar(255) NOT NULL COMMENT '账号',
  `password` varchar(255) NOT NULL COMMENT '密码',
  `cookie` text COMMENT 'Cookie信息',
  `session_info` text COMMENT 'Session信息',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# API Key 表 (api_keys)
CREATE TABLE `api_keys` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `api_key` varchar(255) NOT NULL COMMENT 'API Key',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

# 发布历史表
CREATE TABLE `publish_history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `news_id` int(11) NOT NULL,
  `publish_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`news_id`) REFERENCES `news_list` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 