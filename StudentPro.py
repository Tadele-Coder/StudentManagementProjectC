import tkinter as tk
from tkinter.ttk import Combobox
from tkinter.filedialog import askopenfilename, askdirectory
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import re
import random
import sqlite3
import pymysql
import os
import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import my_email
from tkinter.ttk import Combobox, Treeview
from tkinter.scrolledtext import ScrolledText
import threading

root = tk.Tk()

root.geometry('500x600')
root.title('Student Management and Registration System')
root.resizable(0, 0)

bg_color = '#273b7a'

login_student_icon = tk.PhotoImage(file='loginstudent.png')
login_admin_icon = tk.PhotoImage(file='loginadmin.png')
add_student_icon = tk.PhotoImage(file='addstudent.png')
locked_icon = tk.PhotoImage(file='lockedeye.png')
unlocked_icon = tk.PhotoImage(file='unlockedeye.png')

student_gender = tk.StringVar()
class_list = ['KG1', 'KG2', 'KG3', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12']


def init_database():
    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
    mycursor = con.cursor()
    query = 'select * from data'
    mycursor.execute(query)
    con.commit()
    print(mycursor.fetchall())
    con.close()


def check_id_already_exists(Id):
    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
    mycursor = con.cursor()
    query = 'select Id from data where Id=%s'
    mycursor.execute(query, (Id,))

    con.commit()
    response = mycursor.fetchall()
    con.close()
    return response


def check_valid_password(Id, Password):
    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
    mycursor = con.cursor()
    query = 'select Id, Password from data where Id=%s and Password=%s'
    mycursor.execute(query, (Id, Password))

    con.commit()
    response = mycursor.fetchall()
    con.close()
    return response


def confirmation_box(message):
    answer = tk.BooleanVar()
    answer.set(False)

    def action(ans):
        answer.set(ans)
        confirmation_box_fm.destroy()

    confirmation_box_fm = tk.Frame(root, highlightbackground=bg_color,
                                   highlightthickness=3)
    message_lb = tk.Label(confirmation_box_fm, text=message, font=('bold', 15))
    message_lb.pack(pady=20)

    cancel_btn = tk.Button(confirmation_box_fm, text='Cancel', font=('bold', 15),
                           bd=0, bg=bg_color, fg='white', command=lambda: action(False))
    cancel_btn.place(x=50, y=160)

    yes_btn = tk.Button(confirmation_box_fm, text='Yes', font=('bold', 15),
                        bd=0, bg=bg_color, fg='white', command=lambda: action(True))
    yes_btn.place(x=190, y=160, width=80)

    confirmation_box_fm.place(x=100, y=120, width=320, height=220)
    root.wait_window(confirmation_box_fm)
    return answer.get()


def message_box(message):
    message_box_fm = tk.Frame(root, highlightbackground=bg_color,
                              highlightthickness=3)
    close_btn = tk.Button(message_box_fm, text='X', bd=0, font=('bold', 13),
                          fg=bg_color, command=lambda: message_box_fm.destroy())
    close_btn.place(x=290, y=5)
    message_lb = tk.Label(message_box_fm, text=message, font=('bold', 15))
    message_lb.pack(pady=50)
    message_box_fm.place(x=100, y=120, width=320, height=200)


def draw_student_card(student_pic_path, student_data):
    labels = """
ID Number:
Name:
Gender:
Age:
Class:
Contact:
Email:
"""

    student_card = Image.open('student_card_frame.png')
    pic = Image.open(student_pic_path).resize((100, 100))
    student_card.paste(pic, (15, 25))
    draw = ImageDraw.Draw(student_card)

    heading_font = ImageFont.truetype('bahnschrift', 18)
    label_font = ImageFont.truetype('arial', 15)
    data_font = ImageFont.truetype('arial', 13)

    draw.text(xy=(150, 60), text='Student Card', fill=(0, 0, 0), font=heading_font)
    draw.multiline_text(xy=(15, 120), text=labels, fill=(0, 0, 0), font=label_font, spacing=6)
    draw.multiline_text(xy=(95, 120), text=student_data, fill=(0, 0, 0), font=data_font, spacing=8)

    return student_card


def student_card_page(student_card_obj, bypass_login_page=False):
    def save_student_card():
        path = askdirectory()

        if path:
            # print(path)
            student_card_obj.save(f'{path}/student_card.png')

    def print_student_card():

        path = askdirectory()

        if path:
            # print(path)
            student_card_obj.save(f'{path}/student_card.png')
            win32api.ShellExecute(0, 'Print', f'{path}/student_card.png', None, '. ', 0)

    def close_page():

        student_card_page_fm.destroy()

        if not bypass_login_page:
            root.update()
            student_login_page()

    student_card_img = ImageTk.PhotoImage(student_card_obj)

    student_card_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(student_card_page_fm, text='Student Card',
                          bg=bg_color, fg='white', font=('bold', 18))
    heading_lb.place(x=0, y=0, width=400)

    close_btn = tk.Button(student_card_page_fm, text='X', bg=bg_color,
                          fg='white', font=('bold', 13), bd=0, command=close_page)
    close_btn.place(x=370, y=0)

    student_card_lb = tk.Label(student_card_page_fm, image=student_card_img)
    student_card_lb.place(x=50, y=50)

    student_card_lb.image = student_card_img

    save_student_card_btn = tk.Button(student_card_page_fm, text='Save Student Card',
                                      bg=bg_color, fg='white', command=save_student_card,
                                      font=('bold', 15), bd=1)
    save_student_card_btn.place(x=80, y=375)

    print_student_card_btn = tk.Button(student_card_page_fm, text='🖨',
                                       bg=bg_color, fg='white', command=print_student_card,
                                       font=('bold', 18), bd=1)
    print_student_card_btn.place(x=270, y=370)

    student_card_page_fm.place(x=50, y=30, width=400, height=450)


def welcome_page():
    def forward_to_create_account_page():
        welcome_page_fm.destroy()
        root.update()
        add_acount_page()

    def forward_student_page():
        welcome_page_fm.destroy()
        root.update()
        student_login_page()

    def forward_admin_page():
        welcome_page_fm.destroy()
        root.update()
        admin_login_page()

    welcome_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(welcome_page_fm, text='Welcome to Student Registration \nand Management System',
                          bg=bg_color, fg='white', font=('bold', 18))
    heading_lb.place(x=0, y=0, width=400)
    welcome_page_fm.pack(pady=30)
    welcome_page_fm.pack_propagate(False)
    welcome_page_fm.config(width=400, height=420)

    student_login_btn = tk.Button(welcome_page_fm, text='Login Student',
                                  font=('bold', 15), bd=0, bg=bg_color, fg='white', command=forward_student_page)
    student_login_btn.place(x=120, y=125, width=200)

    student_login_img = tk.Button(welcome_page_fm, image=login_student_icon, bd=0)
    student_login_img.place(x=60, y=100)

    admin_login_btn = tk.Button(welcome_page_fm, text='Admin Student', command=forward_admin_page,
                                font=('bold', 15), bd=0, bg=bg_color, fg='white')
    admin_login_btn.place(x=120, y=225, width=200)

    admin_login_img = tk.Button(welcome_page_fm, image=login_admin_icon, bd=0)
    admin_login_img.place(x=50, y=200)

    addstudent_login_btn = tk.Button(welcome_page_fm, text='Create Account',
                                     font=('bold', 15), bd=0, bg=bg_color, fg='white',
                                     command=forward_to_create_account_page)
    addstudent_login_btn.place(x=120, y=325, width=200)

    addstudent_login_img = tk.Button(welcome_page_fm, image=add_student_icon, bd=0)
    addstudent_login_img.place(x=60, y=300)


def sendmail_to_student(email, message, subject):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    username = 'my_email.email_address'
    password = 'my_email.password'

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email
    msg.attach(MIMEText(_text=message, _subtype='html'))

    smtp_connection = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user=username, password=password)
    smtp_connection.sendmail(from_addr=username, to_addrs=email, msg=msg.as_string())
    print('Mail Sent Successful.')


def forgot_password_page():
    def recover_password():

        if check_id_already_exists(Id=student_id_ent.get()):
            con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
            mycursor = con.cursor()

            query = 'select Password from data where Id=%s'
            mycursor.execute(query, (student_id_ent.get()))

            con.commit()
            recover_password = mycursor.fetchall()[0][0]

            query = 'select Email from data where Id=%s'
            mycursor.execute(query, (student_id_ent.get()))
            con.commit()
            student_email = mycursor.fetchall()[0][0]

            con.close()

            confirmation = confirmation_box(message=f"""
We will Send\nYour Forgot Password
Via Your Email Address:
{student_email}
Do You Want to Continue ?""")
            if confirmation:
                msg = f"""<h1>Your Forgot Password is:</h1>
                <h2>{recover_password}</h2>
                <p>Once Remember Your Password, After Delete This Message</p>

                """
                sendmail_to_student(email=student_email, message=msg, subject='Password Recovery')


        else:
            print('Incorrect ID')
            message_box(message='!Invalid ID Number')

    forgot_password_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(forgot_password_page_fm, text='! Forgetting Password',
                          font=('bold', 15), bg=bg_color, fg='white')
    heading_lb.place(x=0, y=0, width=350)
    close_btn = tk.Button(forgot_password_page_fm, text='X', font=('bold', 13), bg=bg_color, fg='white',
                          bd=0, command=lambda: forgot_password_page_fm.destroy())
    close_btn.place(x=320, y=0)

    student_id_lb = tk.Label(forgot_password_page_fm, text='Enter Student ID Number.', font=('bold', 13))
    student_id_lb.place(x=70, y=40)
    student_id_ent = tk.Entry(forgot_password_page_fm, font=('bold', 15), justify=tk.CENTER)
    student_id_ent.place(x=70, y=70, width=180)

    info_lb = tk.Label(forgot_password_page_fm, text=""" Via Your Email Address
We will Send to You
Your Forgot Password.""", justify=tk.LEFT)
    info_lb.place(x=75, y=110)

    next_btn = tk.Button(forgot_password_page_fm, text='Next',
                         font=('bold', 13), bg=bg_color, fg='white', command=recover_password)
    next_btn.place(x=130, y=200, width=80)

    forgot_password_page_fm.place(x=75, y=120, width=350, height=250)


def fetch_student_data(query):
    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
    mycursor = con.cursor()
    mycursor.execute(query)
    con.commit()
    response = mycursor.fetchall()
    con.close()
    return response


def student_dashboard(student_id):
    get_student_details = fetch_student_data(f"""
    select Name, Age, Gender, Class, Phone_number, Email from data where Id = '{student_id}'
    """)
    get_student_pic = fetch_student_data(f"""
        select Image from data where Id = '{student_id}'
        """)
    student_pic = BytesIO(get_student_pic[0][0])

    def logout():

        confirm = confirmation_box(message='Do You Want to\nLogout Your Account?')

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()

    def switch(indicator, page):

        home_btn_indicator.config(bg='#c3c3c3')
        student_card_btn_indicator.config(bg='#c3c3c3')
        security_btn_indicator.config(bg='#c3c3c3')
        edit_data_btn_indicator.config(bg='#c3c3c3')
        delete_account_indicator.config(bg='#c3c3c3')

        indicator.config(bg=bg_color)
        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()
        page()

    dashboard_fm = tk.Frame(root, highlightcolor=bg_color, highlightthickness=3)

    options_fm = tk.Frame(dashboard_fm, highlightbackground=bg_color, highlightthickness=2, bg='#c3c3c3')

    home_btn = tk.Button(options_fm, text='Home', font=('bold', 15),
                         fg=bg_color, bg='#c3c3c3', bd=0,
                         command=lambda: switch(indicator=home_btn_indicator, page=home_page))
    home_btn.place(x=10, y=50)

    home_btn_indicator = tk.Label(options_fm, bg=bg_color)
    home_btn_indicator.place(x=5, y=48, width=3, height=40)

    student_card_btn = tk.Button(options_fm, text='Student\nCard', font=('bold', 15),
                                 fg=bg_color, bg='#c3c3c3', bd=0, justify=tk.LEFT,
                                 command=lambda:
                                 switch(indicator=student_card_btn_indicator, page=dashboard_student_card_page))
    student_card_btn.place(x=10, y=100)

    student_card_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    student_card_btn_indicator.place(x=5, y=108, width=3, height=40)

    security_card_btn = tk.Button(options_fm, text='Security', font=('bold', 15),
                                  fg=bg_color, bg='#c3c3c3', bd=0,
                                  command=lambda:
                                  switch(indicator=security_btn_indicator, page=security_page))
    security_card_btn.place(x=10, y=170)

    security_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    security_btn_indicator.place(x=5, y=170, width=3, height=40)

    edit_data_btn = tk.Button(options_fm, text='Edit Data', font=('bold', 15),
                              fg=bg_color, bg='#c3c3c3', bd=0,
                              justify=tk.LEFT, command=lambda:
        switch(indicator=edit_data_btn_indicator, page=edit_account_data_page))

    edit_data_btn.place(x=10, y=220)

    edit_data_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    edit_data_btn_indicator.place(x=5, y=220, width=3, height=40)

    delete_account_btn = tk.Button(options_fm, text='Delete\nAccount', font=('bold', 15),
                                   fg=bg_color, bg='#c3c3c3', bd=0,
                                   justify=tk.LEFT,
                                   command=lambda:
                                   switch(indicator=delete_account_indicator, page=delete_account_page))
    delete_account_btn.place(x=10, y=270)

    delete_account_indicator = tk.Label(options_fm, bg='#c3c3c3')
    delete_account_indicator.place(x=5, y=280, width=3, height=40)

    logout_btn = tk.Button(options_fm, text='Logout', font=('bold', 15),
                           fg=bg_color, bg='#c3c3c3', bd=0, command=logout)
    logout_btn.place(x=10, y=340)

    options_fm.place(x=0, y=0, width=120, height=575)

    def home_page():

        student_pic_image_obj = Image.open(student_pic)
        size = 100
        mask = Image.new(mode='L', size=(size, size))

        draw_circle = ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0, 0, size, size), fill=255, outline=True)
        output = ImageOps.fit(image=student_pic_image_obj, size=mask.size, centering=(1, 1))
        output.putalpha(mask)
        student_picture = ImageTk.PhotoImage(output)

        home_page_fm = tk.Frame(pages_fm)
        student_pic_lb = tk.Label(home_page_fm, image=student_picture)
        student_pic_lb.image = student_picture

        student_pic_lb.place(x=10, y=10)
        home_page_lb = tk.Label(home_page_fm, text='Home Page', font=('bold', 15))
        home_page_lb.place(x=100, y=200)

        hi_lb = tk.Label(home_page_fm, text=f'!Hi {get_student_details[0][0]}', font=('bold', 15))
        hi_lb.place(x=130, y=50)

        student_details = f"""
Id: {student_id}\n
Name: {get_student_details[0][0]}\n
Age: {get_student_details[0][1]}\n
Gender: {get_student_details[0][2]}\n
Class: {get_student_details[0][3]}\n
Contact: {get_student_details[0][4]}\n
Email: {get_student_details[0][5]}
"""
        student_details_lb = tk.Label(home_page_fm, text=student_details,
                                      font=('bold', 13), justify=tk.LEFT)
        student_details_lb.place(x=20, y=130)

        home_page_fm.pack(fill=tk.BOTH, expand=True)

    def dashboard_student_card_page():

        student_details = f"""
        {student_id}
        {get_student_details[0][0]}
        {get_student_details[0][2]}
        {get_student_details[0][1]}
        {get_student_details[0][3]}
        {get_student_details[0][4]}
        {get_student_details[0][5]}
        """

        student_card_img_obj = draw_student_card(student_pic_path=student_pic, student_data=student_details)

        def save_student_card():
            path = askdirectory()

            if path:
                # print(path)
                student_card_img_obj.save(f'{path}/student_card.png')

        def print_student_card():

            path = askdirectory()

            if path:
                # print(path)
                student_card_img_obj.save(f'{path}/student_card.png')
                win32api.ShellExecute(0, 'Print', f'{path}/student_card.png', None, '. ', 0)

        student_card_img = ImageTk.PhotoImage(student_card_img_obj)
        student_card_page_fm = tk.Frame(pages_fm)
        card_lb = tk.Label(student_card_page_fm, image=student_card_img)
        card_lb.image = student_card_img
        card_lb.place(x=20, y=50)

        save_student_card_btn = tk.Button(student_card_page_fm, text='Save Student Card',
                                          font=('bold', 15), bd=1,
                                          fg='white', bg=bg_color, command=save_student_card)
        save_student_card_btn.place(x=40, y=400)

        print_student_card_btn = tk.Button(student_card_page_fm, text='🖨',
                                           font=('bold', 15), bd=1, fg='white', bg=bg_color, command=print_student_card)
        print_student_card_btn.place(x=240, y=400)

        student_card_page_fm.pack(fill=tk.BOTH, expand=True)

    def security_page():

        def show_hide_password():

            if current_password_ent['show'] == '*':
                current_password_ent.config(show='')
                show_hide_btn.config(image=unlocked_icon)
            else:
                current_password_ent.config(show='*')
                show_hide_btn.config(image=locked_icon)

        def set_password():

            if new_password_ent.get() != '':

                confirm = confirmation_box(message='Do You Want to Change\n Your Password?')

                if confirm:
                    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
                    mycursor = con.cursor()

                    mycursor.execute('update data set Password = %s where Id = %s',
                                     (new_password_ent.get(), student_id))
                    con.commit()
                    con.close()
                    message_box(message='Password Changed Successfully')
                    current_password_ent.config(state=tk.NORMAL)
                    current_password_ent.delete(0, tk.END)
                    current_password_ent.insert(0, new_password_ent.get())
                    current_password_ent.config(state='readonly')
                    new_password_ent.delete(0, tk.END)
            else:
                message_box(message='Enter New Password Required')

        security_page_fm = tk.Frame(pages_fm)

        current_password_lb = tk.Label(security_page_fm, text='Your Current Password',
                                       font=('bold', 12))
        current_password_lb.place(x=80, y=30)
        current_password_ent = tk.Entry(security_page_fm, font=('bold', 15),
                                        justify=tk.CENTER, show='*')
        current_password_ent.place(x=50, y=80)

        student_current_password = fetch_student_data(f"select password from data "
                                                      f"where Id = '{student_id}'")
        current_password_ent.insert(tk.END, student_current_password[0][0])
        current_password_ent.config(state='readonly')
        show_hide_btn = tk.Button(security_page_fm, image=locked_icon, bd=0,
                                  command=show_hide_password)
        show_hide_btn.place(x=280, y=70)

        change_password_lb = tk.Label(security_page_fm, text='Change Password',
                                      font=('bold', 15), bg='red', fg='white')
        change_password_lb.place(x=30, y=210, width=290)
        new_password_lb = tk.Label(security_page_fm, text='Set New Password', font=('bold', 12))
        new_password_lb.place(x=100, y=280)

        new_password_ent = tk.Entry(security_page_fm, font=('bold', 15), justify=tk.CENTER)
        new_password_ent.place(x=60, y=330)

        change_password_btn = tk.Button(security_page_fm, text='Set Password',
                                        font=('bold', 12), bg=bg_color, fg='white',
                                        command=set_password)
        change_password_btn.place(x=110, y=380)

        security_page_fm.pack(fill=tk.BOTH, expand=True)

    def edit_account_data_page():

        edit_account_page_fm = tk.Frame(pages_fm)

        pic_path = tk.StringVar()
        pic_path.set('')

        def open_pic():
            path = askopenfilename()
            if path:
                img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
                pic_path.set(path)
                add_pic_btn.config(image=img)
                add_pic_btn.image = img

        def remove_highlight_warning(entry):

            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightcolor=bg_color, highlightbackground='gray')

        def check_invalid_email(email):

            pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
            match = re.match(pattern=pattern, string=email)
            return match

        def check_inputs():

            nonlocal get_student_details, get_student_pic, student_pic

            if student_name_ent.get() == '':
                student_name_ent.config(highlightcolor='red', highlightbackground='red')
                student_name_ent.focus()
                message_box(message='Student Full Name is Required')

            elif student_age_ent.get() == '':
                student_age_ent.config(highlightcolor='red', highlightbackground='red')
                student_age_ent.focus()
                message_box(message='Student Contact Number is Required')


            elif student_email_ent.get() == '':
                student_email_ent.config(highlightcolor='red', highlightbackground='red')
                student_email_ent.focus()
                message_box(message='Student Email Address is Required')

            elif not check_invalid_email(email=student_email_ent.get().lower()):

                student_email_ent.config(highlightcolor='red', highlightbackground='red')
                student_email_ent.focus()
                message_box(message='Please Enter a Valid\nEmail Address')

            else:

                if pic_path.get() != '':
                    new_student_picture = Image.open(pic_path.get()).resize((100, 100))
                    new_student_picture.save('temp_pic.png')

                    with open('temp_pic.png', 'rb') as read_new_pic:
                        new_picture_binary = read_new_pic.read()
                        read_new_pic.close()

                    con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
                    mycursor = con.cursor()

                    mycursor.execute("update data set Image= %s where Id =%s", (new_picture_binary, student_id))

                Name = student_name_ent.get()
                Age = student_age_ent.get()
                Class = select_student_class_btn.get()
                Phone_number = student_contact_et.get()
                Email = student_email_ent.get()

                con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')

                mycursor = con.cursor()

                query = 'update data set Name = %s, Age = %s, Class = %s, ' \
                        'Phone_number = %s, Email = %s where Id = %s'

                mycursor.execute(query, (student_name_ent.get(), student_age_ent.get(), select_student_class_btn.get(),
                                         student_contact_et.get(), student_email_ent.get(), student_id))

                con.commit()
                con.close()

                get_student_details = fetch_student_data(f"""
                   select Name, Age, Gender, Class, Phone_number, Email from data where Id = '{student_id}'
                   """)

                get_student_pic = fetch_student_data(f"""
                       select Image from data where Id = '{student_id}'
                       """)
                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message='Data Successfully Updated.')

        student_current_pic = ImageTk.PhotoImage(Image.open(student_pic))

        add_pic_section_fm = tk.Frame(edit_account_page_fm, highlightbackground=bg_color, highlightthickness=2)
        add_pic_btn = tk.Button(add_pic_section_fm, image=student_current_pic, bd=0, command=open_pic)

        add_pic_btn.image = student_current_pic

        add_pic_btn.pack()
        add_pic_section_fm.place(x=5, y=5, width=105, height=105)

        student_name_lb = tk.Label(edit_account_page_fm, text='Enter Student Full Name.', font=('bold', 12))
        student_name_lb.place(x=5, y=130)
        student_name_ent = tk.Entry(edit_account_page_fm, font=('bold', 15),
                                    highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
        student_name_ent.place(x=5, y=160, width=180)
        student_name_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_ent))

        student_name_ent.insert(tk.END, get_student_details[0][0])

        student_age_lb = tk.Label(edit_account_page_fm, text='Enter Student Age.', font=('bold', 12))
        student_age_lb.place(x=5, y=210)

        student_age_ent = tk.Entry(edit_account_page_fm, font=('bold', 15), highlightcolor=bg_color,
                                   highlightbackground='gray', highlightthickness=2)
        student_age_ent.place(x=5, y=235, width=180)
        student_age_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_ent))

        student_age_ent.insert(tk.END, get_student_details[0][1])

        student_contact_lb = tk.Label(edit_account_page_fm, text='Enter Contact Phone Number.', font=('bold', 12))
        student_contact_lb.place(x=5, y=285)

        student_contact_et = tk.Entry(edit_account_page_fm, font=('bold', 15),
                                      highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
        student_contact_et.place(x=5, y=310, width=180)
        student_contact_et.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_et))

        student_contact_et.insert(tk.END, get_student_details[0][4])

        student_class_lb = tk.Label(edit_account_page_fm, text='Select Student Class.',
                                    font=('bold', 12))
        student_class_lb.place(x=5, y=360)

        select_student_class_btn = Combobox(edit_account_page_fm, font=('bold', 15), state='readonly',
                                            values=class_list)
        select_student_class_btn.place(x=5, y=390, width=180, height=30)

        select_student_class_btn.set(get_student_details[0][3])

        student_email_lb = tk.Label(edit_account_page_fm, text='Enter Student Email Address.', font=('bold', 12))
        student_email_lb.place(x=5, y=440)

        student_email_ent = tk.Entry(edit_account_page_fm, font=('bold', 15),
                                     highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
        student_email_ent.place(x=5, y=470, width=180)
        student_email_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_ent))

        student_email_ent.insert(tk.END, get_student_details[0][-1])

        update_data_btn = tk.Button(edit_account_page_fm, text='Update', font=('Bold', 15),
                                    fg='white', bg=bg_color, bd=0, command=check_inputs)
        update_data_btn.place(x=220, y=470, width=80)

        edit_account_page_fm.pack(fill=tk.BOTH, expand=True)

    def delete_account_page():

        def confirm_delete_account():
            confirm = confirmation_box(message='⚠ Do You Want to Delete\n Your Account?')

            if confirm:
                con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
                mycursor = con.cursor()

                query = 'delete from data where Id = %s'
                mycursor.execute(query, (student_id,))
                con.commit()
                con.close()
                dashboard_fm.destroy()
                welcome_page()
                root.update()
                message_box(message='Account Successfully Deleted')

        delete_account_page_fm = tk.Frame(pages_fm)

        delete_account_lb = tk.Label(delete_account_page_fm, text='⚠ Delete Account',
                                     bg='red', fg='white', font=('bold', 15))
        delete_account_lb.place(x=30, y=100, width=290)

        delete_account_btn = tk.Button(delete_account_page_fm, text='Delete Account',
                                       bg='red', fg='white', font=('bold', 13), command=confirm_delete_account)
        delete_account_btn.place(x=110, y=200)

        delete_account_page_fm.pack(fill=tk.BOTH, expand=True)

    pages_fm = tk.Frame(dashboard_fm, bg='gray')
    pages_fm.place(x=122, y=5, width=350, height=550)
    home_page()

    dashboard_fm.place(x=0, y=0)
    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480, height=580)


def student_login_page():
    def show_hide_password():

        if password_entry['show'] == '*':
            password_entry.config(show='')
            show_hide_btn.config(image=unlocked_icon)
        else:
            password_entry.config(show='*')
            show_hide_btn.config(image=locked_icon)

    def forward_welcome_page():
        student_login_page_fm.destroy()
        root.update()
        welcome_page()

    def forward_to_forgot_password_page():

        forgot_password_page()

    def remove_highlight_warning(entry):

        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color, highlightbackground='gray')

    def login_account():

        verify_id_number = check_id_already_exists(Id=student_id_entry.get())

        if verify_id_number:

            verify_password = check_valid_password(Id=student_id_entry.get(), Password=password_entry.get())

            if verify_password:

                id_number = student_id_entry.get()
                student_login_page_fm.destroy()
                student_dashboard(student_id=id_number)
                root.update()

            else:
                print('Password is Wrong')
                password_entry.config(highlightcolor='red', highlightbackground='red')
                message_box(message='Please Enter Valid Password')
        else:
            print('ID wrong')

            student_id_entry.config(highlightcolor='red', highlightbackground='red')
            message_box(message='Please Enter Valid Student ID')

    student_login_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    heading_lb = tk.Label(student_login_page_fm, text='Student Login Page',
                          bg=bg_color, fg='white', font=('bold', 18))
    heading_lb.place(x=0, y=0, width=400)

    student_icon_lb = tk.Label(student_login_page_fm, image=login_student_icon)
    student_icon_lb.place(x=150, y=40)

    id_number_lb = tk.Label(student_login_page_fm, text='Enter Student ID Number', font=('bold', 15))
    id_number_lb.place(x=80, y=140)

    student_id_entry = tk.Entry(student_login_page_fm, font=('bold', 15), fg=bg_color,
                                justify=tk.CENTER, highlightbackground='gray', highlightthickness=2)
    student_id_entry.place(x=80, y=190)

    student_id_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_id_entry))

    password_lb = tk.Label(student_login_page_fm, text='Enter Student Password', font=('bold', 15))
    password_lb.place(x=80, y=240)

    password_entry = tk.Entry(student_login_page_fm, font=('bold', 15), fg=bg_color,
                              justify=tk.CENTER, highlightbackground='gray', highlightthickness=2, show='*')
    password_entry.place(x=80, y=290)
    password_entry.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=password_entry))

    show_hide_btn = tk.Button(student_login_page_fm, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=288)

    login_btn = tk.Button(student_login_page_fm, text='Login', bg=bg_color,
                          font=('bold', 15), fg='white',
                          activebackground=bg_color, activeforeground='white', command=login_account)
    login_btn.place(x=95, y=340, width=200, height=40)

    forgot_password_btn = tk.Button(student_login_page_fm, text='!\n Forgot Password',
                                    fg=bg_color, bd=0, command=forward_to_forgot_password_page)
    forgot_password_btn.place(x=150, y=390)

    back_btn = tk.Button(student_login_page_fm, text='←', font=('bold', 20), bd=0, fg=bg_color,
                         command=forward_welcome_page)
    back_btn.place(x=10, y=50)

    student_login_page_fm.pack(pady=30)
    student_login_page_fm.pack_propagate(False)
    student_login_page_fm.config(width=400, height=450)


def admin_dashboard():
    def switch(indictor, page):

        home_btn_indictor.config(bg='#c3c3c3')
        find_student_btn_indictor.config(bg='#c3c3c3')
        announcement_btn_indictor.config(bg='#c3c3c3')
        indictor.config(bg=bg_color)

        for child in pages_fm.winfo_children():
            child.destroy()
            root.update()

        page()

    dashboard_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

    option_fm = tk.Frame(dashboard_fm, highlightbackground=bg_color, highlightthickness=2, bg='#c3c3c3')

    home_btn = tk.Button(option_fm, text='Home', font=('bold', 15),
                         fg=bg_color, bg='#c3c3c3', bd=0,
                         command=lambda: switch(indictor=home_btn_indictor, page=home_page))
    home_btn.place(x=10, y=50)

    home_btn_indictor = tk.Label(option_fm, text='', bg=bg_color)
    home_btn_indictor.place(x=5, y=48, width=3, height=40)

    find_student_btn = tk.Button(option_fm, text='Find\nStudent', font=('bold', 15),
                                 fg=bg_color, bg='#c3c3c3', bd=0, justify=tk.LEFT,
                                 command=lambda: switch(indictor=find_student_btn_indictor, page=find_student_page)
                                 )
    find_student_btn.place(x=10, y=100)

    find_student_btn_indictor = tk.Label(option_fm, text='', bg='#c3c3c3')
    find_student_btn_indictor.place(x=5, y=108, width=3, height=40)

    announcement_btn = tk.Button(option_fm, text='Announce\nMent🔊', font=('bold', 15),
                                 fg=bg_color, bg='#c3c3c3', bd=0,
                                 command=lambda: switch(indictor=announcement_btn_indictor, page=announcement_page))
    announcement_btn.place(x=10, y=170)

    announcement_btn_indictor = tk.Label(option_fm, text='', bg='#c3c3c3')
    announcement_btn_indictor.place(x=5, y=180, width=3, height=40)

    def logout():

        confirm = confirmation_box(message='Do You Want to\nLogout')

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()

    logout_btn = tk.Button(option_fm, text='Logout', font=('bold', 15),
                           fg=bg_color, bg='#c3c3c3', bd=0, command=logout)
    logout_btn.place(x=10, y=240)

    option_fm.place(x=0, y=0, width=120, height=575)

    def home_page():

        home_page_fm = tk.Frame(pages_fm)

        admin_icon_lb = tk.Label(home_page_fm, image=login_admin_icon)
        admin_icon_lb.image = login_admin_icon
        admin_icon_lb.place(x=10, y=10)

        hi_lb = tk.Label(home_page_fm, text='!Hi Admin', font=('bold', 15))
        hi_lb.place(x=120, y=40)

        class_list_lb = tk.Label(home_page_fm, text='Number of Students By Class.',
                                 font=('bold', 13), bg=bg_color, fg='white')
        class_list_lb.place(x=20, y=130)

        students_number_lb = tk.Label(home_page_fm, text='', font=('bold', 13), justify=tk.LEFT)
        students_number_lb.place(x=20, y=170)

        for i in class_list:
            result = fetch_student_data(query=f"select count(*) from data where class ='{i}'")

            students_number_lb['text'] += f"{i} Class:  {result[0][0]}\n\n"

            print(i, result)

        home_page_fm.pack(fill=tk.BOTH, expand=True)

    def find_student_page():

        def fing_student():

            found_data = ''

            if find_by_option_btn.get() == 'Id':
                found_data = fetch_student_data(query=f"""
                select Id, Name, Class, Gender from data where Id = '{search_input.get()}'
                """)


            elif find_by_option_btn.get() == 'Name':
                found_data = fetch_student_data(query=f"""
                select Id, Name, Class, Gender from data where Name LIKE  '%{search_input.get()}%'
                """)


            elif find_by_option_btn.get() == 'Class':
                found_data = fetch_student_data(query=f"""
                           select Id, Name, Class, Gender from data where Class  = '{search_input.get()}'
                           """)


            elif find_by_option_btn.get() == 'Gender':
                found_data = fetch_student_data(query=f"""
                           select Id, Name, Class, Gender from data where Gender  = '{search_input.get()}'
                           """)

            if found_data:

                for item in record_table.get_children():
                    record_table.delete(item)

                for details in found_data:
                    record_table.insert(parent='', index='end', values=details)

            else:
                for item in record_table.get_children():
                    record_table.detach(item)

        def generate_student_card():

            selection = record_table.selection()
            selected_id = record_table.item(item=selection, option='values')[0]
            print(selected_id)

            get_student_details = fetch_student_data(f"""
                select Name, Age, Gender, Class, Phone_number, Email from data where Id = '{selected_id}'
                """)
            get_student_pic = fetch_student_data(f"""
                    select Image from data where Id = '{selected_id}'
                    """)
            student_pic = BytesIO(get_student_pic[0][0])

            student_details = f"""
{selected_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}
"""

            student_card_img_obj = draw_student_card(student_pic_path=student_pic,
                                                     student_data=student_details)
            student_card_page(student_card_obj=student_card_img_obj, bypass_login_page=True)

        def clear_result():

            find_by_option_btn.set('Id')
            search_input.delete(0, tk.END)

            for item in record_table.get_children():
                record_table.delete(item)

            generate_student_card_btn.config(state=tk.DISABLED)

        search_filters = ['Id', 'Name', 'Class', 'Gender']

        find_student_page_fm = tk.Frame(pages_fm)
        find_student_record_lb = tk.Label(find_student_page_fm, text='Find Student Record',
                                          font=('bold', 13), fg='white', bg=bg_color)
        find_student_record_lb.place(x=20, y=10, width=300)

        find_by_lb = tk.Label(find_student_page_fm, text='Find By:', font=('bold', 12))
        find_by_lb.place(x=12, y=50)

        find_by_option_btn = Combobox(find_student_page_fm, font=('bold', 12),
                                      state='readonly', values=search_filters)
        find_by_option_btn.place(x=80, y=50, width=80)
        find_by_option_btn.set('Id')

        search_input = tk.Entry(find_student_page_fm, font=('bold', 12))
        search_input.place(x=20, y=90)
        search_input.bind('<KeyRelease>', lambda e: fing_student())

        record_table_lb = tk.Label(find_student_page_fm, text='Record Table',
                                   font=('bold', 13), bg=bg_color, fg='white')
        record_table_lb.place(x=20, y=160, width=300)

        record_table = Treeview(find_student_page_fm)
        record_table.place(x=0, y=200, width=350)
        record_table.bind('<<TreeviewSelect>>',
                          lambda e: generate_student_card_btn.config(state=tk.NORMAL))

        record_table['columns'] = ('Id', 'Name', 'Class', 'Gender')

        record_table.column('#0', stretch=tk.NO, width=0)

        record_table.heading('Id', text='Id', anchor=tk.W)
        record_table.column('Id', width=50, anchor=tk.W)

        record_table.heading('Name', text='Name', anchor=tk.W)
        record_table.column('Name', width=90, anchor=tk.W)

        record_table.heading('Class', text='Class', anchor=tk.W)
        record_table.column('Class', width=40, anchor=tk.W)

        record_table.heading('Gender', text='Gender', anchor=tk.W)
        record_table.column('Gender', width=40, anchor=tk.W)

        generate_student_card_btn = tk.Button(find_student_page_fm, text='Generate Student Card',
                                              font=('bold', 13), bg=bg_color, fg='white', state=tk.DISABLED,
                                              command=generate_student_card)
        generate_student_card_btn.place(x=160, y=450)

        clear_btn = tk.Button(find_student_page_fm, text='Clear', font=('bold', 13),
                              bg=bg_color, fg='white', command=clear_result)
        clear_btn.place(x=10, y=450)

        find_student_page_fm.pack(fill=tk.BOTH, expand=True)

    def announcement_page():

        selected_classes = []

        def add_class(name):

            if selected_classes.count(name):
                selected_classes.remove(name)

            else:
                selected_classes.append(name)

            print(selected_classes)

        def collect_emails():

            fetched_emails = []

            for _class in selected_classes:

                emails = fetch_student_data(f" select email from data where class = '{_class}'")

                for email_address in emails:
                    fetched_emails.append(*email_address)

            thread = threading.Thread(target=send_announcement, args=[fetched_emails])
            thread.start()

        def send_announcement(email_addresses):

            box_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)

            heading_lb = tk.Label(box_fm, text='Sending Email', font=('bold', 15),
                                  bg=bg_color, fg='white')
            heading_lb.place(x=0, y=0, width=300)

            sending_lb = tk.Label(box_fm, font=('bold', 12), justify=tk.LEFT)
            sending_lb.pack(pady=50)

            box_fm.place(x=100, y=120, width=300, height=200)

            subject = announcement_subject.get()
            message = f"<h3 style = 'white-space: pre-wrap;'> {announcement_message.get('0.1', tk.END)}</h3>"
            sent_count = 0

            for email in email_addresses:
                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(email_addresses)}")
                sendmail_to_student(email=email, subject=subject, message=message)

                sent_count += 1
                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(email_addresses)}")

            box_fm.destroy()
            message_box(message="Announcement Sent\nSuccessfully")

        announcement_page_fm = tk.Frame(pages_fm)

        subject_lb = tk.Label(announcement_page_fm, text='Enter Announcement Subject.',
                              font=('bold', 12))
        subject_lb.place(x=10, y=10)
        announcement_subject = tk.Entry(announcement_page_fm, font=('bold', 12))
        announcement_subject.place(x=10, y=40, width=210, height=25)

        announcement_message = ScrolledText(announcement_page_fm, font=('bold', 12))
        announcement_message.place(x=10, y=100, width=300, height=200)

        classes_list_lb = tk.Label(announcement_page_fm, text='Select Classes to Announce',
                                   font=('bold', 12))
        classes_list_lb.place(x=10, y=320)

        y_position = 350

        for grade in class_list:
            class_check_btn = tk.Checkbutton(announcement_page_fm, text=f'Class {grade}',
                                             command=lambda grade=grade: add_class(name=grade))
            class_check_btn.place(x=10, y=y_position)
            y_position += 25

        send_announcement_btn = tk.Button(announcement_page_fm, text='Send Announcement',
                                          font=('bold', 12), bg=bg_color, fg='white', command=collect_emails)
        send_announcement_btn.place(x=180, y=520)

        announcement_page_fm.pack(fill=tk.BOTH, expand=True)

    pages_fm = tk.Frame(dashboard_fm)
    pages_fm.place(x=122, y=5, width=350, height=550)

    home_page()

    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.config(width=480, height=580)


def admin_login_page():
    def show_hide_password():

        if password_entry['show'] == '*':
            password_entry.config(show='')
            show_hide_btn.config(image=unlocked_icon)
        else:
            password_entry.config(show='*')
            show_hide_btn.config(image=locked_icon)

    def forward_welcome_page():

        admin_login_page_fm.destroy()
        root.update()
        welcome_page()

    def login_account():

        if username_entry.get() == 'admin':

            if password_entry.get() == 'admin':
                admin_login_page_fm.destroy()
                root.update()
                admin_dashboard()
            else:
                message_box(message='Wrong Password')
        else:

            message_box(message='Wrong Username')

    admin_login_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    admin_login_page_fm.place(x=0, y=0, width=400)

    heading_lb = tk.Label(admin_login_page_fm, text='Admin Login Page', font=('bold', 18), bg=bg_color, fg='white')
    heading_lb.place(x=0, y=0, width=400)

    admin_icon_lb = tk.Label(admin_login_page_fm, image=login_admin_icon, bd=0)
    admin_icon_lb.place(x=150, y=40)
    back_btn = tk.Button(admin_login_page_fm, text='←', font=('bold', 20), bd=0, fg=bg_color,
                         command=forward_welcome_page)
    back_btn.place(x=10, y=50)

    username_lb = tk.Label(admin_login_page_fm, text='Enter Admin Username', font=('bold', 15), fg=bg_color)
    username_lb.place(x=80, y=140)

    username_entry = tk.Entry(admin_login_page_fm, font=('bold', 15), fg=bg_color,
                              justify=tk.CENTER, highlightbackground='gray', highlightthickness=2)
    username_entry.place(x=80, y=190)

    password_lb = tk.Label(admin_login_page_fm, text='Enter Admin Password', font=('bold', 15), fg=bg_color)
    password_lb.place(x=80, y=240)

    password_entry = tk.Entry(admin_login_page_fm, font=('bold', 15), fg=bg_color,
                              justify=tk.CENTER, highlightbackground='gray', highlightthickness=2, show='*')
    password_entry.place(x=80, y=290)

    login_btn = tk.Button(admin_login_page_fm, text='Login', bg=bg_color, command=login_account,
                          font=('bold', 15), fg='white', activebackground=bg_color, activeforeground='white')
    login_btn.place(x=95, y=340, width=200, height=40)

    show_hide_btn = tk.Button(admin_login_page_fm, image=locked_icon, bd=0, command=show_hide_password)
    show_hide_btn.place(x=310, y=288)

    admin_login_page_fm.pack(pady=30)
    admin_login_page_fm.pack_propagate(False)
    admin_login_page_fm.config(width=400, height=430)


def add_acount_page():
    global student_id_ent

    pic_path = tk.StringVar()
    pic_path.set('')

    def open_pic():

        path = askopenfilename()
        if path:
            img = ImageTk.PhotoImage(Image.open(path).resize((100, 100)))
            pic_path.set(path)
            add_pic_btn.config(image=img)
            add_pic_btn.image = img

    def forward_to_welcome_page():
        ans = confirmation_box(message='Do You Want To Leave\nRegistration Form?')
        if ans:
            add_account_page_fm.destroy()
            root.update()
            welcome_page()

    def remove_highlight_warning(entry):

        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color, highlightbackground='gray')

    def check_invalid_email(email):

        pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
        match = re.match(pattern=pattern, string=email)
        return match

    def generate_id_number():

        generate_id = ''
        for r in range(6):
            generate_id += str(random.randint(0, 9))

        if not check_id_already_exists(Id=student_id_ent):

            student_id_ent.config(state=tk.NORMAL)
            student_id_ent.delete(0, tk.END)
            student_id_ent.insert(tk.END, generate_id)
            student_id_ent.config(state='readonly')

        else:
            generate_id_number()

    def check_input_validation():

        if student_name_ent.get() == '':
            student_name_ent.config(highlightcolor='red', highlightbackground='red')
            student_name_ent.focus()
            message_box(message='Student Full Name is Required')

        elif student_age_ent.get() == '':

            student_age_ent.config(highlightcolor='red', highlightbackground='red')
            student_age_ent.focus()
            message_box(message='Student Age is Required')

        elif student_contact_et.get() == '':

            student_contact_et.config(highlightcolor='red', highlightbackground='red')
            student_contact_et.focus()
            message_box(message='Student Contact is Required')

        elif select_student_class_btn.get() == '':

            select_student_class_btn.focus()
            message_box(message='Select Student Class is Required')

        elif student_email_ent.get() == '':

            student_email_ent.config(highlightcolor='red', highlightbackground='red')
            student_email_ent.focus()
            message_box(message='Student Email is Required')

        elif not check_invalid_email(email=student_email_ent.get().lower()):

            student_email_ent.config(highlightcolor='red', highlightbackground='red')
            student_email_ent.focus()
            message_box(message='Please Enter a Valid\nEmail Address')


        elif account_password_ent.get() == '':

            student_email_ent.config(highlightcolor='red', highlightbackground='red')
            student_email_ent.focus()
            message_box(message='Creating Password Required')
        else:

            pic_data = b''

            if pic_path.get() != '':
                ressize_pic = Image.open(pic_path.get()).resize((100, 100))
                ressize_pic.save('temp_pic.png')

                read_data = open('temp_pic.png', 'rb')
                pic_data = read_data.read()
                read_data.close()

            else:
                read_data = open('addstudent.png', 'rb')
                pic_data = read_data.read()
                read_data.close()
                pic_path.set('addstudent.png')

            con = pymysql.connect(host='localhost', user='root', password='root', database='studentpro')
            mycursor = con.cursor()

            query = 'insert into data values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
            mycursor.execute(query, (student_id_ent.get(), account_password_ent.get(), student_name_ent.get(),
                                     student_age_ent.get(), student_gender.get(),
                                     student_contact_et.get(), select_student_class_btn.get(),
                                     student_email_ent.get(), pic_data))
            con.commit()

            data = f"""
            {student_id_ent.get()}
            {student_name_ent.get()}
            {student_age_ent.get()}
            {student_gender.get()}
            {student_contact_et.get()}
            {select_student_class_btn.get()}
            {student_email_ent.get()}


            """

            get_student_card = draw_student_card(student_pic_path=pic_path.get(), student_data=data)
            student_card_page(student_card_obj=get_student_card)

            add_account_page_fm.destroy()
            root.update()
            message_box('Account Sucessful Created')

    add_account_page_fm = tk.Frame(root, highlightbackground=bg_color, highlightthickness=3)
    add_pic_section_fm = tk.Frame(add_account_page_fm, highlightbackground=bg_color, highlightthickness=2)
    add_pic_btn = tk.Button(add_pic_section_fm, image=add_student_icon, bd=0, command=open_pic)
    add_pic_btn.pack()
    add_pic_section_fm.place(x=5, y=5, width=105, height=105)

    student_name_lb = tk.Label(add_account_page_fm, text='Enter Student Full Name.', font=('bold', 12))
    student_name_lb.place(x=5, y=130)
    student_name_ent = tk.Entry(add_account_page_fm, font=('bold', 15),
                                highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
    student_name_ent.place(x=5, y=160, width=180)
    student_name_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_name_ent))

    student_gender_lb = tk.Label(add_account_page_fm, text='Select Student Gender.', font=('bold', 12))
    student_gender_lb.place(x=5, y=210)

    male_gender_btn = tk.Radiobutton(add_account_page_fm, text='Male', font=('bold', 12),
                                     variable=student_gender, value='male')
    male_gender_btn.place(x=25, y=235)

    female_gender_btn = tk.Radiobutton(add_account_page_fm, text='Female', font=('bold', 12),
                                       variable=student_gender, value='Female')
    female_gender_btn.place(x=95, y=235)
    student_gender.set('male')

    student_age_lb = tk.Label(add_account_page_fm, text='Enter Student Age.', font=('bold', 12))
    student_age_lb.place(x=5, y=275)

    student_age_ent = tk.Entry(add_account_page_fm, font=('bold', 15), highlightcolor=bg_color,
                               highlightbackground='gray', highlightthickness=2)
    student_age_ent.place(x=5, y=305, width=180)
    student_age_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_age_ent))

    student_contact_lb = tk.Label(add_account_page_fm, text='Enter Contact Phone Number.', font=('bold', 12))
    student_contact_lb.place(x=5, y=360)

    student_contact_et = tk.Entry(add_account_page_fm, font=('bold', 15),
                                  highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
    student_contact_et.place(x=5, y=390, width=180)
    student_contact_et.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_contact_et))

    student_class_lb = tk.Label(add_account_page_fm, text='Select Student Class.',
                                font=('bold', 12))
    student_class_lb.place(x=5, y=445)

    select_student_class_btn = Combobox(add_account_page_fm, font=('bold', 15), state='readonly', values=class_list)
    select_student_class_btn.place(x=5, y=475, width=180, height=30)

    student_id_lb = tk.Label(add_account_page_fm, text='Student ID Number.', font=('bold', 12))
    student_id_lb.place(x=240, y=35)

    student_id_ent = tk.Entry(add_account_page_fm, font=('bold', 18), bd=0)
    student_id_ent.place(x=380, y=35, width=80)

    student_id_ent.config(state='readonly')
    generate_id_number()

    id_info_lb = tk.Label(add_account_page_fm, text=""" Automatically Generated ID Number !
    Remember Using This ID Number
    Student will Login Account. """, justify=tk.LEFT)
    id_info_lb.place(x=240, y=65)

    student_email_lb = tk.Label(add_account_page_fm, text='Enter Student Email Address.', font=('bold', 12))
    student_email_lb.place(x=240, y=130)

    student_email_ent = tk.Entry(add_account_page_fm, font=('bold', 15),
                                 highlightcolor=bg_color, highlightbackground='gray', highlightthickness=2)
    student_email_ent.place(x=240, y=160, width=180)
    student_email_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=student_email_ent))

    email_info_lb = tk.Label(add_account_page_fm, text=""" Via Email Address Student
     Can Recover Account
     ! In Case Forgetting Password And Also
     Student will get Future Notifications. """, justify=tk.LEFT)
    email_info_lb.place(x=240, y=200)

    account_password_lb = tk.Label(add_account_page_fm, text='Create Account Password.',
                                   font=('bold', 12))
    account_password_lb.place(x=240, y=275)

    account_password_ent = tk.Entry(add_account_page_fm, font=('bold', 15),
                                    highlightcolor=bg_color, highlightbackground='gray',
                                    highlightthickness=2)
    account_password_ent.place(x=240, y=307, width=180)
    account_password_ent.bind('<KeyRelease>', lambda e: remove_highlight_warning(entry=account_password_ent))

    account_password_info_lb = tk.Label(add_account_page_fm, text=""" Via Student Created Password
    And Provided Student ID Number
    Student Can Login Account. """, justify=tk.LEFT)

    account_password_info_lb.place(x=240, y=345)

    home_btn = tk.Button(add_account_page_fm, text='Home', font=('bold', 15),
                         bg='red', fg='white', bd=0, activebackground='red',
                         activeforeground='white', command=forward_to_welcome_page)
    home_btn.place(x=240, y=420)

    submit_btn = tk.Button(add_account_page_fm, text='Submit', font=('bold', 15),
                           bg=bg_color, fg='white', bd=0, activebackground=bg_color,
                           activeforeground='white', command=check_input_validation)
    submit_btn.place(x=360, y=420)

    add_account_page_fm.pack(pady=30)

    add_account_page_fm.pack_propagate(False)
    add_account_page_fm.config(width=480, height=580)


# student_card_page()
# student_login_page()
# add_acount_page()
# draw_student_card()
# forgot_password_page()
# sendmail_to_student(email='ethiopiaselamle@gmail.com', message='<h1>Helow World</h1>',
#                     subject='Testing')

# student_dashboard(student_id=144759)
# admin_dashboard()
# admin_login_page()
welcome_page()

root.mainloop()
