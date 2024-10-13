<h3>University Student Tasks Management Telegram Bot.</h3><br/>
This project is a web scraping-based Telegram bot that allows students from [Mazandaran University of Science and Technology](https://ustmb.ac.ir) to manage their academic tasks easily via Telegram. By simply entering their student code and national ID, students can access various services Such as viewing the lessons offered, checking the transcripts and more.<br/><br/>

Features<br/>
View Offered Courses: Students can see the list of courses available for the current term.<br/>
View Temporary Transcript: Check grades of the current term in real-time.<br/>
View Complete Transcript: Access full academic records, including all past grades.<br/>
Class Selection (Coming Soon): Soon, students will be able to select courses for the next term directly from the bot.<br/><br/>

How It Works<br/>
Login: Students enter their student code and national ID to log in.<br/>
Task Selection: After login, students can select the service they want (view courses, check transcripts, etc.).<br/>
Response: The bot scrapes the university website and returns the requested information to the user.<br/>
Installation<br/>
To run this bot on your local machine, follow these steps:<br/>

Clone the repository:<br/>

```bash
git clone [https://github.com/SajjadAhmadizad/USTMB-Scraper-Telegram-Bot](https://github.com/SajjadAhmadizad/USTMB-Scraper-Telegram-Bot)
cd USTMB-Scraper-Telegram-Bot
```
Install required dependencies:<br/>
```bash
pip install -r requirements.txt
```
<br/>
Set up your environment variables:
<br/>
TELEGRAM_BOT_TOKEN: Your bot's Telegram API token.<br/>
DATABASE_URL: Your database url.<br/>
TERM_CODE: Current term code(like 14031 or 14022).<br/><br/>

And then Run the bot:<br/>
```bash
python TelegramBot/main.py
```
<br/>
<strong>Technologies Used</strong><br/>
![Python Icon](https://www.python.org/static/community_logos/python-logo-master-v3-TM.png)
Python: Programming Language.<br/>
BeautifulSoup: For web scraping the university's website.<br/>
Telebot: For interacting with the Telegram API.<br/>
SQLAlchemy: To communicate with the database and store user information.<br/>
Future Enhancements<br/>
Course Selection: Students will be able to choose and register for courses directly through the bot (coming soon).<br/><br/>

Security and Privacy<br/>
This bot collects student information such as student code and national ID to access academic services. However, all data is handled securely, and no personal data is stored or shared.<br/><br/>

Contribution<br/>
If you would like to contribute to this project:<br/><br/>

Contact<br/>
For any issues or questions, feel free to reach out:<br/><br/>

Email: ahmadizadsajjad@gmail.com<br/>
![Telegram Icon](https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg)
Telegram ID: [@Sajjad_a_b](https://t.me/sajjad_a_b)<br/>
![Telegram Icon](https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg)
Telegram Bot ID:[@USTMB_bot](https://t.me/ustmb_bot)
