from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy_garden.xcamera.xcamera import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from googleapiclient.discovery import build
import requests
from PIL import Image as im
from io import BytesIO
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from android.permissions import request_permissions, Permission


# Window.size = (1080/3.5, 2408/3.5)
class SecondScreen(Screen):
    def __init__(self,obj_news,**kwargs):
        super().__init__(**kwargs)
        self.size=(Window.width,Window.height)
        # self.pos=(0,0)

        grid_layout = GridLayout(rows=2,size_hint_y=None)
        

        # create and add the labels to the GridLayout
        title_label = Label(text=obj_news['Title'], font_size=dp(18))
        content_label = Label(text=obj_news['Content'], font_size=dp(20),text_size=(self.size[0], None))
        grid_layout.add_widget(title_label)

    
        grid_layout.add_widget(content_label)

        # if(obj_news['Photos']!=""):
        #     try: 
        #         pil_image=obj_news['Photos']
        #         print(pil_image.size)
        #         # max_size = grid_layout.height
        #         # if pil_image.width > max_size or pil_image.height > max_size:
        #         #     pil_image.thumbnail((max_size*pil_image.height/pil_image.width, max_size))
        #         # pil_image.show()
        #         texture = Texture.create(size=pil_image.size)
        #         texture.blit_buffer(pil_image.tobytes(), colorfmt='rgba')

        #         # Create an Image widget and set its texture to the Kivy Texture
        #         image = Image(texture=texture)
        #         grid_layout.add_widget(image)
        #     except Exception as e:
        #         print(f"Error: {e}")

        
        # create a ScrollView and add the GridLayout to it
        scroll_view = ScrollView()
        scroll_view.add_widget(grid_layout)
        # position the title label at the top of the screen
        title_label.texture_update()
        label_size = content_label.texture_size
        _,title_label.height=label_size
        title_label.height+=dp(20)
        title_label.size_hint_y = None
        # title_label.pos = (0, Window.height)

        content_label.texture_update()
        label_size = content_label.texture_size
        _,content_label.height=label_size
        content_label.height+=dp(20)
        content_label.size_hint_y=None


        grid_layout.height = title_label.texture_size[1] + content_label.texture_size[1]

        # create a button to go back to the main screen
        button = Button(text="Go Back to Main Screen",pos_hint={'center_x': 0.5, 'center_y': 0.02},size_hint=(None,None ),height=dp(18),width=Window.width)
        button.bind(on_press=self.go_to_main_screen)

        # add the ScrollView and the button to the screen
        self.add_widget(scroll_view)
        self.add_widget(button)
    def go_to_main_screen(self, *args):
        app = App.get_running_app()
        app.screen_manager.current = "main"


class TouchLabel(Label):
    def __init__(self,offset,obj_news, **kwargs):
        super().__init__(**kwargs)
        self.obj_news=obj_news
        self.offset=offset
        self.size_hint = (1, None)
        self.height = dp(18)
        self.count=0
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if(self.count==0):
                self.second_screen=SecondScreen(name="second"+str(self.offset),obj_news=self.obj_news)
                self.count+=1
            else:
                self.second_screen=SecondScreen(obj_news=self.obj_news)
            app = App.get_running_app()
            app.screen_manager.add_widget(self.second_screen)
            app.screen_manager.current = "second"+str(self.offset)


class NewsItem(Screen,BoxLayout):
    def __init__(self, obj_news, **kwargs):
        super().__init__(**kwargs)
        offset=0.04
        for i in obj_news:
            self.a = TouchLabel(offset,i,text=i['Title'], font_size=dp(18), pos_hint={'center_x': 0.5, 'center_y': 0.99-offset})
            self.add_widget(self.a)
            offset+=0.04

        


class NewsList(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def get_news(self):
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("S:\\Projects\\Droid Dynasty\\newsfeedapk-bf11dac6e080.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("News").sheet1
        articles = sheet.get_all_records()
        # for i in range(len(articles)):
        #     if(articles[i]['Photos']!=""):
        #         image_link=articles[i]['Photos']
        #         file_id = image_link.split('/')[-2]
        #         service = build('drive', 'v3', credentials=creds)
        #         response = service.files().get_media(fileId=file_id).execute()
        #         image = im.open(BytesIO(response))
        #         if(image.height>500 or image.width>500):
        #             width, height = image.size
        #             new_size = (int(500*width/height), 500)
        #             image = image.resize(new_size)
        #         # output = BytesIO()
        #         # image.save(output, format='JPEG', quality=20)
        #         # output.seek(0)
        #         # image = output.getvalue()
        #         # image = im.open(BytesIO(image))
        #         # # image.show()
        #         articles[i]['Photos']=image
        # # print(articles)
        return(articles)
        


class NewsApp(App):
    def build(self):
        request_permissions([Permission.INTERNET,Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE])
        self.screen_manager = ScreenManager()
        obj=NewsList()
        obj_news=obj.get_news()
        self.main_screen=NewsItem(name="main",obj_news=obj_news)
        self.screen_manager.add_widget(self.main_screen)
        return self.screen_manager


if __name__ == "__main__":
    NewsApp().run()
