University Student Tasks Management Telegram Bot
This project is a web scraping-based Telegram bot that allows students from [Mazandaran University of Science and Technology(https://ustmb.ac.ir)] to manage their academic tasks easily via Telegram. By simply entering their student code and national ID, students can access various services Such as viewing the lessons offered, checking the transcripts and more.

Features
View Offered Courses: Students can see the list of courses available for the current term.
View Temporary Transcript: Check grades of the current term in real-time.
View Complete Transcript: Access full academic records, including all past grades.
Class Selection (Coming Soon): Soon, students will be able to select courses for the next term directly from the bot.

How It Works
Login: Students enter their student code and national ID to log in.
Task Selection: After login, students can select the service they want (view courses, check transcripts, etc.).
Response: The bot scrapes the university website and returns the requested information to the user.
Installation
To run this bot on your local machine, follow these steps:

Clone the repository:

bash
Copy code
git clone [https://github.com/SajjadAhmadizad/USTMB-Scraper-Telegram-Bot](https://github.com/SajjadAhmadizad/USTMB-Scraper-Telegram-Bot)
cd USTMB-Scraper-Telegram-Bot
Install required dependencies:

bash
Copy code
pip install -r requirements.txt

ش
Set up your environment variables:

TELEGRAM_BOT_TOKEN: Your bot's Telegram API token.
DATABASE_URL: Your database url.
TERM_CODE: Current term code(like 14031 or 14022).

And then Run the bot:
bash
Copy code
python TelegramBot/main.py

Technologies Used
Python: Programming Language.
BeautifulSoup: For web scraping the university's website.
Telebot: For interacting with the Telegram API.
SQLAlchemy: To communicate with the database and store user information.
Future Enhancements
Course Selection: Students will be able to choose and register for courses directly through the bot (coming soon).

Security and Privacy
This bot collects student information such as student code and national ID to access academic services. However, all data is handled securely, and no personal data is stored or shared.

Contribution
If you would like to contribute to this project:

Contact
For any issues or questions, feel free to reach out:

Email: ahmadizadsajjad@gmail.com
Telegram ID: [@Sajjad_a_b](https://t.me/sajjad_a_b)
