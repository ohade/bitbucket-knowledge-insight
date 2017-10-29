from refresher import Refresher
from elements.person import Person


class RefresherImpl(Refresher):
    # use this if you have component to ignore, for example: ignore_component = set(['.gitignore', '.java-version',
    # 'myfile.txt', '2', '3', '1', 'RELEASE_VERSION.issues.theirs', 'pom.xml'])
    ignore_component = {'.gitignore', '.java-version', 'myfile.txt', '2', '3', '1', 'RELEASE_VERSION.issues.theirs',
                        'pom.xml'}

    def __init__(self):
        super(RefresherImpl, self).__init__()

    # In this method you can identify chains that you would like to shorten in the tree end result
    # for example, lets say you have a list of folder like this:
    # src->main->java->com->a->b->c
    # you can make it a single line here so in the final tree you will have it as a single folder
    # you do this the following way:
    # result = ":".join(source)\
    # .replace("src:main:java:com:a:b:c", "src.main.java.com.a.b.c")\
    # .split(":")
    def manipulate_code_display(self, source):
        return ":".join(source) \
            .replace("src:main:java:com:taboola", "src.main.java.com.taboola") \
            .replace("src:main:resources", "src.main.resources") \
            .replace("src:main:proto", "src.main.proto") \
            .replace("src:test:java:com:taboola", "src.test.java.com.taboola") \
            .split(":")

    # In this method you can supply a file with the name and the photo of
    # the person and the AreaKnowledgeFactory.update_photo will get a
    # list of this persons and match them to the info it has from
    # the tickets, so an image will be attached to each contributer or pull requester reviewer
    #
    # place the photo under static people and it will be accesses later
    # for exmaple if you have a picture named smily_face.png
    # simply place it in static/people/ and write here smily_face.png
    def supply_persons_for_update_photo(self):
        persons = list()
        for name in self._persons_name:
            persons.append(Person(display_name=name, photo_id="smily_face.png"))
        return persons


if __name__ == "__main__":
    r = RefresherImpl()
