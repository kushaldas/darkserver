CREATE TABLE buildsystems (
  id int(11) NOT NULL AUTO_INCREMENT,
  sys_name varchar(45) NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE buildservers (
    id int(11) NOT NULL AUTO_INCREMENT,
    sys_id int(11) DEFAULT NULL,
    url varchar(255) DEFAULT NULL,
    PRIMARY KEY (id),
    KEY fk_buildsystems_id (id),
    KEY fk_buildservers_buildsystem (sys_id),
    CONSTRAINT fk_buildservers_buildsystem FOREIGN KEY (sys_id) \
      REFERENCES buildsystems (id) \
      ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE jobstatus (
    id int(11) NOT NULL AUTO_INCREMENT,
    status_name varchar(45) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE jobqueue (
    id int(11) NOT NULL AUTO_INCREMENT,
    buildserver_id int(11) DEFAULT NULL,
    buildjob_id int(11) NOT NULL,
    status_id int(11) NOT NULL,
    PRIMARY KEY (id),
    KEY fk_jobqueue_buildserver (buildserver_id),
    KEY fk_jobqueue_status (status_id),
    CONSTRAINT fk_jobqueue_buildserver FOREIGN KEY (buildserver_id) \
      REFERENCES buildservers (id) \
      ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT fk_jobqueue_status FOREIGN KEY (status_id) \
      REFERENCES jobstatus (id) \
      ON DELETE NO ACTION ON UPDATE NO ACTION,
) ENGINE=InnoDB DEFAULT CHARSET=utf8
