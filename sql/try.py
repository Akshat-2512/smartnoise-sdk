import snsql
from snsql import Privacy
import pandas as pd
import math
import random
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
def laplace_noise(scale=1.0):
    # Generate a uniform random variable between -0.5 and 0.5
    u = random.random() - 0.5
    
    # Determine the sign based on the value of u
    sign = -1.0 if u < 0 else 1.0
    
    # Compute the Laplace noise using the transformation
    noise = sign * math.log(1 - 2 * abs(u))
    
    # Apply the scale factor to the noise
    return scale * noise

result_IJ = reader.execute('SELECT COUNT(*) AS s FROM (SELECT CustomerID as c2  FROM public.Customers) INNER JOIN (SELECT CustomerID as c1 , orderid as ord FROM Orders) ON c1 = c2')
print(float(result_IJ[1][0]) + laplace_noise(scale= 10.45476570491571 )) 
k=0
s_prev=0
s=0
beta = 0
while (s >= s_prev and k < 5):
    mfxr1 = 1 + k # customers max atr for customerID
    s1= 1
    mfxr2 = 2 + k # orders max atr for customerID
    s2 = 1

    sk= 2 + k
    epsilon = 1 
    delta = 0.000001
    beta = epsilon/(2*math.log(2/delta))
    s_prev = s  
    s = math.exp(-beta*k)*sk
    k= k+1

# add laplace noise of 
# noise = 2*s/ epsilon
noise  = 2*s
# 45.720677334346
print(noise)



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
# result_SJ = reader.execute('SELECT COUNT(*) FROM (SELECT CustomerName AS Customer1 , City AS A_city FROM CUSTOMERS) AS A INNER JOIN (SELECT CustomerName AS Customer2, City AS B_city FROM CUSTOMERS) AS B ON A_city = B_city')
# print(result_SJ)


