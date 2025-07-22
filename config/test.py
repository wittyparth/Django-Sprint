import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('parthasaradhimunakala@gmail.com', 'ikdr lgsv daqn zyvv')
print("Login successful")
server.quit()