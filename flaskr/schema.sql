DROP TABLE IF EXISTS Clubs;
DROP TABLE IF EXISTS belongsTo;
CREATE TABLE Clubs (
    club_name TEXT PRIMARY KEY,
    president_name TEXT NOT NULL,
    club_code TEXT not null,
    ticketTable_id INTEGER
);

CREATE TABLE belongsTo (
    mem_name TEXT,
    club_name TEXT,
    password TEXT,
    positioned_in TEXT,
    FOREIGN KEY (club_name) REFERENCES Clubs(club_name),
    PRIMARY KEY (club_name,mem_name)
);
