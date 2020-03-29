CREATE DATABASE IF NOT EXISTS finchart CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER IF NOT EXISTS 'finchart' IDENTIFIED BY 'finchart';
GRANT ALL ON *.* TO finchart@'%' IDENTIFIED BY 'finchart' WITH GRANT OPTION;

FLUSH PRIVILEGES;