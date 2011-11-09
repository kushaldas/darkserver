CREATE TABLE dark_gnubuildid (
    id int AUTO_INCREMENT NOT NULL PRIMARY KEY,
    elfname varchar(255),
    installpath varchar(500),
    buildid varchar(100),
    rpm_name varchar(255)
);

CREATE INDEX gnubuildid_id ON dark_gnubuildid (buildid);
CREATE INDEX gnubuildid_rpm ON dark_gnubuildid (rpm_name);

