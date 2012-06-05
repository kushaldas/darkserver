CREATE TABLE buildid_gnubuildid (
    id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
    elfname varchar(255),
    instpath varchar(500),
    build_id varchar(100),
    rpm_name varchar(255),
    distro varchar(100)
);

CREATE INDEX gnubuildid_id_idx ON buildid_gnubuildid (build_id(45));
CREATE INDEX gnubuildid_rpm_idx ON buildid_gnubuildid (rpm_name(50));
