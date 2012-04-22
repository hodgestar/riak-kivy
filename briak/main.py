from riak import RiakClient, RiakObject

import kivy
kivy.require('1.2.0')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.logger import Logger


def create_test_data(client):
    r = RiakObject(client, client.bucket("test.bucket.1"))
    r.set_data({"foo": 1, "bar": "baz"})
    r.store()

    r = RiakObject(client, client.bucket("test.bucket.2"))
    r.set_data({"foo": 2, "bar": "baz"})
    r.store()


class MyApp(App):

    title = "Riak Browser"

    def build(self):
        layout = StackLayout(size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(Label(text="Riak Buckets"))

        self.client = RiakClient()
        buckets = self.client.get_buckets()
        if not buckets:
            layout.add_widget(Label(text="Can has bucket?"))
        for bucket in buckets:
            button = Button(text=str(bucket))
            button.bucket = bucket
            button.bind(on_press=self.bucket_clicked)
            layout.add_widget(button)

        view = ScrollView()
        view.add_widget(layout)
        return view

    def bucket_clicked(self, button):
        bucket = self.client.bucket(button.bucket)
        self.build_bucket_view(bucket)

    def build_bucket_view(self, bucket):
        layout = StackLayout(size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(Label(text="Bucket: %s" % bucket.get_name()))

        keys = bucket.get_keys()
        if not keys:
            layout.add_widget(Label(text="Can has key?"))
        for key in keys:
            button = Button(text=key)
            button.key = key
            button.bucket = bucket
            button.bind(on_press=self.key_clicked)
            layout.add_widget(button)

        self.root.clear_widgets()
        self.root.add_widget(layout)

    def key_clicked(self, button):
        key, bucket = button.key, button.bucket
        print "-- %s (%s) --" % (key, bucket.get_name())
        robj = bucket.get(key)
        print robj.get_data()


if __name__ == '__main__':
    MyApp().run()
