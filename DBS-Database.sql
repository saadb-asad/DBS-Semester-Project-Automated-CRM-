-- DDL Queries (Structural foundation of the Database)


-- CREATE DATABASE AutomatedCRM;
-- GO
-- USE AutomatedCRM;
-- GO

CREATE TABLE Regions (
    RegionID INT PRIMARY KEY IDENTITY(1,1),
    RegionName VARCHAR(100) NOT NULL
);

CREATE TABLE ProductCategories (
    CategoryID INT PRIMARY KEY IDENTITY(1,1),
    CategoryName VARCHAR(100) NOT NULL
);

CREATE TABLE MarketingCampaigns (
    CampaignID INT PRIMARY KEY IDENTITY(1,1),
    CampaignName VARCHAR(100),
    Budget DECIMAL(10, 2),
    StartDate DATE,
    EndDate DATE
);

CREATE TABLE SalesAgents (
    AgentID INT PRIMARY KEY IDENTITY(1,1),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    RegionID INT, 
    FOREIGN KEY (RegionID) REFERENCES Regions(RegionID)
);

CREATE TABLE Products (
    ProductID INT PRIMARY KEY IDENTITY(1,1),
    ProductName VARCHAR(100),
    Price DECIMAL(10, 2),
    CategoryID INT,
    FOREIGN KEY (CategoryID) REFERENCES ProductCategories(CategoryID)
);

CREATE TABLE Leads (
    LeadID INT PRIMARY KEY IDENTITY(1,1),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Status VARCHAR(20) DEFAULT 'New',
    CampaignID INT,
    AssignedAgentID INT,
    FOREIGN KEY (CampaignID) REFERENCES MarketingCampaigns(CampaignID),
    FOREIGN KEY (AssignedAgentID) REFERENCES SalesAgents(AgentID)
);

CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY IDENTITY(1,1),
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Email VARCHAR(100),
    Phone VARCHAR(20),
    LeadID INT UNIQUE,
    AssignedAgentID INT,
    FOREIGN KEY (LeadID) REFERENCES Leads(LeadID),
    FOREIGN KEY (AssignedAgentID) REFERENCES SalesAgents(AgentID)
);

CREATE TABLE Deals (
    DealID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT,
    AgentID INT,
    DealDate DATETIME DEFAULT GETDATE(),
    TotalAmount DECIMAL(12, 2) DEFAULT 0.00,
    Stage VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (AgentID) REFERENCES SalesAgents(AgentID)
);

CREATE TABLE DealtItems (
    ItemID INT PRIMARY KEY IDENTITY(1,1),
    DealID INT,
    ProductID INT,
    Quantity INT,
    SoldPrice DECIMAL(10, 2),
    FOREIGN KEY (DealID) REFERENCES Deals(DealID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

CREATE TABLE Interactions (
    InteractionID INT PRIMARY KEY IDENTITY(1,1),
    CustomerID INT,
    AgentID INT,
    InteractionDate DATETIME DEFAULT GETDATE(),
    Type VARCHAR(50), -- Call, Email, Meeting
    Notes NVARCHAR(MAX),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (AgentID) REFERENCES SalesAgents(AgentID)
);

CREATE TABLE Tasks (
    TaskID INT PRIMARY KEY IDENTITY(1,1),
    Description VARCHAR(255),
    DueDate DATETIME,
    IsCompleted BIT DEFAULT 0,
    CustomerID INT,
    AgentID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (AgentID) REFERENCES SalesAgents(AgentID)
);

CREATE TABLE Reviews (
    ReviewID INT PRIMARY KEY IDENTITY(1,1),
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    ComplaintText NVARCHAR(MAX),
    CustomerID INT,
    AgentID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (AgentID) REFERENCES SalesAgents(AgentID)
);



-- DML Queries (Populating the Automation Data)


INSERT INTO Regions (RegionName) VALUES ('North America'), ('Europe'), ('Asia');
INSERT INTO ProductCategories (CategoryName) VALUES ('Software'), ('Hardware');
INSERT INTO MarketingCampaigns (CampaignName, Budget) VALUES ('Summer Sale', 5000.00);

INSERT INTO SalesAgents (FirstName, LastName, Email, RegionID) 
VALUES ('John', 'Smith', 'john@crm.com', 1), ('Alice', 'Wonder', 'alice@crm.com', 2);

INSERT INTO Products (ProductName, Price, CategoryID) 
VALUES ('CRM License', 199.99, 1), ('Laptop', 1200.00, 2);

INSERT INTO Leads (FirstName, LastName, CampaignID, AssignedAgentID) 
VALUES ('Bruce', 'Wayne', 1, 1);

INSERT INTO Customers (FirstName, LastName, Email, LeadID, AssignedAgentID) 
VALUES ('Bruce', 'Wayne', 'bruce@wayne.com', 1, 1);

INSERT INTO Deals (CustomerID, AgentID, Stage, TotalAmount) 
VALUES (1, 1, 'Closed-Won', 1399.99);

INSERT INTO DealtItems (DealID, ProductID, Quantity, SoldPrice) 
VALUES (1, 2, 1, 1200.00), (1, 1, 1, 199.99);


-- SQL Join ()