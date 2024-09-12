import snsql
from snsql import Privacy
import pandas as pd
csv_path = '../datasets/filename.csv'
meta_path = '../datasets/PUMS.yaml'

data = pd.read_csv(csv_path)
privacy = Privacy(epsilon=1.0, delta=0.01)

metadata = {
    '': {
        '': {
            'filename': {
                                    "row_privacy":
                                    {
                                        True
                                    },  
                                    "employee_id":
                                    {
                                        "type":"int",
                                        "lower": "1",
                                        "upper": "5"
                                    },
                                    "employee_name":
                                    {
                                        "type":"string",
                                    },
                                    "manager_id":
                                    {
                                        "type":"int",
                                        "lower":"1",
                                        "upper": "5",
                                    }

                    }
                }
    }
}
reader = snsql.from_connection(data, privacy=privacy, metadata=metadata)
result = reader.execute('SELECT COUNT(manager_id) FROM filename')
# result = reader.execute('SELECT COUNT(married) AS puss FROM PUMS.PUMS GROUP BY married ORDER BY puss DESC LIMIT 1')
print(result)