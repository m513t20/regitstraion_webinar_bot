import json




class storage:
    user_data=None
    save_path=None

    def __init__(self,user_pth):
        self.save_path=user_pth
        if self.save_path.exists():
            self._load_users()
        else:
            self.user_data={}

    

    def _load_users(self):
        with open(self.save_path) as source:
            self.user_data=json.load(source)
    
    def _save_users(self):
        with open(self.save_path,'w') as out:
            json.dump(self.user_data,out)

    def add(self,key,new_entry):
        self.user_data[key]=new_entry
        self._save_users()
        self._load_users()

    def delete(self,key):
        if not key in self.user_data.keys():
            return
        del self.user_data[key]
        self._save_users()



