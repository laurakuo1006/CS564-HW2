drop table if exists Item;
drop table if exists bids;
drop table if exists User;
drop table if exists Item_Categories;

create table Item (
    ItemID INTEGER PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Currently DOUBLE NOT NULL,
    First_Bid DOUBLE NOT NULL,
    Buy_Price DOUBLE,
    Started DATETIME NOT NULL,
    Ends DATETIME NOT NULL,
    UserID VARCHAR(255) NOT NULL,
    Description TEXT,
    FOREIGN KEY(UserID) References User(UserID)
);

create table bids (
    ItemID INTEGER NOT NULL,
    UserID VARCHAR(255) NOT NULL,
    Time DATETIME NOT NULL,
    Amount DOUBLE NOT NULL,
    PRIMARY KEY(ItemID, UserID, Time),
    FOREIGN KEY(ItemID) References Item(ItemID),
    FOREIGN KEY(UserID) References User(UserID)
);

create table User (
    UserID VARCHAR(255) PRIMARY KEY,
    Country VARCHAR(255),
    Rating INTEGER,
    Location VARCHAR(255)
);

create table Item_Categories (
    ItemID INTEGER NOT NULL,
    Category VARCHAR(255) NOT NULL,
    PRIMARY KEY(ItemID, Category)
    FOREIGN KEY(ItemID) References Item(ItemID)
);


