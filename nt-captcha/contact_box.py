from bs4 import BeautifulSoup
import requests
import re
import csv
import webbrowser
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
import os



"""
  Program to fill contact boxes for nametailor domain selling. This is achieved through a combination
  of selenium and beautiful soup.
"""


EMAIL = "smartin@nametailor.com"
FIRST_NAME = "Scott "
LAST_NAME = "Martin"
PHONE = "2036931112"

testing = False

tested = 0
completed = 0

def clear_input(input):
  try:
    input.clear()
  except:
    pass


def href_contact(domain):
  if "http://" not in domain:
    domain = "http://" + domain
  try:
    page = requests.get(domain)
  except Exception:
    return ""
  href_values = re.findall(r'href=\"([^\"]*(?i)contact[^\"]*)', page.text)
  if len(href_values) > 0:
    return href_values[0] 
  else:
    return "" 


def clean_link(link, domain):
  if link[0] == "/" and domain not in link:
    link = domain + link
  elif domain not in link:
    link = domain + "/" + link
  if "http://" not in link:
    link = "http://" + link
  return link


def fill_form(forms, contact_page):

  name_filled = False
  email_filled = False
  message_filled = False
  phone_filled = False

  email = """Hello,

  I am contacting you because I thought you might be interested in knowing that we are selling our domain {} ; the search term " {} " receives an average of  {} exact-match searches per month (roughly {} per day) on Google alone and owning this domain would be an asset to your marketing efforts.

  85% of people search online for local services.
  94% of those people don't go beyond the first search page.

  If you are interested or have any questions about the domain please don't hesitate to ask.""".format(domain_name,
                                                                                                       keywords,
                                                                                                       searches,
                                                                                                       searches_per_day)
  form = None
  for a_form in forms:
    try:
      message_box = a_form.find_element_by_tag_name('textarea')
      form = a_form 
      break
    except:
      pass
  
  if message_box:
    message_box.send_keys(email)
    message_filled = True
  inputs = [input for input in form.find_elements_by_tag_name('input') if input.get_attribute('type') != "hidden"]
  labels = form.find_elements_by_tag_name('label')
  selects = [input for input in form.find_elements_by_tag_name('select')]
  for select in selects:
    options = [x for x in select.find_elements_by_tag_name("option")]
    options[-1].click()



  num_inputs = len(inputs)
  num_labels = len(labels)
  for index, label in enumerate(labels):
    
    label_text = label.text.lower()
    try:
      next_input = label.find_element_by_xpath("//input[@id='{}'][1]".format(label.get_attribute('for')))
    except:
      try:
        next_input = label.find_element_by_xpath("//input[@name='{}'][1]".format(label.get_attribute('for'))) 
      except:
        break
    
    if "mail" in label_text:
      clear_input(next_input)
      next_input.send_keys(EMAIL)
      email_filled = True
    elif "first" in label_text:
      clear_input(next_input)
      next_input.send_keys(FIRST_NAME)
    elif "last" in label_text and not name_filled:
      clear_input(next_input)
      next_input.send_keys(LAST_NAME)
      name_filled = True
    elif "name" in label_text and not name_filled:
      clear_input(next_input)
      next_input.send_keys(FIRST_NAME + LAST_NAME)
      name_filled = True
    elif "phone" in label_text:
      clear_input(next_input)
      next_input.send_keys(PHONE)
      phone_filled = True
    elif "subject" in label_text:
      clear_input(next_input)
      next_input.send_keys("Domain")

  
  attributes = ['placeholder', 'innerHTML', 'value']
  for attribute in attributes:
    for input_box in inputs:
      attribute_text = input_box.get_attribute(attribute)
      if not attribute_text:
        continue
      attribute_text = attribute_text.lower()

      if "mail" in attribute_text and not email_filled:
        clear_input(input_box)
        input_box.send_keys(EMAIL)
        email_filled = True
      elif "first" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(FIRST_NAME)
      elif "last" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(LAST_NAME)
        name_filled = True
      elif "name" in attribute_text and not name_filled:
        clear_input(input_box)
        input_box.send_keys(FIRST_NAME + LAST_NAME)
        name_filled = True
      elif "phone" in attribute_text:
        clear_input(input_box)
        input_box.send_keys(PHONE)
        phone_filled = True



        # Fill by type of input
  for input_box in inputs:
    type = input_box.get_attribute('type')
    if type == "email" and not email_filled:
      clear_input(input_box)
      input_box.send_keys(EMAIL)
      email_filled = True
      continue
    if type == "tel" and not phone_filled:
      clear_input(input_box)
      input_box.send_keys(PHONE)
      phone_filled = True
      continue
    if type == "radio" or type == "checkbox":
      input_box.click()
    if type == "submit" and message_filled and name_filled and email_filled:
      #input_box.click()
      global completed
      completed += 1
      time.sleep(2)
    elif type == "submit":
      if not name_filled:
        clear_input(inputs[0])
        inputs[0].send_keys(FIRST_NAME + LAST_NAME)
        clear_input(inputs[1])
        inputs[1].send_keys(EMAIL)
        if len(inputs) == 4:
          clear_input(3)
          inputs[2].send_keys(PHONE)
        #input_box.click()
        completed += 1


def send_contact_form(driver, link):
  driver.get(link)
  forms = driver.find_elements_by_tag_name("form")
  if forms:
    print link
    fill_form(forms, link)
    raw_input("Press enter to move to the next domain >>>")

if __name__ == "__main__":
  driver = webdriver.Firefox()
  domain_list = []
  with open('captcha.txt', 'rb') as f:
    reader = csv.reader(f)
    for line in reader:
      keywords = line[1]
      searches = line[2]
      domain_list.append([line[0],keywords, searches])
  for marketed_domain in domain_list:
    keywords = marketed_domain[1]
    searches = marketed_domain[2]
    searches_per_day = str(int(round(int(searches)/30)))
    domain_name = keywords.title().strip().replace(" ", "") + ".com"
    contact_page = marketed_domain[0].strip()
    try:
      send_contact_form(driver, contact_page)
    except Exception as e:
      driver = webdriver.Firefox()
      print e
  
