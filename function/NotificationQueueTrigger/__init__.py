import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    logging.info(f'Start-----ServiceBusMessage ')
    notification_id = int(msg.get_body().decode('utf-8'))

    # TODO: Get connection to database
    conn_string = os.getenv('DB_URL')
    conection = psycopg2.connect(conn_string)
    logging.info(f'connection----- {conn_string}')
    try:
        cur = conection.cursor()
        cur.execute("select message, subject from notification where id = %s;", (notification_id,))
        msgContent, subject = cur.fetchone()

        # TODO: Get attendees email and name
        cur.execute("select email from attendee")
        attendees = cur.fetchall()
        logging.info(f'Attendee----- {len(attendees)}')

        emails = list(map(lambda x: x[0], attendees))
        count = send_email(emails, subject, msgContent)

        total_attendees = f'Notification {count}'
        completed_date = datetime.utcnow()
        cur.execute("update notification set status = %s, completed_date = %s where id = %s;", (total_attendees, completed_date, notification_id))
        conection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conection.close()

def send_email(email, subject, body):
    logging.info(f'Email----- {email}')
    logging.info(f'Subject----- {subject}')
    logging.info(f'Body----- {body}')

    apiKey = os.getenv('SENDGRID_API_KEY')
    if not apiKey:
        message = Mail(
            from_email= os.getenv.get('ADMIN_EMAIL_ADDRESS'),
            to_emails=email,
            subject=subject,
            plain_text_content=body)

        sg = SendGridAPIClient(apiKey)
        sg.send(message)