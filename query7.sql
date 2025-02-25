SELECT COUNT(DISTINCT Item_Categories.Category)
FROM Item_Categories
JOIN Item ON Item_Categories.ItemID = Item.ItemID
JOIN bids ON bids.ItemID = Item.ItemID
WHERE bids.Amount > 100;