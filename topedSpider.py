import scrapy
import os
from time import sleep
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import logging
import requests

basedir = os.path.dirname(os.path.realpath('__file__'))

class TopedScrapy(scrapy.Spider):
   name="topedscrap"
   parse_count = 0
   batas_item = 500
   arr_items = []
   arr_category=[
      "Bass Elektrik",
      "Gunting Dapur",
      "Kocokan Telur",
      "Kompor",
      "Mouse",
      "Pet Glove",
      "Pisau Dapur",
      "Pompa Galon"
   ]
   urls = [
      "https://www.tokopedia.com/p/film-musik/gitar-bass/bass-elektrik",
      "https://www.tokopedia.com/p/dapur/aksesoris-dapur/gunting-dapur",
      "https://www.tokopedia.com/p/dapur/peralatan-baking/kocokan-telur",
      "https://www.tokopedia.com/p/dapur/peralatan-masak/kompor",
      "https://www.tokopedia.com/p/komputer-laptop/aksesoris-komputer-laptop/mouse",
      "https://www.tokopedia.com/p/perawatan-hewan/grooming-hewan/""pet-glove",
      "https://www.tokopedia.com/p/dapur/aksesoris-dapur/pisau-dapur",
      "https://www.tokopedia.com/p/dapur/peralatan-dapur/pompa-galon"
   ]
   whitelist_word = [
      "Bass,Elektrik,Electric,Listrik,Squier,Ibanez,Marina,Yamaha,Epiphone,Cort,Fender",
      "Gunting,Scissors",
      "Kocok,Pengocok,Whisk,Baloon",
      "Kompor",
      "Mouse",
      "Glove,Sarung",
      "Pisau,Knife",
      "Pompa"
      ]
   blacklist_word = [
      "Pc,Amp,Pick,Pic,Pik,Senar,Case,Tas,Fret,Kabel,Capo,Sifon,Tripod,Holder,Handle,Cover,Knob,Neck,Nut,Rod,Akustik,Acoustic,DVD,Switch,Guard,String",
      "Besi,Serbaguna,Lapis,Botol,Lipat,Mini",
      "Portable,Mangkok,Mixer,Frother",
      "Tabung,Tatakan,Tangkringan,Pelindung,Catridge,Kaleng,Selang,Sumbu,Filter,Burner",
      "Switch,Tatakan,Pouch",
      "Sikat,Roller,Tas,Kantong",
      "Cleaver,Set,Wadah,Tempat,Holder,Golok,Alat",
      "Bottle,Manual"
   ]
   # Init chrome settings
   chrome_options = Options()
   chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
   chrome_options.add_argument("--window-size=1920x1080")

   def start_requests(self):
      print("START URL: "+self.urls[self.parse_count])
      print("START req: "+self.arr_category[self.parse_count])
      yield scrapy.Request(url=self.urls[self.parse_count], callback=self.parse, meta={"index":self.parse_count}, dont_filter=True)

   def parse(self, response):
      # Init Chrome driver
      driver = webdriver.Chrome(ChromeDriverManager().install())
      # Setiap mulai parse dari url set beberapa variabel
      SCROLL_PAUSE_TIME = 1
      counter = 0
      
      # Minta selenium untuk buka URL yang dikasi
      driver.get(response.url)
      driver.implicitly_wait(10)
      sleep(2)
      # Selama yang discrap pada kategori ini belum >150 
      while(counter<=self.batas_item):
         logging.log(logging.INFO, "Jumlah parsed: "+str(response.meta['index']))
         # Pastikan mulai dari atas
         # Biarin nge-load
         sleep(SCROLL_PAUSE_TIME)
         body = driver.find_element_by_css_selector('body')
         body.send_keys(Keys.HOME)
         sleep(SCROLL_PAUSE_TIME)
         # Pastikan ngeload dulu
         #scroll
         i=0
         while i<9:
            # Scroll down to bottom
            body = driver.find_element_by_css_selector('body')
            body.send_keys(Keys.PAGE_DOWN)
            # Wait to load page
            sleep(SCROLL_PAUSE_TIME)
            i=i+1
            
         # Selenium to scrappy
         scrapy_selector = Selector(text = driver.page_source)

         try: 
            logging.log(logging.INFO, "PARSE ITEM urutan: "+self.arr_category[response.meta['index']])
            logging.log(logging.INFO, "total: "+str(response.meta['index']))
            logging.log(logging.INFO, "counter: "+str(counter))
            logging.log(logging.INFO, "YES: "+self.whitelist_word[response.meta['index']])
            logging.log(logging.INFO, "NO: "+self.blacklist_word[response.meta['index']])

            # get items
            items=scrapy_selector.xpath("//div[@class='css-bk6tzz e1nlzfl3']")
            for item in items:
               try:
                  is_white = False
                  is_black = False
               
                  item_image = item.xpath(".//div[@class='css-jo3xxj']/img/@src").get()
                  # <span class="css-1bjwylw" > Taffware HUMI Kipas Cooler Mini Arctic Air Conditioner 8W - AA-MC4 </ span > 
                  # <span class="css-1bjwylw">REMOTE AC MULTI /UNIVERSAL JUN DA K-1028E</span>
                  item_title = item.xpath(".//div[@class='css-11s9vse']/span[@class='css-1bjwylw']").get()
                  item_title = item_title.split(">")[1].split("<")[0]
                  arr_title = item_title.split(" ")                  
                  # logging.log(logging.INFO, "item sekarang: "+item_title)

                  # Check 
                  for word in arr_title:
                     # cek di whitelist
                     split_white =self.whitelist_word[response.meta['index']].split(",") 
                     split_black =self.blacklist_word[response.meta['index']].split(",") 
                     for white in split_white:
                        # Kalau ada
                        if (white.lower() in word.lower()):
                           # Flag tidak ambil dan break ke item selanjutnya
                           is_white = True
                           # logging.log(logging.INFO, "whitelist cocok")
                     for black in split_black:
                        if(black.lower() in word.lower()):
                           is_black = True
                           # logging.log(logging.INFO, "ada blacklist")
                           break
                  # Ambil item, ketika masuk white dan tidak masuk black
                  if(is_white == True and is_black == False):
                     # Item yang benar bertambah
                     counter = counter + 1
                     # return sebagai barang bener
                     self.arr_items.append({
                        "item_title": item_title,
                        "file_urls":item_image,
                        "item_category":self.arr_category[response.meta['index']]
                        })
                     # Download gambar karena Scrapy Pipeline tidak dukung / kurang jelas dynamic save locationnya
                     filename = item_image.split('/')[-1]
                     filename = filename.split(".")[0]
                     filename = filename+".jpg"
                     save_dir = "D:/STTS/S8/Tugas Akhir/Dataset/Tokopedia"
                     save_dir = save_dir+"/"+self.arr_category[response.meta['index']]
                     # Save image to dir
                     # Buat dir jika ngga ada
                     if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                     r = requests.get(item_image, allow_redirects=True)
                     # save image
                     open(save_dir+"/"+filename, 'wb').write(r.content)

                     # log to txt
                     isi = item_title+"; "+item_image+"\n"
                     appendToTxt(save_dir+"/"+"log.txt",isi)                     
                     appendToTxt("hasilF.txt", isi)

                     logging.log(logging.INFO, "total item "+str(len(self.arr_items)))
                     logging.log(logging.INFO, "terima:  "+item_title)
                     # logging.log(logging.INFO, item.title)
                     yield {
                        "item_title": item_title,
                        "file_urls":item_image,
                        "item_category":self.arr_category[response.meta['index']]
                     }
                  # else: 
                     # logging.log(logging.INFO, "tolak: "+item_title)
               except Exception as e:
                  logging.log(logging.INFO, "Error karena "+str(e))
            # Next page
            if(counter<=self.batas_item):
               # //button[@class='css-1gpfbae-unf-pagination-item e19tp72t3']
               # 805, 16
               driver.execute_script("window.scrollTo(805,16)") 
               
               body = driver.find_element_by_css_selector('body')
               button = body.find_element_by_class_name("css-psnnxv-unf-pagination-item")
               # webdriver.ActionChains(driver).move_to_element(button)
               button.click()
               sleep(2)
               body = driver.find_element_by_css_selector('body')
               body.send_keys(Keys.HOME)
               body.send_keys(Keys.HOME)
               sleep(2)
               body.send_keys(Keys.HOME)
            else: 
               logging.log(logging.INFO, "Done iterate")
         except Exception as e:
            logging.log(logging.INFO, "Gagal fetch item, "+str(e))
      driver.quit() 

   def closed(self, reason):
      # Write to text   
      # Empty txt
      f = open("hasil.txt", "w")
      f.write("")
      f.close()
      # inserts from array
      for item in self.arr_items:
         isi = item['item_title']+"; "+item['file_urls']+"\n"
         appendToTxt("hasil.txt",isi)
      
def appendToTxt(fileLoc, text):
   f = open(fileLoc, "a")
   f.write(text)
   f.close()