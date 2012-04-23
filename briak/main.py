from riak import RiakClient, RiakObject

import kivy
kivy.require('1.2.0')

from kivy.app import App
from kivy.uix.widget import Widget
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


class AppWidget(Widget):
    def __init__(self, client):
        super(AppWidget, self).__init__()
        self.client = client
        self.bucket_list = BucketList(self)
        self.key_list = KeyList(self)
        self.key_data = KeyData(self)
        self.switch_to_bucket_list()

    def switch_to_bucket_list(self):
        self.clear_widgets()
        self.add_widget(self.bucket_list)

    def switch_to_bucket(self, bucket):
        self.clear_widgets()
        self.key_list.set_bucket(bucket)
        self.add_widget(self.key_list)

    def switch_to_key(self, bucket, key):
        self.clear_widgets()
        self.key_data.set_key(bucket, key)
        self.add_widget(self.key_data)


class BucketList(StackLayout):
    def __init__(self, app):
        super(BucketList, self).__init__()
        self.bind(minimum_height=app.setter('height'))
        self.app = app

        title = Label(text="Riak Buckets")
        self.add_widget(title)

        refresh = Button(text="Refresh")
        refresh.bind(on_press=self.refresh)
        self.add_widget(refresh)

        scroll = ScrollView()
        self.add_widget(scroll)

        self.layout = StackLayout(size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll.add_widget(self.layout)

        self.refresh(None)

    def refresh(self, _refresh_btn):
        self.layout.clear_widgets()
        buckets = self.app.client.get_buckets()
        if not buckets:
            self.layout.add_widget(Label(text="Can has bucket?"))
        for bucket in buckets:
            button = Button(text=bucket)
            button.bucket = bucket
            button.bind(on_press=self.bucket_clicked)
            self.layout.add_widget(button)

    def bucket_clicked(self, button):
        bucket = self.app.client.bucket(button.bucket)
        self.app.switch_to_bucket(bucket)


class KeyList(StackLayout):
    def __init__(self, app):
        super(KeyList, self).__init__()
        self.bind(minimum_height=self.setter('height'))
        self.app = app
        self.bucket = None

        self.title = Label(text="No bucket yet")
        self.add_widget(self.title)

        back_button = Button(text="Back ...")
        back_button.bind(on_press=self.back)
        self.add_widget(back_button)

        refresh = Button(text="Refresh")
        refresh.bind(on_press=self.refresh)
        self.add_widget(refresh)

        scroll = ScrollView()
        self.add_widget(scroll)

        self.layout = StackLayout(size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll.add_widget(self.layout)

    def back(self, _back_btn):
        self.app.switch_to_bucket_list()

    def refresh(self, _refresh_btn):
        self.set_bucket(self.bucket, force_refresh=True)

    def set_bucket(self, bucket, force_refresh=False):
        if bucket is None:
            return
        if bucket == self.bucket and not force_refresh:
            return
        self.bucket = bucket
        self.title.text = "Bucket: %s" % bucket.get_name()
        self.layout.clear_widgets()

        keys = bucket.get_keys()
        if not keys:
            self.layout.add_widget(Label(text="Can has key?"))
        for key in keys:
            button = Button(text=key)
            button.key = key
            button.bucket = bucket
            button.bind(on_press=self.key_clicked)
            self.layout.add_widget(button)

    def key_clicked(self, button):
        self.app.switch_to_key(button.bucket, button.key)


class KeyData(StackLayout):
    def __init__(self, app):
        super(KeyData, self).__init__()
        self.bind(minimum_height=self.setter('height'))
        self.app = app
        self.bucket, self.key = None, None

        self.title = Label(text="No key yet")
        self.add_widget(self.title)

        back_button = Button(text="Back ...")
        back_button.bind(on_press=self.back)
        self.add_widget(back_button)

        refresh = Button(text="Refresh")
        refresh.bind(on_press=self.refresh)
        self.add_widget(refresh)

        scroll = ScrollView()
        self.add_widget(scroll)

        self.layout = StackLayout(size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll.add_widget(self.layout)

    def back(self, _back_btn):
        self.app.switch_to_bucket(self.bucket)

    def refresh(self, _refresh_button):
        self.set_key(self.bucket, self.key, force_refresh=True)

    def set_key(self, bucket, key, force_refresh=False):
        if bucket is None or key is None:
            return
        if (bucket == self.bucket and key == self.key) and not force_refresh:
            return
        self.bucket, self.key = bucket, key

        self.title.text = "Key: %s (%s)" % (key, bucket.get_name())
        self.layout.clear_widgets()

        robj = bucket.get(key)
        data = robj.get_data()

        if not data:
            self.layout.add_widget(Label(text="Can has data?"))
        for key, value in data.items():
            label = Label(text="%s: %s" % (key, value))
            self.layout.add_widget(label)


class MyApp(App):

    title = "Riak Browser"

    def build(self):
        client = RiakClient()
        return AppWidget(client)


if __name__ == '__main__':
    MyApp().run()
