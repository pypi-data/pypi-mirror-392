CREATE TABLE IF NOT EXISTS `profiles` (
    `address`               VARCHAR(255) NOT NULL,
    `data`                  VARCHAR(65535),
    PRIMARY KEY(`address`),
    FOREIGN KEY(`address`) REFERENCES `accounts`(`address`) ON DELETE CASCADE
);
