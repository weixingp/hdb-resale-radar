# TODO Implement 2 public functions as stated below
# 1) Implement ppm.predict()
# 2) Implement ppm.update()
# TODO implement the following private functions
# 1) Save, save the model using pickle

from django.core.management.base import BaseCommand
from main.models import Room
import pandas as pd
import joblib
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier


class PricePredictionModel:

    def __init__(self):

        try:
            print("Loading from saved model...")
            self.__random_forest = joblib.load("Random_Forest.sav")
            self.__le = joblib.load("Trained_Label_Encoder.joblib")
            self.__oe = joblib.load("Trained_Ordinal_Encoder.joblib")
        except OSError as e:
            print("Model not found, implementing model...")

            # Retrieval of data is less than 1 second
            # Querying and obtaining data from database is very fast
            self.__all_data = Room.objects.all()

            # Dataframe containing data exported from database
            self.__HDBPrices = pd.DataFrame(self.__copy_data_from_db())

            self.__x_data = ['area', 'town', 'flat_type_id', 'level_type_id', 'remaining_lease']

            # Modification of data to allow label encoding to happen
            # Time taken for modification is less than 1 second in total
            self.__modify_x_data()
            self.__modify_y_data()
            self.__get_labels()
            self.__random_forest = self.__implement_machine_model()

    # Declaring a private method to load data from database, not accessible from external classes.
    def __copy_data_from_db(self):

        area = []
        town = []
        flat_type_id = []
        level_type_id = []
        remaining_lease = []
        resale_prices = []

        # To store each data in an array; to convert from database to variable
        for room_data in self.__all_data:
            town.append(room_data.block_address.town_name_id)
            area.append(room_data.area)
            flat_type_id.append(room_data.flat_type_id)
            level_type_id.append(room_data.level_type_id)
            remaining_lease.append(room_data.remaining_lease)
            resale_prices.append(room_data.resale_prices)

        data_dict = {'area': area,
                     'town': town,
                     'flat_type_id': flat_type_id,
                     'level_type_id': level_type_id,
                     'remaining_lease': remaining_lease,
                     'resale_prices': resale_prices
                     }

        # returns a dictionary with all the data stored, to be converted to dataframe in init function.
        return data_dict

    # Declaring a private method to modify independent data for machine learning, not accessible from external classes.
    def __modify_x_data(self):

        # Remaining lease has to be modified because the number of months trailing behind the number of years
        # increases the number of categories available for prediction.
        modified_remaining_lease = []
        for i in range(len(self.__HDBPrices['remaining_lease'])):
            remaining_lease = self.__HDBPrices['remaining_lease'][i]
            if 'month' in remaining_lease:
                end = remaining_lease.index('month') - 1
                start = end - 2
                if int(remaining_lease[start:end]) >= 6:
                    years_remaining = int(remaining_lease[0:2]) + 1
                else:
                    years_remaining = int(remaining_lease[0:2])
            else:
                years_remaining = int(remaining_lease[0:2])
            modified_remaining_lease.append(f'{years_remaining} Years')

        new_column = {'remaining_lease': modified_remaining_lease}
        modified_remaining_lease = pd.DataFrame(new_column)
        modified_remaining_lease.astype('category')
        self.__HDBPrices['remaining_lease'] = modified_remaining_lease

        # columnsToBeUsed = 'area', 'flat_type_id', 'level_type_id', 'remaining_lease'
        self.__HDBPrices['area'] = self.__HDBPrices['area'].astype('category')
        self.__HDBPrices['flat_type_id'] = self.__HDBPrices['flat_type_id'].astype('category')
        self.__HDBPrices['level_type_id'] = self.__HDBPrices['level_type_id'].astype('category')
        self.__HDBPrices['remaining_lease'] = self.__HDBPrices['remaining_lease'].astype('category')

    # Declaring a private method to modify dependent data for machine learning, not accessible from external classes.
    def __modify_y_data(self):

        my_dict = {}
        modified_resale_price = []
        for i in self.__HDBPrices['resale_prices']:
            if i <= 200_000:
                my_dict['100,000 TO 200,000'] = my_dict.get('100,000 TO 200,000', 0) + 1
                modified_resale_price.append('100,000 TO 200,000')
            elif i <= 300_000:
                my_dict['200,001 TO 300,000'] = my_dict.get('200,001 TO 300,000', 0) + 1
                modified_resale_price.append('200,001 TO 300,000')
            elif i <= 400_000:
                my_dict['300,001 TO 400,000'] = my_dict.get('300,001 TO 400,000', 0) + 1
                modified_resale_price.append('300,001 TO 400,000')
            elif i <= 500_000:
                my_dict['400,001 TO 500,000'] = my_dict.get('400,001 TO 500,000', 0) + 1
                modified_resale_price.append('400,001 TO 500,000')
            elif i <= 600_000:
                my_dict['500,001 TO 600,000'] = my_dict.get('500,001 TO 600,000', 0) + 1
                modified_resale_price.append('500,001 TO 600,000')
            elif i <= 700_000:
                my_dict['600,001 TO 700,000'] = my_dict.get('600,001 TO 700,000', 0) + 1
                modified_resale_price.append('600,001 TO 700,000')
            elif i <= 800_000:
                my_dict['700,001 TO 800,000'] = my_dict.get('700,001 TO 800,000', 0) + 1
                modified_resale_price.append('700,001 TO 800,000')
            elif i <= 900_000:
                my_dict['800,001 TO 900,000'] = my_dict.get('800,001 TO 900,000', 0) + 1
                modified_resale_price.append('800,001 TO 900,000')
            else:
                my_dict['900,000 OR MORE'] = my_dict.get('900,000 OR MORE', 0) + 1
                modified_resale_price.append('900,000 OR MORE')

        new_column = {'resale_prices': modified_resale_price}
        modified_resale_price = pd.DataFrame(new_column)
        self.__HDBPrices['resale_prices'] = modified_resale_price
        self.__HDBPrices['resale_prices'] = self.__HDBPrices['resale_prices'].astype('category')

    # Declaring a private method to reduce duplicated codes
    def __get_labels(self):

        x = pd.DataFrame(self.__HDBPrices[self.__x_data])
        y = self.__HDBPrices['resale_prices']

        # Encode all independent categorical data for prediction
        oe = OrdinalEncoder()
        oe.fit(x)

        # Encode all dependents categorical data for prediction
        le = LabelEncoder()
        le.fit(y)

        joblib.dump(le, "Trained_Label_Encoder.joblib")
        joblib.dump(oe, "Trained_Ordinal_Encoder.joblib")

        self.__le = le
        self.__oe = oe

    # Declaring a private method to instantiate the machine learning model
    def __implement_machine_model(self):

        x = pd.DataFrame(self.__HDBPrices[self.__x_data])
        y = self.__HDBPrices['resale_prices']

        x_encoded = self.__oe.transform(x)
        y_encoded = self.__le.transform(y)

        random_forest = RandomForestClassifier(n_estimators=700, criterion='entropy', random_state=0)
        random_forest.fit(x_encoded, y_encoded)

        pickle.dump(random_forest, open("Random_Forest.sav", 'wb'))

        return random_forest

    # Declaring a public method to obtain user inputs which is a 2D array containing information of HDB flats which
    # they want to have a prediction done for them.
    # inputs = [[100, 7, 3, 3, '80 Years']]
    def prediction_for_user_input(self, inputs):

        inputs_encoded = self.__oe.transform(inputs)

        random_forest_result = self.__random_forest.predict(inputs_encoded)
        result_random_forest = list(self.__le.inverse_transform(random_forest_result)).pop()

        return result_random_forest

    def update_prediction_model(self):
        self.__all_data = Room.objects.all()
        self.__HDBPrices = pd.DataFrame(self.__copy_data_from_db())
        self.__x_data = ['area', 'town', 'flat_type_id', 'level_type_id', 'remaining_lease']
        self.__modify_x_data()
        self.__modify_y_data()
        self.__get_labels()
        self.__random_forest = self.__implement_machine_model()

