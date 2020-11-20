from tkinter import *
from tkinter import filedialog
import os.path
import sqlite3
import imghdr
import smtplib, ssl
import random
import imutils
import argparse
from cv2 import cv2
from pyimagesearch.shapedetector import ShapeDetector


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



root = Tk()
root.geometry('500x500')
root.title("safeBox")

label_0 = Label(root, text="Welcome to your safeBox",width=20,font=("bold", 20))
label_0.place(x=90,y=53)


cell_number_label = Label(root, text="Email address",width=20,font=("bold", 10))
cell_number_label.place(x=80,y=130)

cell_number_entry = Entry(root)
cell_number_entry.place(x=240,y=130)

password_label = Label(root, text="Password",width=20,font=("bold", 10))
password_label.place(x=68,y=200)

password_entry = Entry(root)
password_entry.place(x=240,y=200)

images = ["./square.png","./pentagon.png", "./triangle.png", "./rectacle.png"]

# randomImage = ''
attach_file_name = random.choice(images)
number_of_attempt = 3

if not os.path.isfile('users'):

        conn = sqlite3.connect('users')
        c = conn.cursor()
        c.execute("""CREATE TABLE users (
                cell_number integer,
                password text,
                email text
                  )""")
        print ("File not exist")
        c.execute("INSERT INTO users VALUES(0812490306,'root','dryzasa@gmail.com')")

        conn.commit()
        conn.close()



selectBTN = Button(root, text='Select A Shape',width=20,bg='green',fg='white', command=selectFile)

def clearScreen():
        cell_number_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
        return 0

def submit():
        if (not cell_number_entry.get()):
            error_message = Label(root, text="Please provide an email",width=40,font=("bold", 10))
            error_message.place(x=80,y=160)

            number_of_attempt =  number_of_attempt - 1
            return 0

        if (not password_entry.get()):
            error_message = Label(root, text="Please provide a password",width=40,font=("bold", 10))
            error_message.place(x=68,y=230)

            number_of_attempt =  number_of_attempt - 1
            return 0

        conn = sqlite3.connect('users')
        c = conn.cursor()

        query = "SELECT password, email, cell_number FROM users WHERE email='" + cell_number_entry.get() + "'"

        c.execute(query)

        records = c.fetchall()

        if not records:
            error_message = Label(root, text="User Not found in the database",width=40,font=("bold", 10))
            error_message.place(x=68,y=240)


            number_of_attempt =  number_of_attempt - 1
            return 0

        if (records[0][0] != password_entry.get()):
            error_message = Label(root, text="Please provide a correct email",width=40,font=("bold", 10))
            error_message.place(x=68,y=240)

            number_of_attempt =  number_of_attempt - 1
            return 0


        mail_content = '''Hello,
        Good Day Dryza,
        We have recieve a request to acces your safe box
        Please confirm if it was you by scaning the attache image
        to your safe box

        Thank You
        '''
#The mail addresses and password
        sender_address = 'xxxxxxxxxxxxxxxxx'
        sender_pass = 'xxxxxxxx'
        receiver_address = cell_number_entry.get();

#Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Safebox Authetication Message'

#The subject line
#The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        # attach_file_name = random.choice(images)
        # randomImage = attach_file_name
        attach_file = open(attach_file_name, 'r+b') # Open the file as binary mode
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment

#add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)

#Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

        texxt = "An email was sent to " + cell_number_entry.get() 
        error_message = Label(root, text=texxt,width=50,font=("bold", 10))
        error_message.place(x=68,y=350)

        texxt = "Please scan the attache image to acces your safe box"
        error_message = Label(root, text=texxt,width=50,font=("bold", 10))
        error_message.place(x=68,y=370)


        # Button(root, text='Select A Shape',width=20,bg='green',fg='white', command=selectFile).place(x=180,y=420)

        conn.commit()
        conn.close()
        return 0



def selectFile():
        root.filename =  filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes = (("jpeg files","*.png"),("all files","*.*"))) 
        if (not root.filename):
            texxt = "Please select a valid image to scan"
            error_message = Label(root, text=texxt,width=50,font=("bold", 10))
            

        image_1 = cv2.imread(root.filename)
        image_2 = cv2.imread(attach_file_name)

        resized_1 = imutils.resize(image_1, width=300)
        ratio_1 = image_1.shape[0] / float(resized_1.shape[0])


        resized_2 = imutils.resize(image_2, width=300)
        ratio_2 = image_2.shape[0] / float(resized_2.shape[0])

# convert the resized image to grayscale, blur it slightly,
# and threshold it
        gray_1 = cv2.cvtColor(resized_1, cv2.COLOR_BGR2GRAY)
        blurred_1 = cv2.GaussianBlur(gray_1, (5, 5), 0)
        thresh_1 = cv2.threshold(blurred_1, 60, 255, cv2.THRESH_BINARY)[1]

        gray_2 = cv2.cvtColor(resized_2, cv2.COLOR_BGR2GRAY)
        blurred_2 = cv2.GaussianBlur(gray_2, (5, 5), 0)
        thresh_2 = cv2.threshold(blurred_2, 60, 255, cv2.THRESH_BINARY)[1]

# find contours in the thresholded image and initialize the
# shape detector
        cnts_1 = cv2.findContours(thresh_1.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        cnts_1 = imutils.grab_contours(cnts_1)

        cnts_2 = cv2.findContours(thresh_2.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        cnts_2 = imutils.grab_contours(cnts_2)

        sd = ShapeDetector()

        # M_1= cv2.moments(cnts_1[0])
        # cX_1 = int((M_1["m10"] / M_1["m00"]) * ratio_1)
        # cY_1 = int((M_1["m01"] / M_1["m00"]) * ratio_1)
        shape_1 = sd.detect(cnts_1[0])


        # M_2= cv2.moments(cnts_1[0])
        # cX_2 = int((M_2["m10"] / M_2["m00"]) * ratio_2)
        # cY_2 = int((M_2["m01"] / M_2["m00"]) * ratio_2)
        shape_2 = sd.detect(cnts_2[0])


        if (shape_2 == shape_1):
            label_0 = Label(root, text="CONGRATULATION,",width=20,font=("bold", 20))
            label_0.place(x=90,y=463)

            label_0 = Label(root, text="You have access to your safe box",width=40,font=("bold", 20))
            label_0.place(x=90,y=433)
        else:
            clearScreen()
            label_0 = Label(root, text="Sorry, You have scan a wrong shape",width=40,font=("bold", 20))
            label_0.place(x=90,y=463)
            # number_of_attempt =  number_of_attempt - 1





Button(root, text='Submit',width=20,bg='brown',fg='white', command=submit).place(x=180,y=280)

root.mainloop()
