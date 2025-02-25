SELECT COUNT(DISTINCT Item.UserID)
FROM Item
JOIN User ON Item.UserID = User.UserID
WHERE User.Rating > 1000;