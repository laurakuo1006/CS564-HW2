SELECT COUNT(UserID)
FROM (
    SELECT UserID FROM Item
    INTERSECT 
    SELECT UserID FROM bids
) AS bidder_and_seller;