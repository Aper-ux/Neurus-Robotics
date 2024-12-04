import pyrebase

class BDD:
    def __init__(self):
        self._firebaseConfig = {
            "apiKey" : "AIzaSyDZU-roqQjopM7rZ2kTPYPkW2fMUphfAtk",
            "authDomain" : "neurus-cd926.firebaseapp.com",
            "databaseURL" : "https://neurus-cd926-default-rtdb.firebaseio.com",
            "projectId" : "neurus-cd926",
            "storageBucket" : "neurus-cd926.appspot.com",
            "messagingSenderId" : "396219141794",
            "appId" : "1:396219141794:web:499e0e3d8bf6abcf2f51fb",
            "measurementId" : "G-2X63HB8203",

            "storageBucket": "neurus-cd926.firebasestorage.app"
        }

        self._firebase = pyrebase.initialize_app(self._firebaseConfig)
    
    def get_firebase(self):
        return self._firebase

    def db(self):
        db = self.get_firebase().database()

        return db