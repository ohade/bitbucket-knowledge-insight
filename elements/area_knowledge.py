class AreaKnowledge:
    def __init__(self, text=None):
        self.text = text
        self._peoples_names = set()
        self.peoples_info = list()

    def set_text(self, text):
        self.text = text

    def update_people_photos(self, persons):
        for person in persons:
            self.update_people_photo(person.display_name, person.photo_id)

    def update_people_photo(self, name, photo_id):
        if name not in self._peoples_names:
            return

        for p in self.peoples_info:
            if name == p['name']:
                p['photo_id'] = photo_id
                return

    def add_people_names(self, names):
        for name in names:
            self.add_people(name, None)

    def add_people(self, name, photo_id):
        if name in self._peoples_names:
            return
        else:
            self._peoples_names.add(name)
        self.peoples_info.append(dict(name=name, photo_id=photo_id))

    def get_mapping(self):
        return dict(
            area=self.text,
            peoples=self.peoples_info
        )
