VERSIONS = {"v1.0.0": ["""
        CREATE TABLE IF NOT EXISTS `crontab` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `_id` varchar(255) NOT NULL,
          `name` text NOT NULL,
          `uid` int(11) NOT NULL,
          `eid` varchar(255) NOT NULL,
          `crontab` varchar(255) NOT NULL,
          `relate` varchar(255) NOT NULL,
          `relate_id` varchar(255) NOT NULL,
          `enable` int(11) NOT NULL,
          `remark` text NOT NULL,
          `exec_count` int(11) NOT NULL,
          `status` int(11) NOT NULL,
          `log` longtext,
          `config` text NOT NULL,
          `create_time` double NOT NULL,
          `update_time` double NOT NULL,
          `last_time` double NOT NULL,
          `next_time` double NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
    """,
    """
        CREATE TABLE IF NOT EXISTS `crontablog` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `_id` varchar(255) NOT NULL,
          `eid` varchar(255) NOT NULL,
          `content` longtext,
          `start_time` double NOT NULL,
          `end_time` double NOT NULL,
          `create_time` double NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    """
]
}
