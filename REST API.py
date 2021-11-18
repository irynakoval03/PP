#from datetime import date
#from pprint import pprint
#from marshmallow import Schema,

class Users(Resources):
    def get(self):
        data = pd.read_csv('users.csv')  # read CSV
        data = data.to_dict()  # convert dataframe to dictionary
        return {'data': data}, 200  # return data and 200 OK code

api.add_resource(Users, '/users')  # '/users' is our entry point

