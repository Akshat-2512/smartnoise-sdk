import snsql
from snsql import Privacy
import pandas as pd
import psycopg2 as psql
csv_path = '../datasets/PUMS.csv'
meta_path = '../datasets/postgres.yaml'

conn = psql.connect(
    host= "database-1.c9uvotqn49ib.us-east-1.rds.amazonaws.com",
    port="5432",          
    user="postgres",      
    password="tDidpZwoozGw3Nnaiw1n" 
)

data = pd.read_csv(csv_path)
privacy = Privacy(epsilon=1.0, delta=0.01)

reader = snsql.from_connection(conn, privacy=privacy, metadata=meta_path)


#  result2 is re-written query for SELECT COUNT(*) FROM public.my_table2 AS t1 JOIN pulic.my_table3 AS t0 t1.num1 = t0.num1  
# result2 = reader.execute('SELECT COUNT(str1) FROM (SELECT num1 AS c1 FROM public.my_table2) AS t1 INNER JOIN (SELECT  num1 AS c2, str1 FROM public.my_table3) AS t0 ON c1 = c2')


# " SELECT COUNT(*) FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE orders.product_id = 1 AND customers.address LIKE '%United States%' "
# " SELECT COUNT(*) + 4309.348644872521 * (CASE WHEN RAND() - 0.5 < 0 THEN -1.0 ELSE 1.0 END * LN(1 - 2 * ABS(RAND() - 0.5))) 
#   FROM (SELECT customer_id, product_id FROM public.orders) t INNER JOIN (SELECT customer_id, address FROM public.customers) t0 ON t.customer_id = t0.customer_id WHERE t.product_id = 1 AND t0.address LIKE '%United States%' "





#  INNER JOIN
# SELECT Customers.CustomerName, Orders.OrderID, Orders.OrderDate FROM Customers INNER JOIN Orders ON Customers.CustomerID = Orders.CustomerID;
# result_IJ = reader.execute('SELECT SUM(c1) FROM (SELECT CustomerID as c2 FROM public.Customers) INNER JOIN (SELECT CustomerID as c1 FROM Orders) ON c1 = c2')
# print(result_IJ)


# LEFT JOIN 
# SELECT Customers.CustomerName, Orders.OrderID, Orders.OrderDate FROM Customers LEFT JOIN Orders ON Customers.CustomerID = Orders.CustomerID;
# result_LJ = reader.execute('SELECT SUM(c1) FROM (SELECT CustomerID as c2 FROM public.Customers) LEFT JOIN (SELECT CustomerID as c1 FROM Orders) ON c1 = c2')
# print(result_LJ)



# RIGHT JOIN
# SELECT Customers.CustomerName, Orders.OrderID, Orders.OrderDate FROM Customers RIGHT JOIN Orders ON Customers.CustomerID = Orders.CustomerID;
# result_RJ = reader.execute('SELECT SUM(c1) FROM (SELECT CustomerID as c2 FROM public.Customers) RIGHT JOIN (SELECT CustomerID as c1 FROM Orders) ON c1 = c2')
# print(result_RJ)


# FULL OUTER JOIN
# SELECT Customers.CustomerName, Orders.OrderID, Orders.OrderDate FROM Customers FULL OUTER JOIN Orders ON Customers.CustomerID = Orders.CustomerID;
# result_FOJ = reader.execute('SELECT SUM(c1) FROM (SELECT CustomerID as c2 FROM public.Customers) FULL OUTER JOIN (SELECT CustomerID as c1 FROM Orders) ON c1 = c2')
# print(result_FOJ)


# CROSS JOIN
# SELECT Customers.CustomerName, Products.ProductName FROM Customers CROSS JOIN Products;
# result_CJ = reader.execute('SELECT SUM(c1) FROM (SELECT CustomerID as c2 FROM public.Customers) CROSS JOIN (SELECT CustomerID as c1 FROM Orders)')
# print(result_CJ)


# SELF JOIN 
# SELECT A.CustomerName AS Customer1, B.CustomerName AS Customer2 FROM Customers A INNER JOIN Customers B ON A.City = B.City AND A.CustomerID = B.CustomerID;
result_SJ = reader.execute('SELECT COUNT(*) FROM (SELECT CustomerName AS Customer1 , City AS A_city FROM CUSTOMERS) AS A INNER JOIN (SELECT CustomerName AS Customer2, City AS B_city FROM CUSTOMERS) AS B ON A_city = B_city')
print(result_SJ)


