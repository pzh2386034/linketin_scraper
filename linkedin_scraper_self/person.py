import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
import os
from linkedin_scraper import selectors
import time
import json

class Person(Scraper):

    __TOP_CARD = "pv-top-card"
    __WAIT_FOR_ELEMENT_TIMEOUT = 10

    def __init__(
        self,
        linkedin_url=None,
        name=None,
        about=None,
        experiences=None,
        educations=None,
        interests=None,
        accomplishments=None,
        company=None,
        job_title=None,
        contacts=None,
        driver=None,
        get=True,
        scrape=True,
        close_on_complete=True,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about or []
        self.experiences = experiences or []
        self.educations = educations or []
        self.interests = interests or []
        self.accomplishments = accomplishments or []
        self.also_viewed_urls = []
        self.contacts = contacts or []

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape(self, close_on_complete=True):
        if self.is_signed_in():
            self.scrape_logged_in(close_on_complete=close_on_complete)
        else:
            print("you are not logged in!")
            x = input("please verify the capcha then press any key to continue...")
            self.scrape_not_logged_in(close_on_complete=close_on_complete)

    def _click_see_more_by_class_name(self, class_name):
        try:
            _ = WebDriverWait(self.driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            div = self.driver.find_element_by_class_name(class_name)
            div.find_element_by_tag_name("button").click()
        except Exception as e:
            pass



    def getExperience(self):
                # get experience
        driver = self.driver
        works = []
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/5));"
        )

        ## Click SEE MORE
        self._click_see_more_by_class_name("pv-experience-section__see-more")
        time.sleep(1)
        # try:
        #     _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
        #         EC.presence_of_element_located((By.ID, "experience-section"))
        #     )

        # except:
        #     exp = None
        exp = driver.find_element_by_id("experience-section")

        if exp is not None:
            for position in exp.find_elements_by_class_name("pv-position-entity"):
                position_title = position.find_element_by_tag_name("h3").text.strip()

                try:
                    company = position.find_elements_by_tag_name("p")[1].text.strip()
                except:
                    company = None
                try:
                    times = str(
                        position.find_elements_by_tag_name("h4")[0]
                        .find_elements_by_tag_name("span")[1]
                        .text.strip()
                    )
                    from_date = " ".join(times.split(" ")[:2])
                    to_date = " ".join(times.split(" ")[3:])
                except:
                    from_date = None
                    to_date = None
                try:
                    duration = (
                        position.find_elements_by_tag_name("h4")[1]
                        .find_elements_by_tag_name("span")[1]
                        .text.strip()
                    )
                except:
                    duration = None
                try:
                    location = (
                        position.find_elements_by_tag_name("h4")[2]
                        .find_elements_by_tag_name("span")[1]
                        .text.strip()
                    )
                except:
                    location = None

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                    company_name=company,
                )
                works.append(experience)
        return works

    def getEducation(self):
        # get education
        ## Click SEE MORE
        driver = self.driver
        schools = []
        self._click_see_more_by_class_name("pv-education-section__see-more")
        # try:
        #     _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
        #         EC.presence_of_element_located((By.ID, "education-section"))
        #     )

        # except:
        #     print("none education@@@@@")
        #     edu = None
        time.sleep(1)
        edu = driver.find_element_by_id("education-section")
        if edu:
            for school in edu.find_elements_by_class_name("pv-profile-section__list-item"):
                university = school.find_element_by_class_name("pv-entity__school-name").text.strip()
                print("university:" + university)
                try:
                    degree = (
                        school.find_element_by_class_name("pv-entity__degree-name")
                        .find_elements_by_tag_name("span")[1]
                        .text.strip()
                    )
                except:
                    print("none degree@@@@@")
                    degree = None
                try:
                    times = (
                        school.find_element_by_class_name("pv-entity__dates")
                        .find_elements_by_tag_name("span")[1]
                        .text.strip()
                    )
                    from_date, to_date = (times.split(" ")[0], times.split(" ")[2])
                except:
                    print("none times@@@@@")
                    from_date, to_date = (None, None)
                education = Education(
                    from_date=from_date,
                    to_date=to_date,
                    degree=degree,
                    school_name=university,
                )
                #education.institution_name = university
                #self.add_education(education)
                schools.append(education)
        return schools



    def scrape_logged_in(self, close_on_complete=True):
        driver = self.driver
        duration = None

        root = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located(
                (
                    By.CLASS_NAME,
                    self.__TOP_CARD,
                )
            )
        )

        self.name = root.find_element_by_class_name(selectors.NAME).text.strip()

        # get about
        try:
            see_more = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__more']",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", see_more)

            about = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__raw-line']",
                    )
                )
            )
        except:
            about = None
        if about:
            self.add_about(about.text.strip())

        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )

        # get experience
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight*3/5));"
        )

        # get interest
        try:

            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            interestContainer = driver.find_element_by_xpath(
                "//*[@class='pv-profile-section pv-interests-section artdeco-container-card artdeco-card ember-view']"
            )
            for interestElement in interestContainer.find_elements_by_xpath(
                "//*[@class='pv-interest-entity pv-profile-section__card-item ember-view']"
            ):
                interest = Interest(
                    interestElement.find_element_by_tag_name("h3").text.strip()
                )
                self.add_interest(interest)
        except:
            pass

        # get accomplishment
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']",
                    )
                )
            )
            acc = driver.find_element_by_xpath(
                "//*[@class='pv-profile-section pv-accomplishments-section artdeco-container-card artdeco-card ember-view']"
            )
            for block in acc.find_elements_by_xpath(
                "//div[@class='pv-accomplishments-block__content break-words']"
            ):
                category = block.find_element_by_tag_name("h3")
                for title in block.find_element_by_tag_name(
                    "ul"
                ).find_elements_by_tag_name("li"):
                    accomplishment = Accomplishment(category.text, title.text)
                    self.add_accomplishment(accomplishment)
        except:
            pass

        # get connections
        try:
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mn-connections"))
            )
            def see_more_connector():
                try:
                    show_click = driver.find_element_by_xpath('//button//span[text()="Show more results"]')
                    print("show more results click.............")
                    show_click.click()
                except:
                    js = 'window.scrollTo(0,%s)'%(100*100)
                    driver.execute_script(js)
                    time.sleep(1)
                tmp = len(driver.find_elements_by_class_name("mn-connection-card"))
                print("scroll to num:%d" %(tmp))
                return tmp

            header = driver.find_element_by_xpath('//header[@class="mn-connections__header"]')
            total_conn_str = header.find_element_by_tag_name("h1").text.strip()
            num_array = total_conn_str.split(' ')
            num = num_array[0]
            total_conn = int(num.replace(',', ''))

            driver.maximize_window()
            global counts_connection
            counts_connection= len(driver.find_elements_by_class_name("mn-connection-card"))
            print("begin to get connections, num:%d, total_num:%d" %(counts_connection, total_conn))
            i = 0

            while (True):
                if ( (i >= counts_connection - 3) and counts_connection != total_conn):
                    print("need to scroll......")
                    counts_connection = see_more_connector()
                print("num:%d, counts_connection:%d, total:%d" %(i, counts_connection, total_conn))
                if (i >= counts_connection):
                    break
                connections = driver.find_elements_by_xpath('//a[@class="ember-view mn-connection-card__link"]')

                connections[i].click()
                #time.sleep(2)
                #name = driver.find_element_by_xpath('//div//h1[contains(@class, "text-heading-xlarge")]').text.strip()
                _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.ID, "experience-section"))
                )
                experiences = self.getExperience()
                print("GET Experiences:%d" % ( len(experiences) ) )
                educations = self.getEducation()
                print("GET Educations:%d" % ( len(educations)  ))
                #print(name)
                driver.execute_script("window.scrollTo(0, 0);")
                # element = driver.find_element_by_xpath('//a[text()="Contact info"]')
                # driver.execute_script("arguments[0].scrollIntoView();", element)

                driver.find_element_by_xpath('//a[text()="Contact info"]').click()
                #time.sleep(2)
                _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.ID, "pv-contact-info"))
                )
                name = driver.find_element_by_id("pv-contact-info").text.strip()
                print(name)


                detail_info = driver.find_elements_by_class_name("pv-contact-info__contact-type")

                #detail_info = contact_info.find_elements_by_class_name("pv-contact-info__ci-container")
                def load_detail(detail_info):
                    for info in detail_info:
                        header = info.find_element_by_class_name("pv-contact-info__header").text.strip()
                        #print(header)
                        if "Profile" in header:
                            detail = info.find_element_by_class_name("pv-contact-info__ci-container")
                            link = detail.find_element_by_class_name("pv-contact-info__contact-link")
                            url_test = link.get_attribute("href")
                            print(header + ":" +url_test)
                        elif header == "Phone" or header == "IM":
                            elements = info.find_elements_by_class_name("pv-contact-info__ci-container")
                            for detail in elements:
                                if detail.tag_name == "li":
                                    ss = info.find_elements_by_tag_name("span") # findElements(By.tagName("span"))
                                    print(header + ":" +ss[0].text.strip()+ss[1].text.strip())
                        elif header == "Email":
                            detail = info.find_element_by_class_name("pv-contact-info__ci-container")
                            link = detail.find_element_by_class_name("pv-contact-info__contact-link")
                            url_test = link.get_attribute("href")
                            print(header + ":" +url_test)

                        elif header == "Birthday" or header == "Connected" :
                            detail = info.find_element_by_class_name("pv-contact-info__ci-container")
                            item = detail.find_element_by_class_name("pv-contact-info__contact-item")
                            txt = item.text.strip()
                            print(header + ":" +txt)
                        else:
                            print("NO DEAL:" + header)

                load_detail(detail_info)
                driver.back()
                time.sleep(2)
                #print(driver.current_url)
                driver.back()
                time.sleep(2)
                if (i < 32):
                    i = i+6
                else:
                    i = i+3
                #print(driver.current_url)
                counts_connection = len(driver.find_elements_by_class_name("mn-connection-card"))
                #pv-contact-info__ci-container
                #contact = Contact(name=name, occupation=occupation, url=url)
                #self.add_contact(contact)

        except Exception as e:
            print("exception!!!!!!!!!!!!" + e)

        if close_on_complete:
            driver.quit()

    def scrape_not_logged_in(self, close_on_complete=True, retry_limit=10):
        driver = self.driver
        retry_times = 0
        while self.is_signed_in() and retry_times <= retry_limit:
            page = driver.get(self.linkedin_url)
            retry_times = retry_times + 1

        # get name
        self.name = driver.find_element_by_class_name(
            "top-card-layout__title"
        ).text.strip()

        # get experience
        try:
            _ = WebDriverWait(driver, self.__WAIT_FOR_ELEMENT_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "experience"))
            )
            exp = driver.find_element_by_class_name("experience")
        except:
            exp = None

        if exp is not None:
            for position in exp.find_elements_by_class_name(
                "experience-item__contents"
            ):
                position_title = position.find_element_by_class_name(
                    "experience-item__title"
                ).text.strip()
                company = position.find_element_by_class_name(
                    "experience-item__subtitle"
                ).text.strip()

                try:
                    times = position.find_element_by_class_name(
                        "experience-item__duration"
                    )
                    from_date = times.find_element_by_class_name(
                        "date-range__start-date"
                    ).text.strip()
                    try:
                        to_date = times.find_element_by_class_name(
                            "date-range__end-date"
                        ).text.strip()
                    except:
                        to_date = "Present"
                    duration = position.find_element_by_class_name(
                        "date-range__duration"
                    ).text.strip()
                    location = position.find_element_by_class_name(
                        "experience-item__location"
                    ).text.strip()
                except:
                    from_date, to_date, duration, location = (None, None, None, None)

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )

        # get education
        edu = driver.find_element_by_class_name("education__list")
        for school in edu.find_elements_by_class_name("result-card"):
            university = school.find_element_by_class_name(
                "result-card__title"
            ).text.strip()
            degree = school.find_element_by_class_name(
                "education__item--degree-info"
            ).text.strip()
            try:
                times = school.find_element_by_class_name("date-range")
                from_date = times.find_element_by_class_name(
                    "date-range__start-date"
                ).text.strip()
                to_date = times.find_element_by_class_name(
                    "date-range__end-date"
                ).text.strip()
            except:
                from_date, to_date = (None, None)
            education = Education(from_date=from_date, to_date=to_date, degree=degree)

            education.institution_name = university
            self.add_education(education)

        if close_on_complete:
            driver.close()

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
