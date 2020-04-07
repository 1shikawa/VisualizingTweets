CREATE DATABASE IF NOT EXISTS visualizingTweets CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER IF NOT EXISTS 'visualizingTweets' IDENTIFIED BY 'visualizingTweets';
GRANT ALL ON *.* TO visualizingTweets@'%' IDENTIFIED BY 'visualizingTweets' WITH GRANT OPTION;

FLUSH PRIVILEGES;