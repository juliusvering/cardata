"""Smartcar API

This script runs the Smartcar API according to the Spec detailed in README.html

Its requirements are specified in the requirements.txt file.

All requests can be made as detailed in the API Spec found in the README
file using the Python requests library.
"""

from flask import Flask
from flask_restful import reqparse, Api, Resource
import requests
import json

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('action')


headers = {'content-type': 'application/json'}
payload = {'id': "placeholder", 'responseType': 'JSON'}


def make_post_request(service_str, payload):
    """Return the gmapi's response to the post request in JSON format."""
    return requests.post(
        "http://gmapi.azurewebsites.net/"+service_str, data=json.dumps(payload), headers=headers).json()


# The following classes handle all the requests.

class VehicleInfo(Resource):
    """This class handles the requests to general vehicle information.

    The class inherits from the Resource class from the flask_restful module.
    In the Flask-RESTful context, it represents a resource.

    Methods
    -------
    get(vehicle_id)
        Handles the GET request connected to the VehicleInfo class.
    """

    def get(self, vehicle_id):
        """Handle the GET request to the VehicleInfo resource.

        If any Exception is raised during the request, return the Exception
        instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        """

        payload['id'] = vehicle_id
        try:
            results = make_post_request("getVehicleInfoService", payload)['data']
            if results['fourDoorSedan']['value'] == 'True':
                doorCount = 4
            else:
                doorCount = 2

            new_response = {'vin': results['vin']['value'],
                            'color': results['color']['value'],
                            'doorCount': doorCount,
                            'driveTrain': results['driveTrain']['value']}

            return new_response
        except Exception as e:
            return {'Error': str(e)}


class VehicleDoors(Resource):
    """This class handles the requests to vehicle's door information.

    The class inherits from the Resource class from the flask_restful module.
    In the Flask-RESTful context, it represents a resource.

    Methods
    -------
    get(vehicle_id)
        Handles the GET request connected to the VehicleDoors class.
    """

    def get(self, vehicle_id):
        """Handle the GET request to the VehicleDoors resource.

        If any Exception is raised during the request, return the Exception
        instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        """

        payload['id'] = vehicle_id
        try:
            results = make_post_request("getSecurityStatusService", payload)['data']
            new_response = []
            # for every door, check what the status is and add it to the JSON string
            for door in results["doors"]["values"]:
                if door["locked"]["value"] == "True":
                    new_response.append(
                        {"location": door["location"]["value"], "locked": bool(1)})
                else:
                    new_response.append(
                        {"location": door["location"]["value"], "locked": bool(0)})
            return new_response
        except Exception as e:
            return {'Error': str(e)}


class VehicleEnergy(Resource):
    """This class handles the requests to vehicle's energy information.

    The class inherits from the Resource class from the flask_restful module.
    In the Flask-RESTful context, it represents a resource. It also represents
    the base class for the VehicleFuel and the VehicleBattery class, which
    make the same request on the GM API.

    Methods
    -------
    getEnergy(vehicle_id, energy_type)
        Handles the GET request connected to the VehicleEnergy class.
    """

    def getEnergy(self, vehicle_id, energy_type):
        """Handle the GET request to the VehicleEnergy resource.

        If any Exception is raised during the request, return the Exception
        instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        energy_type: str
            Either battery or gas, depending on what class makes the request
        """

        results = make_post_request("getEnergyService", payload)['data']
        energy_level = results["tankLevel"]["value"]
        if energy_type == "battery":
            energy_level = results["batteryLevel"]["value"]
        if energy_level == "null":
            # Return an error message if the wrong energy_type for the vehicle
            # was requested
            return {'Error': "This vehicle runs on "+energy_type}
        else:
            new_response = {"percentage": energy_level}
            return new_response


class VehicleFuel(VehicleEnergy):
    """This class handles the requests to vehicle's fuel information.

    The class inherits from the VehicleEnergy class.

    Methods
    -------
    get(vehicle_id)
        Handles the GET request connected to the VehicleFuel class.
    """

    def get(self, vehicle_id):
        """Handle the GET request to the VehicleFuel resource.

        Call the getEnergy method of the VehicleEnergy class to handle the actual
        request to the GM API.If any Exception is raised during the request,
        return the Exception instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        """

        payload['id'] = vehicle_id
        try:
            return self.getEnergy(vehicle_id, "gas")
        except Exception as e:
            return {'Error': str(e)}


class VehicleBattery(VehicleEnergy):
    """This class handles the requests to vehicle's battery information.

    The class inherits from the VehicleEnergy class.

    Methods
    -------
    get(vehicle_id)
        Handles the GET request connected to the VehicleBattery class.
    """

    def get(self, vehicle_id):
        """Handle the GET request to the VehicleBattery resource.

        Call the getEnergy method of the VehicleEnergy class to handle the actual
        request to the GM API.If any Exception is raised during the request,
        return the Exception instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        """

        payload['id'] = vehicle_id
        try:
            return self.getEnergy(vehicle_id, "battery")
        except Exception as e:
            return {'Error': str(e)}


class VehicleEngine(Resource):
    """This class handles the requests connected to the vehicle's engine.

    The class inherits from the Resource class from the flask_restful module.
    In the Flask-RESTful context, it represents a resource.

    Methods
    -------
    post(vehicle_id)
        Handles the POST request connected to the VehicleEngine class.
    """

    def post(self, vehicle_id):
        """Handle the POST request to the VehicleEngine resource.

        If any Exception is raised during the request, return the Exception
        instead.

        Parameters
        ----------
        vehicle_id: str
            The ID of the vehicle
        """

        payload['id'] = vehicle_id
        # the payload is different for this request and includes an "action" key
        payload_engine = dict(payload)
        args = parser.parse_args()  # get the argument from the post request
        if args['action'] == "START" or args['action'] == "STOP":
            payload_engine["command"] = args['action']+"_VEHICLE"
        else:
            # Return an error message if the action passed in with the payload
            # is invalid
            return {"Error": "This action is not supported."}

        try:
            result = make_post_request("actionEngineService", payload_engine)[
                'actionResult']["status"]
            if result == "EXECUTED":
                new_response = {"status": "success"}
            else:
                new_response = {"status": "error"}
            return new_response
        except Exception as e:
            return {'Error': str(e)}


# Handle the routing from the Flask-RESTful module by adding
# the resources to the API

api.add_resource(VehicleInfo, '/vehicles/:<vehicle_id>')
api.add_resource(VehicleDoors, '/vehicles/:<vehicle_id>/doors')
api.add_resource(VehicleFuel, '/vehicles/:<vehicle_id>/fuel')
api.add_resource(VehicleBattery, '/vehicles/:<vehicle_id>/battery')
api.add_resource(VehicleEngine, '/vehicles/:<vehicle_id>/engine')

if __name__ == '__main__':
    app.run(threaded=True)
