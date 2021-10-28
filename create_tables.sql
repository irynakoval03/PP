
CREATE TABLE user(
    userId    SERIAL  NOT NULL,
    username  VARCHAR(45) NOT NULL,
    firstName VARCHAR(45) NOT NULL,
    lastName  VARCHAR(45) NOT NULL,
    email     VARCHAR(45) NOT NULL,
    password  BYTEA   NOT NULL,
    phone     INT     NOT NULL,
    PRIMARY KEY (userId)
);

CREATE TABLE audience(
    audienceId SERIAL  NOT NULL,
    name       VARCHAR(45) NOT NULL,
    status     VARCHAR(45) NOT NULL,
    PRIMARY KEY (audienceId),
);



CREATE TABLE reserve (
    reserveId  INT      NOT NULL,
    begin      DATETIME NOT NULL,
    end        DATETIME NOT NULL,
    userId     INT      NOT NULL,
    audienceId INT      NOT NULL,
    PRIMARY KEY (reserveId),
    FOREIGN KEY (userId) REFERENCES user (userId),
    FOREIGN KEY (audienceId) REFERENCES audience (audienceId)
);