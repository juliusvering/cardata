"""Test Script for Smartcar API

This script allows to test all requests specified in the README.htm file.
The tests check the status code returned by the request as well as the returned
information.
"""


import requests
import json
import unittest


class TestFlaskApiUsingRequests(unittest.TestCase):
    def test_vehicle_info_1(self):
        # Testing Vehicle 1234

        response = requests.get("http://127.0.0.1:5000/vehicles/:1234")
        self.assertEqual(response.status_code, 200)
        expectedResponse = {
            "vin": "123123412412",
            "color": "Metallic Silver",
            "doorCount": 4,
            "driveTrain": "v8"
        }
        self.assertEqual(response.json(), expectedResponse)

    def test_vehicle_info_2(self):
        # Testing Vehicle 1235

        response = requests.get("http://127.0.0.1:5000/vehicles/:1235")
        self.assertEqual(response.status_code, 200)
        expectedResponse = {
            "vin": "1235AZ91XP",
            "color": "Forest Green",
            "doorCount": 2,
            "driveTrain": "electric"
        }

        self.assertEqual(response.json(), expectedResponse)

    def test_vehicle_security_1(self):
        # Testing doors for Vehicle 1234

        response = requests.get("http://127.0.0.1:5000/vehicles/:1234/doors")
        self.assertEqual(response.status_code, 200)
        for door in response.json():
            self.assertEqual(type(door["location"]), str)
            self.assertEqual(type(door["locked"]), bool)

    def test_vehicle_security_2(self):
        # Testing doors for Vehicle 1235

        response = requests.get("http://127.0.0.1:5000/vehicles/:1235/doors")
        self.assertEqual(response.status_code, 200)
        for door in response.json():
            self.assertEqual(type(door["location"]), str)
            self.assertEqual(type(door["locked"]), bool)

    def test_vehicle_energy_1(self):
        # Testing energy for Vehicle 1234

        response = requests.get("http://127.0.0.1:5000/vehicles/:1234/fuel")
        response2 = requests.get("http://127.0.0.1:5000/vehicles/:1234/battery")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(type(response.json()), dict)
        self.assertEqual(type(response2.json()), dict)

    def test_vehicle_energy_2(self):
        # Testing energy for Vehicle 1235

        response = requests.get("http://127.0.0.1:5000/vehicles/:1234/fuel")
        response2 = requests.get("http://127.0.0.1:5000/vehicles/:1234/battery")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(type(response.json()), dict)
        self.assertEqual(type(response2.json()), dict)

    def test_vehicle_engine_1(self):
        # Testing engine for Vehicle 1234

        for action in ["START", "STOP"]:
            response = requests.post("http://127.0.0.1:5000/vehicles/:1234/engine",
                                     data={"action": action})
            self.assertEqual(response.status_code, 200)
            self.assertIn(response.json()["status"], ["success", "error"])

    def test_vehicle_engine_2(self):
        # Testing engine for Vehicle 1235
        for action in ["START", "STOP"]:
            response = requests.post("http://127.0.0.1:5000/vehicles/:1235/engine",
                                     data={"action": action})
            self.assertEqual(response.status_code, 200)
            self.assertIn(response.json()["status"], ["success", "error"])


if __name__ == '__main__':
    unittest.main()
