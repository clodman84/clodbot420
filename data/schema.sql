--The timers stores all the times recorded by SimpleTimer
CREATE TABLE IF NOT EXISTS timers(
    timestamp REAL,
    timer_name TEXT,
    time REAL
);


--based and sqlite pilled
CREATE TABLE IF NOT EXISTS pills(
    timestamp INTEGER,
    pill TEXT,
    basedMessage TEXT,
    senderID INTEGER,
    receiverID INTEGER,
    channelID INTEGER,
    messageID INTEGER,
    guildID INTEGER,
    UNIQUE(pill, guildID)
);

DROP table IF EXISTS pills_fts;
CREATE VIRTUAL TABLE pills_fts USING fts5(pill, guildID UNINDEXED, content='pills', tokenize='trigram');

DROP TRIGGER IF EXISTS pills_ai;
DROP TRIGGER IF EXISTS pills_ad;
DROP TRIGGER IF EXISTS pills_au;

-- Triggers to keep the FTS index up to date.
CREATE TRIGGER pills_ai AFTER INSERT ON pills BEGIN
  INSERT INTO pills_fts(rowid, pill, guildID) VALUES (new.rowid, new.pill, new.guildID);
END;
CREATE TRIGGER pills_ad AFTER DELETE ON pills BEGIN
  INSERT INTO pills_fts(pills_fts, rowid, pill, guildID) VALUES('delete', old.rowid, old.pill, old.guildID);
END;
CREATE TRIGGER pills_au AFTER UPDATE ON pills BEGIN
  INSERT INTO pills_fts(pills_fts, rowid, pill, guildID) VALUES('delete', old.rowid, old.pill, old.guildID);
  INSERT INTO pills_fts(rowid, pill, guildID) VALUES (new.rowid, new.pill, new.guildID);
END;

INSERT INTO pills_fts(pills_fts) VALUES('rebuild');


--Stores all the files used by the --py, /run, etc commands
CREATE TABLE IF NOT EXISTS files(
    created_on TIMESTAMP,
    userID INTEGER,
    filename TEXT,
    content BLOB,
    last_updated TIMESTAMP,
    UNIQUE(userID, filename)
);

DROP table IF EXISTS files_fts;
CREATE VIRTUAL TABLE files_fts USING fts5(filename, userID UNINDEXED, content='files', tokenize='trigram');

DROP TRIGGER IF EXISTS files_ai;
DROP TRIGGER IF EXISTS files_ad;
DROP TRIGGER IF EXISTS files_au;

-- Triggers to keep the FTS index up to date.
CREATE TRIGGER files_ai AFTER INSERT ON files BEGIN
  INSERT INTO files_fts(rowid, filename, userID) VALUES (new.rowid, new.filename, new.userID);
END;
CREATE TRIGGER files_ad AFTER DELETE ON files BEGIN
  INSERT INTO files_fts(files_fts, rowid, filename, userID) VALUES('delete', old.rowid, old.filename, old.userID);
END;
CREATE TRIGGER files_au AFTER UPDATE ON files BEGIN
  INSERT INTO files_fts(files_fts, rowid, filename, userID) VALUES('delete', old.rowid, old.filename, old.userID);
  INSERT INTO files_fts(rowid, filename, userID) VALUES (new.rowid, new.filename, new.userID);
END;

INSERT INTO files_fts(files_fts) VALUES('rebuild');
