CREATE TABLE assets (
        id INTEGER NOT NULL,
        "majorArea" VARCHAR,
        "minorArea" VARCHAR,
        "assetType" VARCHAR,
        model VARCHAR,
        description VARCHAR,
        "assetState" VARCHAR,
        satellite VARCHAR,
        station VARCHAR,
        "gpsLat" DOUBLE,
        "gpsLng" DOUBLE,
        "createdBy" VARCHAR,
        "createdDate" DATETIME DEFAULT (CURRENT_TIMESTAMP),
        "updatedBy" VARCHAR,
        "updatedDate" DATETIME,
        PRIMARY KEY (id),
        FOREIGN KEY("createdBy") REFERENCES users (initials),
        FOREIGN KEY("updatedBy") REFERENCES users (initials)
);
CREATE INDEX ix_assets_id ON assets (id);


CREATE TABLE temp (
        "majorArea" VARCHAR,
        "minorArea" VARCHAR,
        "assetType" VARCHAR,
        description VARCHAR,
        "assetState" VARCHAR,
        satellite VARCHAR,
        station VARCHAR,
        "createdBy" INTEGER
);



INSERT INTO assets (majorArea,minorArea,assetType,
description,assetState,satellite,station,createdBy)
select * from temp;

